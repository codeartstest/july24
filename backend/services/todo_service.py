"""Todo service — business logic for CRUD operations.

Functions:
  list_todos(db, status_filter) — list all todos, optionally filtered
  get_todo(db, todo_id)          — get a single todo (raises 404)
  create_todo(db, todo_create)   — create a new todo
  update_todo(db, todo_id, data) — update an existing todo (raises 404)
  delete_todo(db, todo_id)       — delete a todo (raises 404)
"""
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from db.models import TodoItem
from models.todo import TodoCreate, TodoUpdate


def list_todos(db: Session, status_filter: str | None = None) -> list[TodoItem]:
    """List all todos, optionally filtered by completion status."""
    query = db.query(TodoItem)
    if status_filter == "active":
        query = query.filter(TodoItem.completed.is_(False))
    elif status_filter == "completed":
        query = query.filter(TodoItem.completed.is_(True))
    return query.order_by(TodoItem.id).all()


def get_todo(db: Session, todo_id: int) -> TodoItem:
    """Get a single todo by ID. Raises 404 if not found."""
    todo = db.get(TodoItem, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )
    return todo


def create_todo(db: Session, todo_create: TodoCreate) -> TodoItem:
    """Create a new todo."""
    todo = TodoItem(title=todo_create.title, completed=False)
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


def update_todo(db: Session, todo_id: int, todo_update: TodoUpdate) -> TodoItem:
    """Update an existing todo. Only provided fields are updated. Raises 404 if not found."""
    todo = db.get(TodoItem, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )

    update_data = todo_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(todo, field, value)

    db.commit()
    db.refresh(todo)
    return todo


def delete_todo(db: Session, todo_id: int) -> None:
    """Delete a todo. Raises 404 if not found."""
    todo = db.get(TodoItem, todo_id)
    if todo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Todo not found",
        )
    db.delete(todo)
    db.commit()
