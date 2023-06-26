from pydantic import BaseModel


class AuthorBase(BaseModel):
    name: str


class AuthorCreate(AuthorBase):
    book_ids: list[int] | None = None


class AuthorUpdate(AuthorBase):
    name: str | None = None


class Author(AuthorBase):
    id: int
    books: list[dict]

    class Config:
        orm_mode = True
