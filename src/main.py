from fastapi import FastAPI

from src.views.tasks import router as tasks_router
from src.data.models import create_db_and_tables

app = FastAPI(title="Task Manager API")


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


app.include_router(tasks_router)


@app.get(
    "/",
    summary="API information and available endpoints",
    tags=["root"],
)
def read_root() -> dict:
    """
    Return basic API info and a map of available endpoints.
    """
    return {
        "api_name": app.title,
        "description": "A simple Task Management API built with FastAPI, Pydantic & SQLModel.",
        "endpoints": {
            "root": {"method": "GET", "path": "/"},
            "health_check": {"method": "GET", "path": "/health"},
            "list_tasks": {"method": "GET", "path": "/tasks"},
            "get_task": {"method": "GET", "path": "/tasks/{task_id}"},
            "create_task": {"method": "POST", "path": "/tasks"},
            "update_task": {"method": "PUT", "path": "/tasks/{task_id}"},
            "delete_task": {"method": "DELETE", "path": "/tasks/{task_id}"},
            "by_status": {"method": "GET", "path": "/tasks/status/{status}"},
            "by_priority": {"method": "GET", "path": "/tasks/priority/{priority}"},
            "docs": {"method": "GET", "path": "/docs"},
            "openapi": {"method": "GET", "path": "/openapi.json"},
        },
    }


@app.get("/health", summary="Health Check")
def health_check():
    return {"status": "ok"}
