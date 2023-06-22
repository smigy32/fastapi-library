FROM python:3.10

WORKDIR /fastapi-library

COPY . /fastapi-library

RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["uvicorn", "--host", "0.0.0.0", "--port", "8000", "api.main:app", "--reload"]
