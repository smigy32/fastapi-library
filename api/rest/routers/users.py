from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.database import get_session
from api.dependencies import get_current_user
from api.models import UserModel
from api.rest.schemas import user
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
async def get_users(
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    users = await UserModel.return_all(session)
    return [u.to_dict() for u in users]


@router.get("/{user_id}", response_model=user.User)
@admin_required
async def get_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    db_user = await UserModel.get_by_id(session, user_id)
    if db_user:
        return db_user.to_dict()
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/", status_code=201)
@admin_required
@drop_cache("users")
async def create_user(
    user_data: user.UserCreate,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    try:
        new_user = UserModel(
            name=user_data.name,
            login=user_data.login,
            hashed_password=UserModel.generate_hash(user_data.password),
            email=user_data.email,
        )

        if user_data.email:
            try:
                send_welcome_email.delay(email_to=user_data.email, body={"name": user_data.name})
            except Exception as e:
                raise HTTPException(
                    status_code=500, detail="Failed to send welcome email. User creation rolled back."
                ) from e

        await new_user.save_to_db(session)
        return {"id": new_user.id}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to create user. Database access error."
        ) from e


@router.put("/{user_id}", response_model=user.User)
@admin_required
@drop_cache("users")
async def update_user(
    user_id: int,
    user_data: user.UserUpdate,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    db_user = await UserModel.get_by_id(session, user_id)

    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")

    if not any([user_data.name, user_data.login, user_data.password, user_data.email]):
        raise HTTPException(status_code=400, detail="Please provide valid information about the user")

    db_user.name = user_data.name or db_user.name
    db_user.login = user_data.login or db_user.login
    db_user.email = user_data.email or db_user.email
    db_user.hashed_password = UserModel.generate_hash(user_data.password) if user_data.password else db_user.hashed_password
    await db_user.save_to_db(session)

    return db_user.to_dict()


@router.delete("/{user_id}")
@admin_required
@drop_cache("users")
async def delete_user(
    user_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    status_code = await UserModel.delete_by_id(session, user_id)
    if status_code == 200:
        return {"detail": "User has been deleted"}
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="User not found")
