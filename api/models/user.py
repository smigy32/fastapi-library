from passlib.hash import pbkdf2_sha256 as sha256
from sqlalchemy import Column, Integer, String, Boolean, select
from sqlalchemy.ext.asyncio import AsyncSession

from api.database.database import Base


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    login = Column(String(50), nullable=False, unique=True)
    hashed_password = Column(String(150), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean(), default=False)
    email = Column(String(), unique=True)

    def __repr__(self):
        return f"<UserModel(id={self.id}, name='{self.name}')>"

    @classmethod
    async def return_all(cls, session: AsyncSession):
        result = await session.execute(select(cls).where(cls.is_active == True))
        return result.scalars().all()

    @classmethod
    async def get_by_id(cls, session: AsyncSession, user_id: int):
        result = await session.execute(
            select(cls).where(cls.id == user_id, cls.is_active == True)
        )
        return result.scalar_one_or_none()

    @classmethod
    async def get_by_login(cls, session: AsyncSession, login: str):
        result = await session.execute(
            select(cls).where(cls.login == login, cls.is_active == True)
        )
        return result.scalar_one_or_none()

    async def save_to_db(self, session: AsyncSession):
        session.add(self)
        await session.commit()
        await session.refresh(self)

    @classmethod
    async def delete_by_id(cls, session: AsyncSession, user_id: int):
        user = await cls.get_by_id(session, user_id)
        if user:
            user.is_active = False
            await user.save_to_db(session)
            return 200
        return 404

    @staticmethod
    def generate_hash(password):
        return sha256.hash(password)

    @staticmethod
    def verify_hash(password, password_hash):
        return sha256.verify(password, password_hash)

    def to_dict(self):
        return {
            "id": self.id,
            "login": self.login,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active,
            "is_admin": self.is_admin,
        }
