from datetime import datetime, timedelta
from functools import wraps

from fastapi import HTTPException, Depends
from jose import jwt

from api import fastapi_config
from api.dependencies import get_current_user
from api.models import UserModel


def create_access_token(subject: str, user: UserModel) -> str:
    expires_delta = datetime.utcnow(
    ) + timedelta(minutes=fastapi_config.ACCESS_TOKEN_EXPIRE_MINUTES)
    groups = ["admin", "user"] if user.is_admin else ["user"]
    to_encode = {"exp": expires_delta, "sub": subject, "groups": groups}
    encoded_jwt = jwt.encode(
        to_encode, fastapi_config.JWT_SECRET_KEY, fastapi_config.ALGORITHM)
    return encoded_jwt


def create_refresh_token(subject: str, user: UserModel) -> str:
    expires_delta = datetime.utcnow(
    ) + timedelta(minutes=fastapi_config.REFRESH_TOKEN_EXPIRE_MINUTES)
    groups = ["admin", "user"] if user.is_admin else ["user"]
    to_encode = {"exp": expires_delta, "sub": subject, "groups": groups}
    encoded_jwt = jwt.encode(
        to_encode, fastapi_config.JWT_REFRESH_SECRET_KEY, fastapi_config.ALGORITHM)
    return encoded_jwt

from fastapi import HTTPException, Depends


def admin_required(func):
    @wraps(func)
    def wrapper(*args, current_user: UserModel = Depends(get_current_user), **kwargs):
        if not current_user.is_admin:
            raise HTTPException(status_code=403, detail="Access forbidden")
        return func(*args, **kwargs)
    return wrapper

