from fastapi import APIRouter, HTTPException, Depends

from api.dependencies import get_current_user
from api.models import BookModel, AuthorModel, UserModel
from api.schemas.book import Book, BookCreate, BookUpdate
from api.security import admin_required
from api.redis import cache_it


router = APIRouter(
    prefix="/books",
    tags=["books"],
)


@router.get("/", response_model=list[Book])  # get all books
@cache_it("books")
def get_books(title: str | None = None, current_user: UserModel = Depends(get_current_user)):

    # a simple filter by QUERY params
    if title:
        books = BookModel.get_by_title(title)
        return books

    books = BookModel.return_all()
    return [book.to_dict() for book in books]


@router.get("/{book_id}", response_model=Book)  # get a book by its id
def get_book(book_id: int, current_user: UserModel = Depends(get_current_user)):
    book = BookModel.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")

    return book.to_dict()


@router.post("/", status_code=201, response_model=Book)  # create a new book
@admin_required
def create_book(book_data: BookCreate, current_user: UserModel = Depends(get_current_user)):
    print(book_data)
    invalid_body_exception = HTTPException(
        status_code=400, detail="Please fill in all information about the book")

    if not book_data or not book_data.title:  # a post request mustn't be empty
        raise invalid_body_exception

    title, author_ids = book_data.title, book_data.author_ids
    description = book_data.description

    authors = AuthorModel.get_by_ids(
        author_ids) if book_data.author_ids else []
    new_book = BookModel(title=title, authors=authors, description=description)
    print(new_book.title)
    new_book.save_to_db()
    return new_book.to_dict()


@router.put("/{book_id}", response_model=Book)
@admin_required
def update_book(book_id: int, book_data: BookUpdate, current_user: UserModel = Depends(get_current_user)):
    book = BookModel.get_by_id(book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not book_data:  # request mustn't be empty
        raise HTTPException(
            status_code=400, detail="Please fill in some information about the book!")
    title = book_data.title or book.title
    author_ids = book_data.author_ids
    description = book_data.description or book.description

    authors = AuthorModel.get_by_ids(
        author_ids) if author_ids else book.authors

    book.title = title
    book.authors = authors
    book.description = description
    book.save_to_db()
    return book.to_dict()


@router.delete("/{book_id}")
@admin_required
def delete_book(book_id: int, current_user: UserModel = Depends(get_current_user)):
    status_code = BookModel.delete_by_id(book_id)
    if status_code == 200:
        return {"detail": "Book has been deleted"}
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="Book not found")
