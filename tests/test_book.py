import pytest


def test_get_books(client, user_headers):
    response = client.get("/books", headers=user_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_create_book(client, admin_headers, author):
    response = client.post("/books", headers=admin_headers, json={
        "title": "New Book",
        "description": "A description",
        "author_ids": [author.id],
    })
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "New Book"
    assert any(a["id"] == author.id for a in data["authors"])


@pytest.mark.parametrize("payload, expected_status", [
    ({"title": "", "description": "desc", "author_ids": []}, 400),
    ({"title": "", "description": "", "author_ids": []}, 400),
])
def test_create_book_invalid(client, admin_headers, payload, expected_status):
    response = client.post("/books", headers=admin_headers, json=payload)
    assert response.status_code == expected_status


def test_get_book(client, user_headers, book, author):
    response = client.get(f"/books/{book.id}", headers=user_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == book.id
    assert data["title"] == book.title
    assert data["description"] == book.description
    assert any(a["id"] == author.id for a in data["authors"])


def test_get_book_not_found(client, user_headers):
    response = client.get("/books/99999", headers=user_headers)
    assert response.status_code == 404


def test_update_book(client, admin_headers, book):
    response = client.put(f"/books/{book.id}", headers=admin_headers, json={"title": "Updated Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "Updated Title"


def test_update_book_empty_fields(client, admin_headers, book):
    response = client.put(f"/books/{book.id}", headers=admin_headers, json={"title": ""})
    assert response.status_code == 400


def test_update_book_not_found(client, admin_headers):
    response = client.put("/books/99999", headers=admin_headers, json={"title": "Ghost"})
    assert response.status_code == 404


def test_delete_book(client, admin_headers, book):
    response = client.delete(f"/books/{book.id}", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["detail"] == "Book has been deleted"


def test_delete_book_not_found(client, admin_headers):
    response = client.delete("/books/99999", headers=admin_headers)
    assert response.status_code == 404
