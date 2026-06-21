from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.database import get_session
from api.dependencies import get_current_user
from api.models import BookModel, AuthorModel, UserModel
from api.rest.schemas.author import Author, AuthorCreate, AuthorUpdate
from api.security import admin_required
from api.redis import cache_it, drop_cache


router = APIRouter(
    prefix="/authors",
    tags=["authors"],
)


@router.get("/", response_model=list[Author])
@cache_it("authors")
async def get_authors(
    name: str | None = None,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if name:
        authors = await AuthorModel.get_by_name(session, name.capitalize())
        return [author.to_dict() for author in authors]
    authors = await AuthorModel.return_all(session)
    return [author.to_dict() for author in authors]


@router.get("/{author_id}", response_model=Author)
async def get_author(
    author_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    author = await AuthorModel.get_by_id(session, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    return author.to_dict()


@router.post("/", status_code=201, response_model=Author)
@admin_required
@drop_cache("authors")
async def create_author(
    author_data: AuthorCreate,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    if not author_data or not author_data.name:
        raise HTTPException(status_code=400, detail="Please fill in all information about the author")
    new_author = AuthorModel(name=author_data.name)
    await new_author.save_to_db(session)
    return (await AuthorModel.get_by_id(session, new_author.id)).to_dict()


@router.put("/{author_id}", response_model=Author)
@admin_required
@drop_cache("authors")
@drop_cache("books")
async def update_author(
    author_id: int,
    author_data: AuthorUpdate,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    author = await AuthorModel.get_by_id(session, author_id)
    if not author:
        raise HTTPException(status_code=404, detail="Author not found")
    if not author_data.name and not author_data.book_ids:
        raise HTTPException(status_code=400, detail="Please fill in some information about the author")

    author.name = author_data.name or author.name
    author.books = await BookModel.get_by_ids(session, author_data.book_ids) if author_data.book_ids else author.books
    await author.save_to_db(session)
    return (await AuthorModel.get_by_id(session, author.id)).to_dict()


@router.delete("/{author_id}")
@admin_required
@drop_cache("authors")
@drop_cache("books")
async def delete_author(
    author_id: int,
    current_user: UserModel = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
):
    status_code = await AuthorModel.delete_by_id(session, author_id)
    if status_code == 200:
        return {"detail": "Author has been deleted"}
    elif status_code == 404:
        raise HTTPException(status_code=404, detail="Author not found")
