from pydantic import BaseModel


# Common fields for reading and creating
class UserBase(BaseModel):
    name: str
    login: str
    email: str | None = None


# Fields required only for creation
class UserCreate(UserBase):
    password: str


# Fields required only for the update
class UserUpdate(UserBase):
    name: str | None = None
    login: str | None = None
    password: str | None = None


# Readable fields (what will be returned to the user)
class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True
