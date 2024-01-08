from pydantic import BaseModel


# Спільні поля для читання та створення
class UserBase(BaseModel):
    name: str
    login: str
    email: str | None = None


# Поля, потрібні лише для створення
class UserCreate(UserBase):
    password: str


# Поля, потрібні лише для апдейту
class UserUpdate(UserBase):
    name: str | None = None
    login: str | None = None
    password: str | None = None


# Поля для читання (те, що повертатиметься юзеру)
class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True
