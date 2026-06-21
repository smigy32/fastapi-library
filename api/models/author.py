from sqlalchemy import Column, String, Integer, Boolean, select
from sqlalchemy.orm import relationship, selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.database import Base
from api.models.book import book_author_association


class AuthorModel(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    books = relationship("BookModel", secondary=book_author_association, back_populates="authors")
    is_active = Column(Boolean, default=True)

    @classmethod
    async def return_all(cls, session: AsyncSession):
        result = await session.execute(
            select(cls).where(cls.is_active == True).options(selectinload(cls.books))
        )
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, author_id: int):
        result = await session.execute(
            select(cls).where(cls.id == author_id, cls.is_active == True)
            .options(selectinload(cls.books))
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_ids(cls, session: AsyncSession, authors_ids: list[int]):
        result = await session.execute(
            select(cls).where(cls.id.in_(authors_ids)).options(selectinload(cls.books))
        )
        return result.scalars().all()

    @classmethod
    async def get_by_name(cls, session: AsyncSession, name: str):
        result = await session.execute(
            select(cls).where(cls.name == name, cls.is_active == True)
            .options(selectinload(cls.books))
        )
        return result.scalars().all()

    @classmethod
    async def delete_by_id(cls, session: AsyncSession, author_id: int):
        author = await cls.get_by_id(session, author_id)
        if author:
            author.is_active = False
            await author.save_to_db(session)
            return 200
        return 404

    async def save_to_db(self, session: AsyncSession):
        session.add(self)
        await session.commit()
        await session.refresh(self)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "books": [{"id": book.id, "title": book.title} for book in self.books]
        }
