"""Pydantic schemas for Todo CRUD operations.

Schemas:
  TodoCreate   — POST request body (title required)
  TodoUpdate   — PATCH request body (all fields optional)
  TodoResponse — All API responses
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TodoBase(BaseModel):
    """Shared fields for todo schemas."""

    title: str = Field(min_length=1, max_length=255, description="Todo title")


class TodoCreate(TodoBase):
    """Schema for POST /api/todos — create a new todo."""

    pass


class TodoUpdate(BaseModel):
    """Schema for PATCH /api/todos/{id} — partial update (all fields optional)."""

    title: str | None = Field(default=None, min_length=1, max_length=255)
    completed: bool | None = None


class TodoResponse(BaseModel):
    """Schema for all API responses."""

    id: int
    title: str
    completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
