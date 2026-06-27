import factory
from factory.alchemy import SQLAlchemyModelFactory

from api.models.author import AuthorModel
from api.models.book import BookModel
from api.models.user import UserModel


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = UserModel
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"User {n}")
    login = factory.Sequence(lambda n: f"user_{n}")
    email = factory.LazyAttribute(lambda o: f"{o.login}@example.com")
    hashed_password = factory.LazyFunction(lambda: UserModel.generate_hash("password"))
    is_active = True
    is_admin = False


class AdminUserFactory(UserFactory):
    name = factory.Sequence(lambda n: f"Admin {n}")
    login = factory.Sequence(lambda n: f"admin_{n}")
    is_admin = True


class AuthorFactory(SQLAlchemyModelFactory):
    class Meta:
        model = AuthorModel
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    name = factory.Sequence(lambda n: f"Author {n}")
    is_active = True


class BookFactory(SQLAlchemyModelFactory):
    class Meta:
        model = BookModel
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    title = factory.Sequence(lambda n: f"Book {n}")
    description = factory.Sequence(lambda n: f"Description {n}")
    is_active = True
