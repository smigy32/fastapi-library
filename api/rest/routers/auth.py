from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.models import UserModel
from api.rest.schemas import auth, user
from api.security import create_access_token, create_refresh_token
from api.tasks.tasks import send_welcome_email


router = APIRouter(
    tags=["auth"]
)


@router.post("/login", response_model=auth.Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    """
    Logs in a user and returns JWT tokens.

    Args:
        form_data (Annotated[OAuth2PasswordRequestForm, Depends()]): The user's login credentials.

    Raises:
        HTTPException: If the login or password is missing, or authentication fails.

    Returns:
        dict: A dictionary containing access_token and refresh_token.
    """
    login = form_data.username
    password = form_data.password
    if not login or not password:
        # returns 400 if any login or / and password is missing
        raise HTTPException(status_code=400, detail="You have to provide both login and password")

    user = UserModel.get_by_login(login)

    if not user:
        # returns 401 if user does not exist
        raise HTTPException(
            status_code=401, detail="Authentification failed! Check entered values")

    if UserModel.verify_hash(password, user.hashed_password):
        # generates the JWT Token
        return {
            "access_token": create_access_token(subject=user.login, user=user),
            "refresh_token": create_refresh_token(subject=user.login, user=user),
        }
    else:
        raise HTTPException(
            status_code=401, detail="You've entered wrong password")


@router.post("/signup", status_code=201)
def signup(user_data: user.UserCreate):
    """
    Signs up a new user.

    Args:
        user_data (user.UserCreate): User registration data.

    Raises:
        HTTPException: If the user already exists or if there are errors in sending mail or accessing the database.

    Returns:
        dict: A dictionary indicating successful registration.
    """
    try:
        # gets name, login and password
        name, login = user_data.name, user_data.login
        password = user_data.password
        email = user_data.email
        # checking for existing user
        existing_user = UserModel.get_by_login(login)
        if existing_user:
            # returns 409 if user already exists
            raise HTTPException(
                status_code=409, detail="User already exists. Please Log in")

        # database ORM object
        new_user = UserModel(
            name=name,
            login=login,
            hashed_password=UserModel.generate_hash(password),
            email=email,
        )
        # insert user
        new_user.save_to_db()

        if email:
            try:
                send_welcome_email.delay(email_to=email, body={"name": name})
            except Exception as e:
                # Handling errors in sending mail
                UserModel.delete_by_id(new_user.id)  # Rolling back the user creation
                raise HTTPException(
                    status_code=500, detail="Failed to send welcome email. User registration rolled back."
                ) from e

        return {"detail": "Successfully registered"}

    except Exception as e:
        # Handling errors related to database access
        raise HTTPException(
            status_code=500, detail="Failed to create user. Database access error."
        ) from e
