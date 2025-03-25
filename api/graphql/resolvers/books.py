from typing import List
import strawberry

from api.graphql.schemas.books import Book
from api.models.book import BookModel


@strawberry.type
class BookQuery:
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
