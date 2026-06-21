from graphql import GraphQLError
import strawberry

from api.graphql.schemas.auth import Token
from api.graphql.schemas.users import User
from api.models.user import UserModel
from api.security import create_access_token, create_refresh_token
from api.tasks.tasks import send_welcome_email


@strawberry.type
class AuthMutation:
    @strawberry.mutation
    async def signup(self, info: strawberry.types.Info, name: str, login: str, password: str, email: str) -> User:
        session = info.context["session"]
        try:
            existing_user = await UserModel.get_by_login(session, login)
            if existing_user:
                raise GraphQLError("User already exists. Please Log in")

            new_user = UserModel(
                name=name,
                login=login,
                hashed_password=UserModel.generate_hash(password),
                email=email,
            )
            await new_user.save_to_db(session)

            if email:
                try:
                    send_welcome_email.delay(email_to=email, body={"name": name})
                except Exception as e:
                    await UserModel.delete_by_id(session, new_user.id)
                    raise GraphQLError("Failed to send welcome email. User registration rolled back.") from e

            return User(**new_user.to_dict())

        except GraphQLError:
            raise
        except Exception as e:
            raise GraphQLError("Failed to create user. Database access error.") from e

    @strawberry.mutation
    async def login(self, info: strawberry.types.Info, login: str, password: str) -> Token:
        session = info.context["session"]
        if not login or not password:
            raise GraphQLError("You have to provide both login and password")

        user = await UserModel.get_by_login(session, login)
        if not user:
            raise GraphQLError("Authentification failed! Check entered values")

        if UserModel.verify_hash(password, user.hashed_password):
            return Token(
                access_token=create_access_token(subject=user.login, user=user),
                refresh_token=create_refresh_token(subject=user.login, user=user),
            )
        raise GraphQLError("You've entered wrong password")
