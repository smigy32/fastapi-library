from typing import Annotated

from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.database import get_session
from api.models import UserModel
from api.rest.schemas import auth, user
from api.security import create_access_token, create_refresh_token
from api.tasks.tasks import send_welcome_email


router = APIRouter(
    tags=["auth"]
)


@router.post("/login", response_model=auth.Token)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_session),
):
    login = form_data.username
    password = form_data.password
    if not login or not password:
        raise HTTPException(status_code=400, detail="You have to provide both login and password")

    db_user = await UserModel.get_by_login(session, login)

    if not db_user:
        raise HTTPException(status_code=401, detail="Authentification failed! Check entered values")

    if UserModel.verify_hash(password, db_user.hashed_password):
        return {
            "access_token": create_access_token(subject=db_user.login, user=db_user),
            "refresh_token": create_refresh_token(subject=db_user.login, user=db_user),
        }
    else:
        raise HTTPException(status_code=401, detail="You've entered wrong password")


@router.post("/signup", status_code=201)
async def signup(
    user_data: user.UserCreate,
    session: AsyncSession = Depends(get_session),
):
    try:
        name, login = user_data.name, user_data.login
        password = user_data.password
        email = user_data.email

        existing_user = await UserModel.get_by_login(session, login)
        if existing_user:
            raise HTTPException(status_code=409, detail="User already exists. Please Log in")

        new_user = UserModel(
            name=name,
            login=login,
            hashed_password=UserModel.generate_hash(password),
            email=email,
        )
        await new_user.save_to_db(session)

        if email:
            try:
                send_welcome_email.delay(email_to=email, body={"name": name})
            except Exception as e:
                await UserModel.delete_by_id(session, new_user.id)
                raise HTTPException(
                    status_code=500, detail="Failed to send welcome email. User registration rolled back."
                ) from e

        return {"detail": "Successfully registered"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, detail="Failed to create user. Database access error."
        ) from e
