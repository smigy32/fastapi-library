from typing import List
import strawberry

from api.graphql.schemas.authors import Author
from api.models.author import AuthorModel


@strawberry.type
class AuthorQuery:
    @strawberry.field
    async def authors(self, info: strawberry.types.Info) -> List[Author]:
        session = info.context["session"]
        authors = await AuthorModel.return_all(session)
        return [
            Author(
                id=author.id,
                name=author.name,
            )
            for author in authors
        ]
