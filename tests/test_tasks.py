import os
import sys
from datetime import datetime, timezone, timedelta

from sqlmodel import Session, select

# Ensure the root of the project is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from src.main import app
from src.data.models import engine, Task

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    json = response.json()
    assert json["api_name"] == "Task Manager API"
    assert "endpoints" in json


def test_create_task_success():
    due = (datetime.now(timezone.utc) + timedelta(days=1)).isoformat()
    payload = {
        "title": "  My Task  ",
        "description": "Test description",
        "priority": "high",
        "due_date": due,
        "assigned_to": "Alice"
    }
    response = client.post("/tasks/", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "My Task"
    assert data["status"] == "pending"
    assert data["priority"] == "high"
    assert data["assigned_to"] == "Alice"
    # Confirms the stored due_date string begins with the same year–month–day you calculated.
    assert data["due_date"].startswith(due[:10])


def test_create_task_empty_title():
    response = client.post("/tasks/", json={"title": "   "})
    assert response.status_code == 422
    assert "Title must not be empty" in response.text


def test_create_task_past_due_date():
    past = (datetime.now(timezone.utc) - timedelta(days=1)).isoformat()
    response = client.post("/tasks/", json={"title": "T", "due_date": past})
    assert response.status_code == 422
    assert "Due date must be in the future" in response.text


def test_get_nonexistent_task():
    response = client.get("/tasks/999")
    assert response.status_code == 404
    assert response.json() == {"detail": "Task not found"}


def test_list_pagination_and_filters():
    r1 = client.get("/tasks/")
    assert len(r1.json()) == 10
    r2 = client.get("/tasks/?skip=1&limit=1")
    assert r2.status_code == 200
    assert len(r2.json()) == 1
    r3 = client.get("/tasks/?priority=medium")
    assert all(t["priority"] == "medium" for t in r3.json())


def test_update_task_and_not_found_task():
    r = client.post("/tasks/", json={"title": "Orig"})
    tid = r.json()["id"]
    upd = {"title": "Updated", "status": "completed"}

    r2 = client.put(f"/tasks/{tid}", json=upd)
    assert r2.status_code == 200
    assert r2.json()["title"] == "Updated"
    assert r2.json()["status"] == "completed"

    r3 = client.put("/tasks/9999", json=upd)
    assert r3.status_code == 404


def test_delete_task_and_not_found_task_to_delete():
    # create new task
    r = client.post("/tasks/", json={"title": "ToDelete"})
    tid = r.json()["id"]

    r2 = client.delete(f"/tasks/{tid}")
    assert r2.status_code == 204

    r3 = client.get(f"/tasks/{tid}")
    assert r3.status_code == 404

    r4 = client.delete("/tasks/9999")
    assert r4.status_code == 404


def test_tasks_by_status_and_priority_endpoints():
    with Session(engine) as session:
        completed_tasks = session.exec(select(Task).where(Task.status == "completed")).all()
        medium_tasks = session.exec(select(Task).where(Task.priority == "medium")).all()

    r_status = client.get("/tasks/status/completed")
    assert r_status.status_code == 200
    assert len(r_status.json()) == len(completed_tasks)
    assert r_status.json()[0]["status"] == "completed"

    r_prio = client.get("/tasks/priority/medium")
    assert r_prio.status_code == 200
    assert len(r_prio.json()) == len(medium_tasks)
    assert r_prio.json()[0]["priority"] == "medium"
