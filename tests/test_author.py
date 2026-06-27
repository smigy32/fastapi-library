import pytest


def test_get_authors(client, user_headers):
    response = client.get("/authors", headers=user_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.parametrize("name, expected_status", [
    ("Valid Author", 201),
    ("", 400),
    (None, 422),
])
def test_create_author(client, admin_headers, name, expected_status):
    response = client.post("/authors", headers=admin_headers, json={"name": name})
    assert response.status_code == expected_status


def test_create_author_returns_correct_data(client, admin_headers):
    response = client.post("/authors", headers=admin_headers, json={"name": "Specific Author"})
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Specific Author"
    assert "id" in data
    assert data["books"] == []


def test_get_author(client, user_headers, author):
    response = client.get(f"/authors/{author.id}", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == author.id
    assert data["name"] == author.name


def test_get_author_not_found(client, user_headers):
    response = client.get("/authors/99999", headers=user_headers)
    assert response.status_code == 404


@pytest.mark.parametrize("name, expected_status", [
    ("Updated Name", 200),
    ("", 400),
])
def test_update_author(client, admin_headers, author, name, expected_status):
    response = client.put(f"/authors/{author.id}", headers=admin_headers, json={"name": name})
    assert response.status_code == expected_status


def test_update_author_not_found(client, admin_headers):
    response = client.put("/authors/99999", headers=admin_headers, json={"name": "Ghost"})
    assert response.status_code == 404


def test_delete_author(client, admin_headers, author):
    response = client.delete(f"/authors/{author.id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Author has been deleted"


def test_delete_author_not_found(client, admin_headers):
    response = client.delete("/authors/99999", headers=admin_headers)
    assert response.json()["detail"] == "Author not found"
