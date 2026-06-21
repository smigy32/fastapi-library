from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from api import fastapi_config

db_url = fastapi_config.SQLALCHEMY_DATABASE_URI.replace("postgresql://", "postgresql+asyncpg://")
engine = create_async_engine(db_url, echo=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()


async def get_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
