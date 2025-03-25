

from typing import List
import strawberry

from api.graphql.schemas.users import User
from api.models.user import UserModel


@strawberry.type
class UserQuery:
    @strawberry.field
    def users(self) -> List[User]:
        users = UserModel.return_all()
        return [User(**user.to_dict()) for user in users]
