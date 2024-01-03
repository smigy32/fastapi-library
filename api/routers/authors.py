from fastapi import APIRouter, HTTPException, Depends

from api.dependencies import get_current_user
from api.models import BookModel, AuthorModel, UserModel
from api.schemas.author import Author, AuthorCreate, AuthorUpdate
from api.security import admin_required
from api.redis import cache_it


router = APIRouter(
    prefix="/authors",
    tags=["authors"],
)


@router.get("/", response_model=list[Author])
@cache_it("authors")
def get_authors(name: str | None = None, current_user: UserModel = Depends(get_current_user)):
    # a simple filter by last_name QUERY param
    if name:
        authors = AuthorModel.get_by_name(name.capitalize())
        return authors
    authors = AuthorModel.return_all()
    return [author.to_dict() for author in authors]


@router.get("/{author_id}", response_model=Author)
def get_author(author_id: int, current_user: UserModel = Depends(get_current_user)):
    author = AuthorModel.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")

    return author.to_dict()


@router.post("/", status_code=201, response_model=Author)
@admin_required
def create_author(author_data: AuthorCreate, current_user: UserModel = Depends(get_current_user)):
    if not author_data or not author_data.name:  # a post request mustn't be empty
        raise HTTPException(
            status_code=400, detail="Please fill in all information about the author")
    new_author = AuthorModel(name=author_data.name)
    new_author.save_to_db()
    return new_author.to_dict()


@router.put("/{author_id}", response_model=Author)
@admin_required
def update_author(author_id: int, author_data: AuthorUpdate, current_user: UserModel = Depends(get_current_user)):
    author = AuthorModel.get_by_id(author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if not author_data.name and not author_data.book_ids:  # a put request mustn't be empty
        raise HTTPException(
            status_code=400, detail="Please fill in some information about the author")

    name = author_data.name or author.name
    book_ids = author_data.book_ids

    books = BookModel.get_by_ids(
        book_ids) if book_ids else author.books
    author.books = books
    author.name = name
    author.save_to_db()
    return author.to_dict()


@router.delete("/{author_id}")
@admin_required
def delete_author(author_id: int, current_user: UserModel = Depends(get_current_user)):
    status_code = AuthorModel.delete_by_id(author_id)
    if status_code == 200:
        return {"detail": "Author has been deleted"}
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="Author not found")
