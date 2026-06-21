from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.ext.asyncio import AsyncSession
import uvicorn

from api.database.database import Base, engine, get_session
from api.graphql import schema


@asynccontextmanager
async def lifespan(_: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


async def get_graphql_context(session: AsyncSession = Depends(get_session)):
    return {"session": session}


def create_app():
    app = FastAPI(lifespan=lifespan)

    from api.rest.routers import users, auth, books, authors
    app.include_router(users.router)
    app.include_router(auth.router)
    app.include_router(books.router)
    app.include_router(authors.router)

    graphql_app = GraphQLRouter(schema, context_getter=get_graphql_context)
    app.include_router(graphql_app, prefix="/graphql")

    return app


app = create_app()


@app.get("/")
async def root():
    return "Hello World!"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
