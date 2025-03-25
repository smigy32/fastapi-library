import strawberry


@strawberry.type
class Author:
    id: int
    name: str
