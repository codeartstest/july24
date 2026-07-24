"""SQLAlchemy ORM model for the Todo entity.

Table: todos
  id         — Integer PK, auto-increment
  title      — String(255), not null
  completed  — Boolean, default False
  created_at — DateTime, set on creation
  updated_at — DateTime, updated on every mutation
"""
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from db.database import Base


class TodoItem(Base):
    """ORM model for a todo item."""

    __tablename__ = "todos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    completed = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )

    def __repr__(self) -> str:
        return f"<TodoItem(id={self.id}, title={self.title!r}, completed={self.completed})>"
