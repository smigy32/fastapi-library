from sqlalchemy import Column, String, Integer, Boolean
from sqlalchemy.orm import relationship


from api.database.database import Base, session
from api.models.book import book_author_association


class AuthorModel(Base):
    __tablename__ = "authors"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    books = relationship(
        "BookModel", secondary=book_author_association, back_populates="authors")
    is_active = Column(Boolean, default=True)

    @classmethod
    def return_all(cls):
        """
        Return a list of all active authors.

        Returns:
            List[Author]: List of active authors.
        """
        authors = session.query(cls).filter_by(is_active=True).all()
        return authors

    @classmethod
    def get_by_id(cls, author_id: int):
        """
        Get an author by ID.

        Args:
            author_id (int): The ID of the author to retrieve.

        Returns:
            Author: The author with the specified ID.
        """
        author = session.query(cls).filter_by(
            id=author_id, is_active=True).first()
        return author

    @classmethod
    def get_by_ids(cls, authors_ids: list[int]):
        """
        Get authors by a list of IDs.

        Args:
            authors_ids (List[int]): The list of author IDs.

        Returns:
            List[Author]: List of authors matching the provided IDs.
        """
        authors = session.query(cls).filter(cls.id.in_(authors_ids)).all()
        return authors

    @classmethod
    def get_by_name(cls, name: str):
        """
        Get authors by name.

        Args:
            name (str): The name of the authors to retrieve.

        Returns:
            List[Author]: List of authors with the specified name.
        """
        authors = session.query(cls).filter_by(name=name, is_active=True).all()
        return authors

    @classmethod
    def delete_by_id(cls, author_id: int):
        """
        Delete an author by ID.

        Args:
            author_id (int): The ID of the author to delete.

        Returns:
            int: The status code indicating the success of the operation (200 if success, 404 if the author not found).
        """
        author = session.query(cls).filter_by(
            id=author_id, is_active=True).first()
        if author:
            author.is_active = False
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
        Convert the author object to a dictionary.

        Returns:
            dict: Dictionary representation of the author object.
        """
        return {
            "id": self.id,
            "name": self.name,
            "books": [{"id": book.id, "title": book.title} for book in self.books]
        }
