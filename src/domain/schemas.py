from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime, timezone
from enum import Enum


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    cancelled = "cancelled"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    urgent = "urgent"


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.pending
    priority: TaskPriority = TaskPriority.medium
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None

    @validator("title")
    def title_not_empty(cls, v):
        v = v.strip()  # Remove leading/trailing spaces
        if not v:
            raise ValueError("Title must not be empty or whitespace")
        return v

    @validator("due_date")
    def due_date_must_be_future(cls, v):
        if v and v <= datetime.now(timezone.utc):
            raise ValueError("Due date must be in the future")
        return v


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = None

    @validator("title")
    def title_not_empty(cls, v):
        if v is not None:
            v = v.strip()
            if not v:
                raise ValueError("Title must not be empty or whitespace")
        return v

    @validator("due_date")
    def due_date_must_be_future(cls, v):
        if v and v <= datetime.now(timezone.utc):
            raise ValueError("Due date must be in the future")
        return v


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    status: TaskStatus
    priority: TaskPriority
    created_at: datetime
    updated_at: Optional[datetime]
    due_date: Optional[datetime]
    assigned_to: Optional[str]

    class Config:
        orm_mode = True
