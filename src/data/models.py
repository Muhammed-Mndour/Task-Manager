from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session
from src.domain.schemas import TaskStatus, TaskPriority


class Task(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = None
    due_date: Optional[datetime] = None
    assigned_to: Optional[str] = Field(default=None, max_length=100)


sqlite_file = "tasks.db"
sqlite_url = f"sqlite:///{sqlite_file}"
connect_args = {"check_same_thread": False}  # required for SQLite
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
