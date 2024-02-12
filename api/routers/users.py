from fastapi import APIRouter, HTTPException, Depends

from api.dependencies import get_current_user
from api.models import UserModel
from api.schemas import user
from api.security import admin_required
from api.tasks.tasks import send_welcome_email
from api.redis import cache_it, drop_cache


router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get("/", response_model=list[user.User])
@admin_required
@cache_it("users")
def get_users(current_user: UserModel = Depends(get_current_user)):
    """
    Retrieve a list of users.

    Args:
        current_user (UserModel, optional): Current authenticated user. Defaults to Depends(get_current_user).

    Returns:
        List[User]: A list of User objects.
    """
    users = UserModel.return_all()
    return [user.to_dict() for user in users]


@router.get("/{user_id}", response_model=user.User)
@admin_required
def get_user(user_id: int, current_user: UserModel = Depends(get_current_user)):
    """
    Retrieve details of a specific user by ID.

    Args:
        user_id (int): The ID of the user.
        current_user (UserModel, optional): Current authenticated user. Defaults to Depends(get_current_user).

    Returns:
        User: Details of the user.
    """
    user = UserModel.get_by_id(user_id)
    if user:
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


@router.post("/", status_code=201)
@admin_required
@drop_cache("users")
def create_user(user_data: user.UserCreate, current_user: UserModel = Depends(get_current_user)):
    """
    Create a new user.

    Args:
        user_data (user.UserCreate): Data for creating a new user.
        current_user (UserModel, optional): Current authenticated user. Defaults to Depends(get_current_user).

    Returns:
        dict: A dictionary containing the ID of the newly created user.
    """
    new_user = UserModel(name=user_data.name, login=user_data.login,
                         hashed_password=UserModel.generate_hash(user_data.password))
    if user_data.email:
        new_user.email = user_data.email
        send_welcome_email.delay(email_to=user_data.email, body={"name": user_data.name})
    new_user.save_to_db()
    return {"id": new_user.id}


@router.put("/{user_id}", response_model=user.User)
@admin_required
@drop_cache("users")
def update_user(user_id: int, user_data: user.UserUpdate, current_user: UserModel = Depends(get_current_user)):
    """
    Update details of an existing user.

    Args:
        user_id (int): The ID of the user to be updated.
        user_data (user.UserUpdate): Data for updating the user.
        current_user (UserModel, optional): Current authenticated user. Defaults to Depends(get_current_user).

    Returns:
        User: Details of the updated user.
    """
    user = UserModel.get_by_id(user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any([user_data.name, user_data.login, user_data.password, user_data.email]):
        raise HTTPException(
            status_code=400, detail="Please provide valid information about the user")

    user.name = user_data.name or user.name
    user.login = user_data.login or user.login
    user.email = user_data.email or user.email
    user.hashed_password = UserModel.generate_hash(
        user_data.password) if user_data.password else user.hashed_password
    user.save_to_db()

    return user


@router.delete("/{user_id}")
@admin_required
@drop_cache("users")
def delete_user(user_id: int, current_user: UserModel = Depends(get_current_user)):
    """
    Delete a user by ID.

    Args:
        user_id (int): The ID of the user to be deleted.
        current_user (UserModel, optional): Current authenticated user. Defaults to Depends(get_current_user).

    Returns:
        dict: A dictionary with a detail message indicating the success or failure of the deletion.
    """
    status_code = UserModel.delete_by_id(user_id)
    if status_code == 200:
        return {"detail": "User has been deleted"}
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")
