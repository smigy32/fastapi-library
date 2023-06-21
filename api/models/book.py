from sqlalchemy import Table, Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship


from api.database.database import Base, session


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

    @classmethod
    def return_all(cls):
        books = session.query(cls).filter_by(is_active=True).all()
        return books

    @classmethod
    def get_by_id(cls, book_id: int):
        book = session.query(cls).filter_by(id=book_id, is_active=True).first()
        return book
    
    @classmethod
    def get_by_ids(cls, book_ids: list[int]):
        books = session.query(cls).filter(cls.id.in_(book_ids)).all()
        return books

    @classmethod
    def get_by_title(cls, title: str):
        books = session.query(cls).filter(cls.title.like(
            f"%{title.capitalize()}%"), cls.is_active == True).all()
        return books

    @classmethod
    def delete_by_id(cls, book_id: int):
        book = session.query(cls).filter_by(
            id=book_id, is_active=True).first()
        if book:
            book.is_active = False
            book.save_to_db()
            return 200
        else:
            return 404

    def save_to_db(self):
        session.add(self)
        session.commit()
        
        
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "authors": [{"id": author.id, "name": author.name} for author in self.authors]
        }
