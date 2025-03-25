import strawberry


@strawberry.type
class User:
    id: int
    name: str
    login: str
    email: str
    is_active: bool
    is_admin: bool
