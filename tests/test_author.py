import pytest


def test_get_authors(client, authentication_headers):
    """
    Test for getting all authors
    """
    response = client.get("/authors", headers=authentication_headers())
    assert response.status_code == 200


@pytest.mark.parametrize("name, expected_status_code",
                         [("Test Author", 201),
                          ("", 400),
                          (None, 422)])
def test_create_author(client, authentication_headers, name: str, expected_status_code: int):
    """
    Test for creating an author
    """
    response = client.post("/authors", headers=authentication_headers(is_admin=True), json={"name": name})
    assert response.status_code == expected_status_code


def test_get_author(client, authentication_headers):
    """
    Test for getting one author
    """
    response = client.get("/authors/1", headers=authentication_headers())
    assert response.json() == {
        "name": "Test Author",
        "id": 1,
        "books": []
    }


@pytest.mark.parametrize("id, name, expected_status_code",
                         [(1, "Updated Author", 200),
                             (1, "", 400),
                             (100, "Updated Author", 404)])
def test_update_author(client, authentication_headers, id, name, expected_status_code):
    """
    Test for updating an author
    """
    response = client.put(f"/authors/{id}", headers=authentication_headers(is_admin=True), json={"name": name})
    assert response.status_code == expected_status_code


@pytest.mark.parametrize("id, expected_message",
                         [(1, "Author has been deleted"),
                          (100, "Author not found")])
def test_delete_author(client, authentication_headers, id, expected_message):
    """
    Test for deleting an author
    """
    response = client.delete(f"/authors/{id}", headers=authentication_headers(is_admin=True))
    assert response.json()["detail"] == expected_message
