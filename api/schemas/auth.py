from pydantic import BaseModel


class Login(BaseModel):
    login: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str


class TokenData(BaseModel):
    login: str | None = None
