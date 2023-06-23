from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import Column, Integer, String, Boolean

from api.database.database import Base, session


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    login = Column(String(50), nullable=False, unique=True)
    hashed_password = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean(), default=False)

    def __repr__(self):
        return f"<UserModel(id={self.id}, name='{self.name}')>"

    @classmethod
    def return_all(cls):
        """
        Fetch all users from database
        Returns:
            list[User]: List of all users
        """
        users = session.query(cls).filter_by(is_active=True).all()
        return users

    @classmethod
    def get_by_id(cls, user_id: int):
        """
        Fetch a user by his id
        Args:
            user_id (int): User id 

        Returns:
            User: User with the specified ID
        """
        user = session.query(cls).filter_by(id=user_id, is_active=True).first()
        return user

    @classmethod
    def get_by_login(cls, login: str, to_dict=True):
        """
        Fetch a user by his login
        Args:
            login (str): Login of a user

        Returns:
            User: User with a certain login
        """
        user = session.query(cls).filter_by(
            login=login, is_active=True).first()
        return user

    def save_to_db(self):
        """
        Save changes to db
        """
        session.add(self)
        session.commit()

    @classmethod
    def delete_by_id(cls, user_id: int):
        """
        Delete a user by id.
        After deleting is_active attribute sets to False
        Args:
            user_id (int): User id 

        Returns:
            int: Status code
        """
        user = session.query(cls).filter_by(id=user_id, is_active=True).first()
        if user:
            user.is_active = False
            user.save_to_db()
            return 200
        else:
            return 404
        

    @staticmethod
    def generate_hash(password):
        """
        Hash a password via sha256 hash function
        :param password: Some reader's password
        :return: Hashed password
        """
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, password_hash):
        """
        Check if a password is valid
        :param password: Some reader's password
        :param password_hash: Hashed password from database
        :return: Bool value that shows if the password is valid
        """
        return sha256.verify(password, password_hash)
