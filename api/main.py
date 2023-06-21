from fastapi import FastAPI
import uvicorn

from api.database.database import Base, engine


def setup_database():
    print(Base.metadata)
    Base.metadata.create_all(engine)


def create_app():
    app = FastAPI()
    setup_database()
    from api.routers import users, auth
    app.include_router(users.router)
    app.include_router(auth.router)
    return app


app = create_app()


@app.get("/")
async def root():
    return "Hello World!"


if __name__ == "__main__":
    uvicorn.run(app)
