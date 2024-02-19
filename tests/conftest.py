import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database, drop_database

from api.models.user import UserModel
from api.database.database import session
from api import fastapi_config


@pytest.fixture(scope="session")
def client():
    SQLALCHEMY_DATABASE_URI = fastapi_config.TEST_SQLALCHEMY_DATABASE_URI
    # create connection to the test database
    engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)
    if not database_exists(engine.url):
        create_database(engine.url)
    session.bind = engine  # change the engine the session uses
    from api.main import create_app
    app = create_app(engine)
    yield TestClient(app)
    drop_database(engine.url)


@pytest.fixture
def authentication_headers(client):
    def _authentication_headers(is_admin=False):

        if is_admin:
            name = "Admin"
            login = "admin"
            password = "test"
            email = "admin@example.com"
        else:
            name = "User"
            login = "user"
            password = "test"
            email = "user@example.com"

        resp = _login(client, login, password)

        if resp.json().get("detail") == "Authentification failed! Check entered values":
            resp = client.post(
                "/signup",
                json={
                    "name": name,
                    "login": login,
                    "password": password,
                    "email": email,
                },
            )
            if resp.json()["detail"] == "Successfully registered":
                if is_admin:
                    user = UserModel.get_by_login(login, to_dict=False)
                    user.is_admin = True
                    user.save_to_db()
                resp = _login(client, login, password)
        headers = {"Authorization": f"Bearer {resp.json()['access_token']}"}

        return headers

    return _authentication_headers


def _login(client, login, password):
    return client.post(
        "/login",
        data={
            "username": login,
            "password": password,
        },
    )
