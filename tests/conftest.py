import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session as SyncSession
from sqlalchemy_utils import database_exists, create_database, drop_database

from api.database.database import Base, get_session
from api.models.user import UserModel
from api import fastapi_config


_TestSessionLocal = None
_sync_url = None


@pytest.fixture(scope="session")
def client():
    global _TestSessionLocal, _sync_url

    _sync_url = fastapi_config.TEST_SQLALCHEMY_DATABASE_URI
    async_url = _sync_url.replace("postgresql://", "postgresql+asyncpg://")

    if not database_exists(_sync_url):
        create_database(_sync_url)

    sync_engine = create_engine(_sync_url)
    Base.metadata.create_all(sync_engine)
    sync_engine.dispose()

    test_engine = create_async_engine(async_url, echo=True)
    _TestSessionLocal = async_sessionmaker(test_engine, expire_on_commit=False)

    async def override_get_session():
        async with _TestSessionLocal() as session:
            yield session

    from api.main import app
    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app) as c:
        yield c

    app.dependency_overrides.clear()
    test_engine.sync_engine.dispose()
    drop_database(_sync_url)


@pytest.fixture
def authentication_headers(client):
    def _authentication_headers(is_admin=False):
        if is_admin:
            name, login, password, email = "Admin", "admin", "test", "admin@example.com"
        else:
            name, login, password, email = "User", "user", "test", "user@example.com"

        resp = _login(client, login, password)

        if resp.json().get("detail") == "Authentification failed! Check entered values":
            resp = client.post(
                "/signup",
                json={"name": name, "login": login, "password": password, "email": email},
            )
            if resp.json()["detail"] == "Successfully registered":
                if is_admin:
                    _make_admin(login)
                resp = _login(client, login, password)

        return {"Authorization": f"Bearer {resp.json()['access_token']}"}

    return _authentication_headers


def _make_admin(login: str):
    sync_engine = create_engine(_sync_url)
    with SyncSession(sync_engine) as session:
        user = session.execute(
            select(UserModel).where(UserModel.login == login)
        ).scalar_one_or_none()
        if user:
            user.is_admin = True
            session.commit()
    sync_engine.dispose()


def _login(client, login, password):
    return client.post("/login", data={"username": login, "password": password})
