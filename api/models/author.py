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
        authors = session.query(cls).filter_by(is_active=True).all()
        return authors

    @classmethod
    def get_by_id(cls, author_id: int):
        author = session.query(cls).filter_by(
            id=author_id, is_active=True).first()
        return author

    @classmethod
    def get_by_ids(cls, authors_ids: list[int]):
        authors = session.query(cls).filter(cls.id.in_(authors_ids)).all()
        return authors

    @classmethod
    def get_by_name(cls, name: str):
        authors = session.query(cls).filter_by(name=name, is_active=True).all()
        return authors

    @classmethod
    def delete_by_id(cls, author_id: int):
        author = session.query(cls).filter_by(
            id=author_id, is_active=True).first()
        if author:
            author.is_active = False
            return 200
        else:
            return 404

    def save_to_db(self):
        session.add(self)
        session.commit()
        
        
    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "books": [{"id": book.id, "title": book.title} for book in self.books]
        }
