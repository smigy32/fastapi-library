from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from api import fastapi_config
from api.database.database import get_session
from api.models.user import UserModel
from api.rest.schemas import auth


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    session: AsyncSession = Depends(get_session),
):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, fastapi_config.JWT_SECRET_KEY, algorithms=[fastapi_config.ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_data = auth.TokenData(login=login)
    except JWTError:
        raise credentials_exception
    user = await UserModel.get_by_login(session, login=token_data.login)
    if user is None:
        raise credentials_exception
    return user
