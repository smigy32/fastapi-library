import strawberry


@strawberry.type
class Token:
    access_token: str
    refresh_token: str
