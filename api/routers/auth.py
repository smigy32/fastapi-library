from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm

from api.models import UserModel
from api.schemas import auth, user
from api.security import create_access_token, create_refresh_token
from api.email_settings import send_email


router = APIRouter(
    tags=["auth"]
)


@router.post("/login", response_model=auth.Token)
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    login = form_data.username
    password = form_data.password
    if not login or not password:
        # returns 400 if any login or / and password is missing
        raise HTTPException(
            status_code=400, detail="You have to provide both login and password")

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

    # gets name, login and password
    name, login = user_data.name, user_data.login
    password = user_data.password
    email = user_data.email
    # checking for existing user
    user = UserModel.get_by_login(login)
    if not user:
        # database ORM object
        user = UserModel(
            name=name,
            login=login,
            hashed_password=UserModel.generate_hash(password),
            email=email,
        )
        # insert user
        user.save_to_db()

        if email:
            send_email(email_to=email, name=name)

        return {"detail": "Successfully registered"}
    else:
        # returns 409 if user already exists
        raise HTTPException(
            status_code=409, detail="User already exists. Please Log in")
