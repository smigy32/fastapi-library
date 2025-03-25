import strawberry

from api.graphql.resolvers.auth import AuthMutation
from api.graphql.resolvers.authors import AuthorQuery
from api.graphql.resolvers.books import BookQuery
from api.graphql.resolvers.users import UserQuery


@strawberry.type
class Mutation(AuthMutation):
    pass


@strawberry.type
class Query(UserQuery, AuthorQuery, BookQuery):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
