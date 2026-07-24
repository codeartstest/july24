"""Todo CRUD router — 5 REST endpoints.

Endpoints:
  GET    /api/todos           — List all todos (optional ?status=active|completed)
  POST   /api/todos           — Create a new todo
  GET    /api/todos/{todo_id}  — Get a single todo
  PATCH  /api/todos/{todo_id}  — Update todo fields
  DELETE /api/todos/{todo_id}  — Delete a todo (204 No Content)
"""
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from db.database import get_db
from models.todo import TodoCreate, TodoResponse, TodoUpdate
from services.todo_service import (
    create_todo,
    delete_todo,
    get_todo,
    list_todos,
    update_todo,
)

router = APIRouter()


@router.get("/todos", response_model=list[TodoResponse])
def get_todos(
    status_filter: str | None = Query(
        default=None,
        alias="status",
        pattern="^(active|completed)$",
        description="Filter todos by status: 'active' or 'completed'",
    ),
    db: Session = Depends(get_db),
):
    """List all todos. Optional status filter."""
    return list_todos(db, status_filter)


@router.post("/todos", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_new_todo(
    todo_create: TodoCreate,
    db: Session = Depends(get_db),
):
    """Create a new todo."""
    return create_todo(db, todo_create)


@router.get("/todos/{todo_id}", response_model=TodoResponse)
def get_single_todo(
    todo_id: int,
    db: Session = Depends(get_db),
):
    """Get a single todo by ID."""
    return get_todo(db, todo_id)


@router.patch("/todos/{todo_id}", response_model=TodoResponse)
def update_existing_todo(
    todo_id: int,
    todo_update: TodoUpdate,
    db: Session = Depends(get_db),
):
    """Update an existing todo."""
    return update_todo(db, todo_id, todo_update)


@router.delete("/todos/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_existing_todo(
    todo_id: int,
    db: Session = Depends(get_db),
):
    """Delete a todo. Returns 204 No Content."""
    delete_todo(db, todo_id)
