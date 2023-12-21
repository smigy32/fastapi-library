# FastAPI Library

This is a sample project called FastAPI Library. It showcases the implementation of a library management system using the FastAPI framework.

## Getting Started

To run the project, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/Smigy32/fastapi-library.git
```

2. Navigate to the project directory:

```bash
cd fastapi-library
```

3. Modify the environment variables:

   - Rename the `.env.example` file to `.env`.
   - Open the `.env` file and update the values with your database credentials.

4. Start the application using Docker Compose:

```bash
docker-compose up
```

5. Once the containers are up and running, open a new terminal or command prompt.

6. Enter the Docker container:

```bash
docker exec -it <api container id>  bash
```

7. Inside the container, run the database migrations:

```bash
alembic upgrade head
```

8. After the migrations are applied, you can start using the API.

9. Open your web browser and navigate to `http://localhost:8000/docs` to access the Swagger UI and explore the API endpoints.

## API Endpoints

The following endpoints are available in the API:

- `POST /signup`: User registration
- `POST /login`: User Login

- `GET /users`: Get a list of all users. <span style="color:yellow">*Admin only*</span>
- `GET /users/{user_id}`: Get details of a specific user by ID. <span style="color:yellow">*Admin only*</span>
- `POST /users`: Create a new user. <span style="color:yellow">*Admin only*</span>
- `PUT /users/{user_id}`: Update an existing user by ID. <span style="color:yellow">*Admin only*</span>
- `DELETE /users/{user_id}`: Delete a user by ID. <span style="color:yellow">*Admin only*</span>

- `GET /books`: Get a list of all books.
- `GET /books/{book_id}`: Get details of a specific book by ID.
- `POST /books`: Create a new book. <span style="color:yellow">*Admin only*</span>
- `PUT /books/{book_id}`: Update an existing book by ID. <span style="color:yellow">*Admin only*</span>
- `DELETE /books/{book_id}`: Delete a book by ID. <span style="color:yellow">*Admin only*</span>
- `GET /books/pdf/`: Get a PDF catalog of all books.

- `GET /authors`: Get a list of all authors. 
- `GET /authors/{author_id}`: Get details of a specific author by ID.
- `POST /authors`: Create a new author. <span style="color:yellow">*Admin only*</span>
- `PUT /authors/{author_id}`: Update an existing author by ID. <span style="color:yellow">*Admin only*</span>
- `DELETE /authors/{author_id}`: Delete an author by ID. <span style="color:yellow">*Admin only*</span>
