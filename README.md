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

## Contributing

Contributions to this project are welcome. If you find any issues or have suggestions for improvements, feel free to create a GitHub issue or submit a pull request.

When contributing, please adhere to the existing code style, follow best practices, and ensure that tests pass.
