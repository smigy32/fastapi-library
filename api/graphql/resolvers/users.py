from typing import List
import strawberry

from api.graphql.schemas.users import User
from api.models.user import UserModel


@strawberry.type
class UserQuery:
    @strawberry.field
    async def users(self, info: strawberry.types.Info) -> List[User]:
        session = info.context["session"]
        users = await UserModel.return_all(session)
        return [User(**user.to_dict()) for user in users]
