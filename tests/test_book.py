import pytest


def test_get_books(client, authentication_headers):
    """
    Test for getting all books
    """
    response = client.get("/books", headers=authentication_headers())
    assert response.status_code == 200


@pytest.mark.parametrize("title, description, author_ids, expected_status_code",
                         [("Test Book", "Description", [1], 201),
                          ("", "", [], 400),
                          ("", "Description", [1], 400),
                          ])
def test_create_book(client, authentication_headers, title, description, author_ids, expected_status_code):
    """
    Test for creating a book
    """
    response = client.post("/books", headers=authentication_headers(is_admin=True),
                           json={
                               "title": title,
                               "description": description,
                               "author_ids": author_ids,
    })
    assert response.status_code == expected_status_code


def test_get_book(client, authentication_headers):
    """
    Test for getting one book
    """
    response = client.get("/books/1", headers=authentication_headers())
    assert response.json() == {
        "title": "Test Book",
        "id": 1,
        "description": "Description",
        "authors": [{"id": 1, "name": "Updated Author"}]
    }


@pytest.mark.parametrize("id, title, expected_status_code",
                         [(1, "Updated Title", 200),
                          (1, "", 400),
                          (100, "Updated Title", 404)])
def test_update_book(client, authentication_headers, id, title, expected_status_code):
    """
    Test for updating a book
    """
    response = client.put(f"/books/{id}", headers=authentication_headers(is_admin=True),
                          json={
        "title": title,
    })
    assert response.status_code == expected_status_code


def test_delete_book(client, authentication_headers):
    """
    Test for deleting a book
    """
    response = client.delete("/books/1", headers=authentication_headers(is_admin=True))
    assert response.json()["detail"] == "Book has been deleted"
