from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt

from api import fastapi_config
from api.models.user import User
from api.schemas import auth


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, fastapi_config.JWT_SECRET_KEY, algorithms=[
                             fastapi_config.ALGORITHM])
        login: str = payload.get("sub")
        if login is None:
            raise credentials_exception
        token_data = auth.TokenData(login=login)
    except JWTError:
        raise credentials_exception
    user = User.get_by_login(login=token_data.login)
    if user is None:
        raise credentials_exception
    return user
