from typing import List
import strawberry

from api.graphql.schemas.authors import Author


@strawberry.type
class Book:
    id: int
    title: str
    description: str
    authors: List[Author]
