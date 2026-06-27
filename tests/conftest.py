import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session as SyncSession
from sqlalchemy_utils import database_exists, create_database, drop_database

from api.database.database import Base, get_session
from api import fastapi_config
from tests.factories import AdminUserFactory, AuthorFactory, BookFactory, UserFactory


@pytest.fixture(scope="session")
def test_db():
    sync_url = fastapi_config.TEST_SQLALCHEMY_DATABASE_URI
    if not database_exists(sync_url):
        create_database(sync_url)
    engine = create_engine(sync_url)
    Base.metadata.create_all(engine)
    engine.dispose()
    yield sync_url
    drop_database(sync_url)


@pytest.fixture(scope="session")
def sync_engine(test_db):
    engine = create_engine(test_db)
    yield engine
    engine.dispose()


@pytest.fixture(scope="session")
def client(test_db):
    async_url = test_db.replace("postgresql://", "postgresql+asyncpg://")
    test_engine = create_async_engine(async_url, echo=False)
    TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_session():
        async with TestSessionLocal() as session:
            yield session

    from api.main import app
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    test_engine.sync_engine.dispose()

@pytest.fixture
def db_session(sync_engine):
    with SyncSession(sync_engine) as session:
        yield session


@pytest.fixture(autouse=True)
def configure_factories(db_session):
    """Wire every factory to the current test's sync session."""
    factories = (UserFactory, AdminUserFactory, AuthorFactory, BookFactory)
    for f in factories:
        f._meta.sqlalchemy_session = db_session
    yield
    for f in factories:
        f._meta.sqlalchemy_session = None

@pytest.fixture
def regular_user():
    return UserFactory()


@pytest.fixture
def admin_user():
    return AdminUserFactory()


@pytest.fixture
def user_headers(client, regular_user):
    resp = client.post("/login", data={"username": regular_user.login, "password": "password"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def admin_headers(client, admin_user):
    resp = client.post("/login", data={"username": admin_user.login, "password": "password"})
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture
def author():
    return AuthorFactory()


@pytest.fixture
def book(db_session, author):
    b = BookFactory()
    b.authors.append(author)
    db_session.commit()
    return b
