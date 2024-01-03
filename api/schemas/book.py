from pydantic import BaseModel


class BookBase(BaseModel):
    title: str
    description: str | None = None


class BookCreate(BookBase):
    author_ids: list[int] | None = None


class BookUpdate(BookBase):
    title: str | None = None
    author_ids: list[int] | None = None


class Book(BookBase):
    id: int
    authors: list[dict]

    class Config:
        orm_mode = True
