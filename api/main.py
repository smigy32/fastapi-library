from fastapi import FastAPI
import uvicorn

from api.database.database import Base, engine


def setup_database(db_engine):
    Base.metadata.create_all(db_engine)


def create_app(db_engine):
    app = FastAPI()
    setup_database(db_engine)
    from api.routers import users, auth, books, authors
    app.include_router(users.router)
    app.include_router(auth.router)
    app.include_router(books.router)
    app.include_router(authors.router)
    return app


app = create_app(engine)


@app.get("/")
async def root():
    return "Hello World!"


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
