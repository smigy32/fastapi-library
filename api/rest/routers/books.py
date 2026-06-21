from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.database import get_session
from api.dependencies import get_current_user
from api.models import BookModel, AuthorModel, UserModel
from api.rest.schemas.book import Book, BookCreate, BookUpdate
from api.security import admin_required
from api.redis import cache_it, drop_cache
from api.tasks.tasks import generate_pdf
from api.email_settings import send_catalog


router = APIRouter(
    prefix="/books",
    tags=["books"],
)


@router.get("/", response_model=list[Book])
@cache_it("books")
async def get_books(
    title: str | None = None,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if title:
        books = await BookModel.get_by_title(session, title)
        return [book.to_dict() for book in books]
    books = await BookModel.return_all(session)
    return [book.to_dict() for book in books]


@router.get("/{book_id}", response_model=Book)
async def get_book(
    book_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    book = await BookModel.get_by_id(session, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    return book.to_dict()


@router.post("/", status_code=201, response_model=Book)
@admin_required
@drop_cache("books")
@drop_cache("authors")
async def create_book(
    book_data: BookCreate,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not book_data or not book_data.title:
        raise HTTPException(status_code=400, detail="Please fill in all information about the book")

    authors = await AuthorModel.get_by_ids(session, book_data.author_ids) if book_data.author_ids else []
    new_book = BookModel(title=book_data.title, authors=authors, description=book_data.description)
    await new_book.save_to_db(session)
    return (await BookModel.get_by_id(session, new_book.id)).to_dict()


@router.put("/{book_id}", response_model=Book)
@admin_required
@drop_cache("books")
@drop_cache("authors")
async def update_book(
    book_id: int,
    book_data: BookUpdate,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    book = await BookModel.get_by_id(session, book_id)
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    if not any([book_data.title, book_data.description, book_data.author_ids]):
        raise HTTPException(status_code=400, detail="Please fill in some information about the book!")

    book.title = book_data.title or book.title
    book.description = book_data.description or book.description
    book.authors = await AuthorModel.get_by_ids(session, book_data.author_ids) if book_data.author_ids else book.authors
    await book.save_to_db(session)
    return (await BookModel.get_by_id(session, book.id)).to_dict()


@router.delete("/{book_id}")
@admin_required
@drop_cache("books")
@drop_cache("authors")
async def delete_book(
    book_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    status_code = await BookModel.delete_by_id(session, book_id)
    if status_code == 200:
        return {"detail": "Book has been deleted"}
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="Book not found")


@router.get("/pdf/")
async def generate_catalog(
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    books = [book.to_dict() for book in await BookModel.return_all(session)]
    generate_pdf.delay(books, "books")
    await send_catalog(email_to=current_user.email, body={"name": current_user.name})
    return books
