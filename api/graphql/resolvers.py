from typing import List
import strawberry
from graphql import GraphQLError

from api.graphql.schemas import Author, Token, User, Book
from api.models.author import AuthorModel
from api.models.book import BookModel
from api.models.user import UserModel
from api.security import create_access_token, create_refresh_token
from api.tasks.tasks import send_welcome_email


@strawberry.type
class Mutation:
    @strawberry.mutation
    def signup(self, name: str, login: str, password: str, email: str) -> User:
        try:
            # checking for existing user
            existing_user = UserModel.get_by_login(login)
            if existing_user:
                raise GraphQLError("User already exists. Please Log in")

            # database ORM object
            new_user = UserModel(
                name=name,
                login=login,
                hashed_password=UserModel.generate_hash(password),
                email=email,
            )
            # insert user
            new_user.save_to_db()

            if email:
                try:
                    send_welcome_email.delay(email_to=email, body={"name": name})
                except Exception as e:
                    # Handling errors in sending mail
                    UserModel.delete_by_id(new_user.id)  # Rolling back the user creation
                    raise GraphQLError("Failed to send welcome email. User registration rolled back.") from e

            return User(**new_user.to_dict())

        except Exception as e:
            raise GraphQLError("Failed to create user. Database access error.") from e

    @strawberry.mutation
    def login(self, login: str, password: str) -> Token:
        if not login or not password:
            raise GraphQLError("You have to provide both login and password")

        user = UserModel.get_by_login(login)

        if not user:
            raise GraphQLError("Authentification failed! Check entered values")

        if UserModel.verify_hash(password, user.hashed_password):
            # generates the JWT Token
            return Token(
                access_token=create_access_token(subject=user.login, user=user),
                refresh_token=create_refresh_token(subject=user.login, user=user)
            )
        else:
            raise GraphQLError("You've entered wrong password")


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


schema = strawberry.Schema(query=Query, mutation=Mutation)
