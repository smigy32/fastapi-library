from typing import List
import strawberry


@strawberry.type
class User:
    id: int
    name: str
    login: str
    email: str
    is_active: bool
    is_admin: bool


@strawberry.type
class Author:
    id: int
    name: str


@strawberry.type
class Book:
    id: int
    title: str
    description: str
    authors: List[Author]
