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
    description = Column(String)

    @classmethod
    def return_all(cls):
        """
        Return a list of all active books.

        Returns:
            List[Book]: List of active books.
        """
        books = session.query(cls).filter_by(is_active=True).all()
        return books

    @classmethod
    def get_by_id(cls, book_id: int):
        """
        Get a book by ID.

        Args:
            book_id (int): The ID of the book to retrieve.

        Returns:
            Book: The book with the specified ID.
        """
        book = session.query(cls).filter_by(id=book_id, is_active=True).first()
        return book

    @classmethod
    def get_by_ids(cls, book_ids: list[int]):
        """
        Get books by a list of IDs.

        Args:
            book_ids (List[int]): The list of book IDs.

        Returns:
            List[Book]: List of books matching the provided IDs.
        """
        books = session.query(cls).filter(cls.id.in_(book_ids)).all()
        return books

    @classmethod
    def get_by_title(cls, title: str):
        """
        Get books by title.

        Args:
            title (str): The title of the books to retrieve.

        Returns:
            List[Book]: List of books with the specified title.
        """
        books = session.query(cls).filter(cls.title.like(
            f"%{title.capitalize()}%"), cls.is_active == True).all()
        return books

    @classmethod
    def delete_by_id(cls, book_id: int):
        """
        Delete a book by ID.

        Args:
            book_id (int): The ID of the book to delete.

        Returns:
            int: The status code indicating the success of the operation (200 if success, 404 if the book not found).
        """
        book = session.query(cls).filter_by(
            id=book_id, is_active=True).first()
        if book:
            book.is_active = False
            book.save_to_db()
            return 200
        else:
            return 404

    def save_to_db(self):
        """
        Save changes to the database.
        """
        session.add(self)
        session.commit()

    def to_dict(self):
        """
        Convert the book object to a dictionary.

        Returns:
            dict: Dictionary representation of the book object.
        """
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "authors": [{"id": author.id, "name": author.name} for author in self.authors]
        }
