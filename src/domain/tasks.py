

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException
from sqlmodel import Session, select

from src.data.models import Task
from src.domain.schemas import TaskCreate, TaskUpdate, TaskStatus, TaskPriority



def create_task(session: Session, task: TaskCreate):
    db_task = Task.from_orm(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task

def list_tasks(
        session: Session,
        skip: int = 0,
        limit: int = 10,
        status: Optional[TaskStatus] = None,
        priority: Optional[TaskPriority] = None
):
    query = select(Task)

    if status is not None:
        query = query.where(Task.status == status)

    if priority is not None:
        query = query.where(Task.priority == priority)

    query = query.offset(skip).limit(limit)

    tasks = session.exec(query).all()
    # List[Task] -> List[TaskResponse]
    return tasks


def get_task(
        session: Session,
        task_id: int
):
    task = session.get(Task, task_id)
    return task


def update_task(
        session: Session,
        task_id: int,
        task_update: TaskUpdate
):
    task = session.get(Task, task_id)
    if not task:
        return None

    task_data = task_update.dict(exclude_unset=True)

    for key, value in task_data.items():
        setattr(task, key, value)

    task.updated_at = datetime.now(timezone.utc)
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


def delete_task(
        session: Session,
        task_id: int
):
    task = session.get(Task, task_id)
    if not task:
        return False
    session.delete(task)
    session.commit()
    return True


def tasks_by_status(
        session: Session,
        status: TaskStatus
):
    tasks = session.exec(select(Task).where(Task.status == status)).all()
    return tasks


def tasks_by_priority(
        session: Session,
        priority: TaskPriority
):
    tasks = session.exec(select(Task).where(Task.priority == priority)).all()
    return tasks