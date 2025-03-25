from fastapi import FastAPI
from strawberry.fastapi import GraphQLRouter
import uvicorn

from api.database.database import Base, engine
from api.graphql import schema


def setup_database(db_engine):
    Base.metadata.create_all(db_engine)


def setup_graphql(app: FastAPI):
    graphql_app = GraphQLRouter(schema)
    app.include_router(graphql_app, prefix="/graphql")


def create_app(db_engine):
    app = FastAPI()
    setup_database(db_engine)
    from api.rest.routers import users, auth, books, authors
    app.include_router(users.router)
    app.include_router(auth.router)
    app.include_router(books.router)
    app.include_router(authors.router)
    setup_graphql(app)
    return app


app = create_app(engine)


@app.get("/")
async def root():
    return "Hello World!"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
