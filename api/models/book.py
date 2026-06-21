from sqlalchemy import Table, Column, String, Integer, ForeignKey, Boolean, select
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.database import Base


book_author_association = Table(
    "book_author_association",
    Base.metadata,
    Column("book_id", Integer, ForeignKey("books.id")),
    Column("author_id", Integer, ForeignKey("authors.id"))
)


class BookModel(Base):
    __tablename__ = "books"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    authors = relationship(
        "AuthorModel", secondary=book_author_association, back_populates="books")
    is_active = Column(Boolean, default=True)
    description = Column(String)

    @classmethod
    async def return_all(cls, session: AsyncSession):
        result = await session.execute(
            select(cls).where(cls.is_active == True).options(selectinload(cls.authors))
        )
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, book_id: int):
        result = await session.execute(
            select(cls).where(cls.id == book_id, cls.is_active == True)
            .options(selectinload(cls.authors))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_ids(cls, session: AsyncSession, book_ids: list[int]):
        result = await session.execute(
            select(cls).where(cls.id.in_(book_ids)).options(selectinload(cls.authors))
        )
        return result.scalars().all()

    @classmethod
    async def get_by_title(cls, session: AsyncSession, title: str):
        result = await session.execute(
            select(cls).where(cls.title.like(f"%{title.capitalize()}%"), cls.is_active == True)
            .options(selectinload(cls.authors))
        )
        return result.scalars().all()

    @classmethod
    async def delete_by_id(cls, session: AsyncSession, book_id: int):
        book = await cls.get_by_id(session, book_id)
        if book:
            book.is_active = False
            await book.save_to_db(session)
            return 200
        return 404

    async def save_to_db(self, session: AsyncSession):
        session.add(self)
        await session.commit()
        await session.refresh(self)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "authors": [{"id": author.id, "name": author.name} for author in self.authors]
        }
