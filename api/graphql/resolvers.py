from typing import List
import strawberry

from api.graphql.schemas import Author, User, Book
from api.models.author import AuthorModel
from api.models.book import BookModel
from api.models.user import UserModel


@strawberry.type
class Query:
    @strawberry.field
    def users(self) -> List[User]:
        users = UserModel.return_all()
        return [User(**user.to_dict()) for user in users]

    @strawberry.field
    def authors(self) -> List[Author]:
        authors = AuthorModel.return_all()
        return [
            Author(
                id=author.id,
                name=author.name,
            )
            for author in authors
        ]

    @strawberry.field
    def books(self) -> List[Book]:
        books = BookModel.return_all()
        return [
            Book(
                id=book.id,
                title=book.title,
                description=book.description,
                authors=book.authors,
            )
            for book in books
        ]


schema = strawberry.Schema(query=Query)
