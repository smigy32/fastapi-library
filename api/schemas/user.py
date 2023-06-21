from pydantic import BaseModel

# Спільні поля для читання та створення
class UserBase(BaseModel):
    name: str
    login: str

# Поля, потрібні лише для створення 
class UserCreate(UserBase):
    password: str
    
# Поля, потрібні лише для апдейту
class UserUpdate(BaseModel):
    name: str | None
    login: str | None
    password: str | None

# Поля для читання (те, що повертатиметься юзеру)
class User(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    class Config:
        orm_mode = True
