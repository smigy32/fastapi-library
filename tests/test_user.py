import pytest


def test_get_users(client, admin_headers):
    response = client.get("/users", headers=admin_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_user(client, admin_headers):
    response = client.post("/users", headers=admin_headers, json={
        "name": "New User",
        "login": "new_user_unique",
        "password": "secret",
    })
    assert response.status_code == 201
    assert "id" in response.json()


def test_get_user(client, admin_headers, regular_user):
    response = client.get(f"/users/{regular_user.id}", headers=admin_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == regular_user.id
    assert data["login"] == regular_user.login


def test_get_user_not_found(client, admin_headers):
    response = client.get("/users/99999", headers=admin_headers)
    assert response.status_code == 404


@pytest.mark.parametrize("payload, expected_status", [
    ({"name": "Updated"}, 200),
    ({"name": ""}, 400),
])
def test_update_user(client, admin_headers, regular_user, payload, expected_status):
    response = client.put(f"/users/{regular_user.id}", headers=admin_headers, json=payload)
    assert response.status_code == expected_status


def test_update_user_not_found(client, admin_headers):
    response = client.put("/users/99999", headers=admin_headers, json={"name": "Ghost"})
    assert response.status_code == 404


def test_delete_user(client, admin_headers, regular_user):
    response = client.delete(f"/users/{regular_user.id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "User has been deleted"


def test_delete_user_not_found(client, admin_headers):
    response = client.delete("/users/99999", headers=admin_headers)
    assert response.json()["detail"] == "User not found"
