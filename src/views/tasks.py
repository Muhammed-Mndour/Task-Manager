from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Depends, Query
from sqlmodel import select, Session
from typing import List, Annotated, Optional, Literal
from src.data.models import Task, get_session
from src.domain.schemas import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskStatus,
    TaskPriority,
)

from src.domain.tasks import (
    create_task as create_task_service,
    list_tasks as list_tasks_service,
    get_task as get_task_service,
    update_task as update_task_service,
    delete_task as delete_task_service,
    tasks_by_status as tasks_by_status_service,
    tasks_by_priority as tasks_by_priority_service,
)

SessionDep = Annotated[Session, Depends(get_session)]

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post(
    "/",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new task",
)
def create_task(task: TaskCreate, session: SessionDep):
    return create_task_service(session, task)


@router.get(
    "/",
    response_model=List[TaskResponse],
    status_code=status.HTTP_200_OK,
    summary="List tasks with optional filters & pagination",
)
def list_tasks(
        session: SessionDep,
        skip: int = 0,
        limit: int = 10,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None,
        sort_by: Optional[Literal["created_at", "updated_at", "due_date"]] = None,
        sort_order: Literal["asc", "desc"] = "asc"
):
    return list_tasks_service(session, skip, limit, status, priority,sort_by,sort_order)


@router.get(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a task by ID",
)
def get_task(session: SessionDep, task_id: int):
    task = get_task_service(session, task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing task",
)
def update_task(session: SessionDep, task_id: int, task_update: TaskUpdate):
    task = update_task_service(session, task_id, task_update)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.delete(
    "/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task"
)
def delete_task(session: SessionDep, task_id: int):
    success = delete_task_service(session, task_id)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")


@router.get(
    "/status/{status}", response_model=List[TaskResponse], summary="Get tasks by status"
)
def tasks_by_status(session: SessionDep, status: TaskStatus):
    return tasks_by_status_service(session, status)


@router.get(
    "/priority/{priority}",
    response_model=List[TaskResponse],
    summary="Get tasks by priority",
)
def tasks_by_priority(session: SessionDep, priority: TaskPriority):
    return tasks_by_priority_service(session, priority)
