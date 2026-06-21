from typing import List
import strawberry

from api.graphql.schemas.books import Book
from api.models.book import BookModel


@strawberry.type
class BookQuery:
    @strawberry.field
    async def books(self, info: strawberry.types.Info) -> List[Book]:
        session = info.context["session"]
        books = await BookModel.return_all(session)
        return [
            Book(
                id=book.id,
                title=book.title,
                description=book.description,
                authors=book.authors,
            )
            for book in books
        ]
