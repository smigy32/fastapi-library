import pytest


def test_get_users(client, authentication_headers):
    """
    Test for getting all users
    """
    response = client.get("/users", headers=authentication_headers(is_admin=True))
    assert response.status_code == 200


def test_create_user(client, authentication_headers):
    """
    Test for creating a user
    """
    response = client.post("/users", headers=authentication_headers(is_admin=True),
                           json={
                               "name": "Test User",
                               "login": "test",
                               "email": "test@example.com",
                               "password": "test",
    })
    assert response.status_code == 201


def test_get_user(client, authentication_headers):
    """
    Test for getting a user
    """
    response = client.get("/users/1", headers=authentication_headers(is_admin=True))
    assert response.status_code == 200


@pytest.mark.parametrize("id, name, expected_status_code",
                         [(3, "Updated User", 200),
                          (3, "", 400),
                          (100, "Updated User", 404)])
def test_update_user(client, authentication_headers, id, name, expected_status_code):
    """
    Test for updating a user
    """
    response = client.put(f"/users/{id}", headers=authentication_headers(is_admin=True),
                          json={
        "name": name,
    })
    assert response.status_code == expected_status_code


@pytest.mark.parametrize("id, expected_message",
                         [(3, "User has been deleted"),
                          (100, "User not found")])
def test_delete_user(client, authentication_headers, id, expected_message):
    """
    Test for deleting a user
    """
    response = client.delete(f"/users/{id}", headers=authentication_headers(is_admin=True))
    assert response.json()["detail"] == expected_message
