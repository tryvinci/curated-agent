# Curated Agent

This project is a FastAPI application that uses Redis as a message broker and Celery for asynchronous task processing.

## Key Technologies

- Python 3.11
- FastAPI
- Celery
- Redis
- Docker

## How to Run

The easiest way to get started is with Docker Compose:

```bash
docker-compose up -d
```

This will start the FastAPI application, a Redis instance, and a Celery worker.

The API will be available at `http://localhost:8000`.
