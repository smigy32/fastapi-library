from typing import List
import strawberry

from api.graphql.schemas.authors import Author
from api.models.author import AuthorModel


@strawberry.type
class AuthorQuery:
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
