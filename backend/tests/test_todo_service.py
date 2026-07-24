"""Tests for the todo_service business-logic layer.

Directly tests each service function with a real in-memory SQLite database
to verify correctness of CRUD operations and error handling.
"""
import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from models.todo import TodoCreate, TodoUpdate
from services.todo_service import (
    create_todo,
    delete_todo,
    get_todo,
    list_todos,
    update_todo,
)


# ──────────────────────────────────────────────────────────────────────────────
# create_todo
# ──────────────────────────────────────────────────────────────────────────────

class TestCreateTodo:
    def test_create_returns_todo_with_defaults(self, db_session: Session):
        """Created todo has id, completed=False, and timestamps."""
        todo = create_todo(db_session, TodoCreate(title="Test item"))

        assert todo.id is not None
        assert todo.title == "Test item"
        assert todo.completed is False
        assert todo.created_at is not None
        assert todo.updated_at is not None


# ──────────────────────────────────────────────────────────────────────────────
# get_todo
# ──────────────────────────────────────────────────────────────────────────────

class TestGetTodo:
    def test_get_existing(self, db_session: Session):
        """Returns the todo when it exists."""
        created = create_todo(db_session, TodoCreate(title="Find me"))
        result = get_todo(db_session, created.id)

        assert result.id == created.id
        assert result.title == "Find me"

    def test_get_not_found_raises_404(self, db_session: Session):
        """Raises HTTPException 404 for non-existent ID."""
        with pytest.raises(HTTPException) as exc:
            get_todo(db_session, 999)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Todo not found"


# ──────────────────────────────────────────────────────────────────────────────
# list_todos
# ──────────────────────────────────────────────────────────────────────────────

class TestListTodos:
    def test_list_empty(self, db_session: Session):
        """Empty database returns an empty list."""
        assert list_todos(db_session) == []

    def test_list_all(self, db_session: Session):
        """Returns all todos ordered by id."""
        for title in ["A", "B", "C"]:
            create_todo(db_session, TodoCreate(title=title))

        result = list_todos(db_session)
        assert len(result) == 3
        assert [t.title for t in result] == ["A", "B", "C"]

    def test_list_filter_active(self, db_session: Session):
        """status_filter='active' returns only incomplete todos."""
        create_todo(db_session, TodoCreate(title="Active"))
        done = create_todo(db_session, TodoCreate(title="Done"))
        done.completed = True
        db_session.commit()

        result = list_todos(db_session, status_filter="active")
        assert len(result) == 1
        assert result[0].title == "Active"
        assert result[0].completed is False

    def test_list_filter_completed(self, db_session: Session):
        """status_filter='completed' returns only completed todos."""
        create_todo(db_session, TodoCreate(title="Active"))
        done = create_todo(db_session, TodoCreate(title="Done"))
        done.completed = True
        db_session.commit()

        result = list_todos(db_session, status_filter="completed")
        assert len(result) == 1
        assert result[0].title == "Done"
        assert result[0].completed is True

    def test_list_filter_none_returns_all(self, db_session: Session):
        """status_filter=None returns all todos."""
        for title in ["A", "B"]:
            create_todo(db_session, TodoCreate(title=title))

        result = list_todos(db_session, status_filter=None)
        assert len(result) == 2

    def test_list_filter_unknown_returns_all(self, db_session: Session):
        """Unknown status_filter value returns all todos (no filtering)."""
        for title in ["A", "B"]:
            create_todo(db_session, TodoCreate(title=title))

        result = list_todos(db_session, status_filter="unknown")
        assert len(result) == 2


# ──────────────────────────────────────────────────────────────────────────────
# update_todo
# ──────────────────────────────────────────────────────────────────────────────

class TestUpdateTodo:
    def test_update_title(self, db_session: Session):
        """Can update title."""
        created = create_todo(db_session, TodoCreate(title="Old"))
        result = update_todo(db_session, created.id, TodoUpdate(title="New"))

        assert result.title == "New"
        assert result.completed is False

    def test_update_completed(self, db_session: Session):
        """Can update completed status."""
        created = create_todo(db_session, TodoCreate(title="Task"))
        result = update_todo(db_session, created.id, TodoUpdate(completed=True))

        assert result.completed is True
        assert result.title == "Task"

    def test_update_both_fields(self, db_session: Session):
        """Can update both fields at once."""
        created = create_todo(db_session, TodoCreate(title="Original"))
        result = update_todo(
            db_session, created.id, TodoUpdate(title="Updated", completed=True)
        )

        assert result.title == "Updated"
        assert result.completed is True

    def test_update_partial_leaves_other_unchanged(self, db_session: Session):
        """Partial update (only completed) leaves title unchanged."""
        created = create_todo(db_session, TodoCreate(title="Keep"))
        result = update_todo(db_session, created.id, TodoUpdate(completed=True))

        assert result.title == "Keep"
        assert result.completed is True

    def test_update_no_fields(self, db_session: Session):
        """Empty update (no fields set) leaves todo unchanged."""
        created = create_todo(db_session, TodoCreate(title="Original"))
        result = update_todo(db_session, created.id, TodoUpdate())

        assert result.title == "Original"
        assert result.completed is False

    def test_update_not_found_raises_404(self, db_session: Session):
        """Updating non-existent ID raises 404."""
        with pytest.raises(HTTPException) as exc:
            update_todo(db_session, 999, TodoUpdate(title="X"))

        assert exc.value.status_code == 404
        assert exc.value.detail == "Todo not found"


# ──────────────────────────────────────────────────────────────────────────────
# delete_todo
# ──────────────────────────────────────────────────────────────────────────────

class TestDeleteTodo:
    def test_delete_existing(self, db_session: Session):
        """Deleting an existing todo removes it from the database."""
        created = create_todo(db_session, TodoCreate(title="Bye"))
        delete_todo(db_session, created.id)

        with pytest.raises(HTTPException) as exc:
            get_todo(db_session, created.id)
        assert exc.value.status_code == 404

    def test_delete_not_found_raises_404(self, db_session: Session):
        """Deleting non-existent ID raises 404."""
        with pytest.raises(HTTPException) as exc:
            delete_todo(db_session, 999)

        assert exc.value.status_code == 404
        assert exc.value.detail == "Todo not found"
