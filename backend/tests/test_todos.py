"""Tests for the Todo CRUD API endpoints.

Covers all 5 REST endpoints:
  GET    /api/todos           — list (with filter)
  POST   /api/todos           — create (with validation)
  GET    /api/todos/{id}      — single item (found / 404)
  PATCH  /api/todos/{id}      — update (full / partial / 404)
  DELETE /api/todos/{id}      — delete (success / 404 / 204)
"""
import pytest
from fastapi.testclient import TestClient


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/todos
# ──────────────────────────────────────────────────────────────────────────────

class TestListTodos:
    def test_list_empty(self, client: TestClient):
        """Empty database returns 200 with an empty list."""
        response = client.get("/api/todos")
        assert response.status_code == 200
        assert response.json() == []

    def test_list_returns_all(self, client: TestClient):
        """Returns all todos ordered by id."""
        for title in ["Buy milk", "Walk dog", "Write tests"]:
            client.post("/api/todos", json={"title": title})

        response = client.get("/api/todos")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        assert data[0]["title"] == "Buy milk"
        assert data[2]["title"] == "Write tests"

    def test_list_filter_active(self, client: TestClient):
        """?status=active returns only incomplete todos."""
        client.post("/api/todos", json={"title": "Active"})
        resp = client.post("/api/todos", json={"title": "Done"})
        client.patch(f"/api/todos/{resp.json()['id']}", json={"completed": True})

        response = client.get("/api/todos?status=active")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Active"
        assert data[0]["completed"] is False

    def test_list_filter_completed(self, client: TestClient):
        """?status=completed returns only completed todos."""
        client.post("/api/todos", json={"title": "Active"})
        resp = client.post("/api/todos", json={"title": "Done"})
        client.patch(f"/api/todos/{resp.json()['id']}", json={"completed": True})

        response = client.get("/api/todos?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Done"
        assert data[0]["completed"] is True

    def test_list_invalid_status_returns_422(self, client: TestClient):
        """Invalid ?status value returns 422 validation error."""
        response = client.get("/api/todos?status=invalid")
        assert response.status_code == 422


# ──────────────────────────────────────────────────────────────────────────────
# POST /api/todos
# ──────────────────────────────────────────────────────────────────────────────

class TestCreateTodo:
    def test_create_valid(self, client: TestClient):
        """Valid title returns 201 with the created todo."""
        response = client.post("/api/todos", json={"title": "New task"})
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == 1
        assert data["title"] == "New task"
        assert data["completed"] is False
        assert "created_at" in data
        assert "updated_at" in data

    def test_create_empty_title_rejected(self, client: TestClient):
        """Empty title returns 422."""
        response = client.post("/api/todos", json={"title": ""})
        assert response.status_code == 422

    def test_create_missing_title_rejected(self, client: TestClient):
        """Missing title field returns 422."""
        response = client.post("/api/todos", json={})
        assert response.status_code == 422

    def test_create_title_too_long_rejected(self, client: TestClient):
        """Title exceeding 255 chars returns 422."""
        response = client.post("/api/todos", json={"title": "x" * 256})
        assert response.status_code == 422


# ──────────────────────────────────────────────────────────────────────────────
# GET /api/todos/{id}
# ──────────────────────────────────────────────────────────────────────────────

class TestGetSingleTodo:
    def test_get_existing(self, client: TestClient):
        """Existing todo returns 200 with full details."""
        resp = client.post("/api/todos", json={"title": "Find me"})
        todo_id = resp.json()["id"]

        response = client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == todo_id
        assert data["title"] == "Find me"

    def test_get_not_found(self, client: TestClient):
        """Non-existent ID returns 404."""
        response = client.get("/api/todos/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Todo not found"


# ──────────────────────────────────────────────────────────────────────────────
# PATCH /api/todos/{id}
# ──────────────────────────────────────────────────────────────────────────────

class TestUpdateTodo:
    def test_update_title(self, client: TestClient):
        """Can update the title field."""
        resp = client.post("/api/todos", json={"title": "Old"})
        todo_id = resp.json()["id"]

        response = client.patch(f"/api/todos/{todo_id}", json={"title": "New"})
        assert response.status_code == 200
        assert response.json()["title"] == "New"
        assert response.json()["completed"] is False

    def test_update_completed(self, client: TestClient):
        """Can update the completed field."""
        resp = client.post("/api/todos", json={"title": "Task"})
        todo_id = resp.json()["id"]

        response = client.patch(f"/api/todos/{todo_id}", json={"completed": True})
        assert response.status_code == 200
        assert response.json()["completed"] is True
        assert response.json()["title"] == "Task"

    def test_update_both_fields(self, client: TestClient):
        """Can update both fields simultaneously."""
        resp = client.post("/api/todos", json={"title": "Original"})
        todo_id = resp.json()["id"]

        response = client.patch(
            f"/api/todos/{todo_id}",
            json={"title": "Updated", "completed": True},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated"
        assert data["completed"] is True

    def test_update_partial_leaves_other_unchanged(self, client: TestClient):
        """Partial update leaves other fields unchanged."""
        resp = client.post("/api/todos", json={"title": "Keep"})
        todo_id = resp.json()["id"]

        response = client.patch(f"/api/todos/{todo_id}", json={"completed": True})
        assert response.status_code == 200
        assert response.json()["title"] == "Keep"
        assert response.json()["completed"] is True

    def test_update_empty_body(self, client: TestClient):
        """Empty body returns the todo unchanged."""
        resp = client.post("/api/todos", json={"title": "No change"})
        todo_id = resp.json()["id"]

        response = client.patch(f"/api/todos/{todo_id}", json={})
        assert response.status_code == 200
        assert response.json()["title"] == "No change"
        assert response.json()["completed"] is False

    def test_update_not_found(self, client: TestClient):
        """Updating non-existent ID returns 404."""
        response = client.patch("/api/todos/999", json={"title": "X"})
        assert response.status_code == 404
        assert response.json()["detail"] == "Todo not found"

    def test_update_empty_title_rejected(self, client: TestClient):
        """Empty title in update returns 422."""
        resp = client.post("/api/todos", json={"title": "Keep"})
        todo_id = resp.json()["id"]

        response = client.patch(f"/api/todos/{todo_id}", json={"title": ""})
        assert response.status_code == 422


# ──────────────────────────────────────────────────────────────────────────────
# DELETE /api/todos/{id}
# ──────────────────────────────────────────────────────────────────────────────

class TestDeleteTodo:
    def test_delete_success(self, client: TestClient):
        """Deleting an existing todo returns 204 with empty body."""
        resp = client.post("/api/todos", json={"title": "Bye"})
        todo_id = resp.json()["id"]

        response = client.delete(f"/api/todos/{todo_id}")
        assert response.status_code == 204
        assert response.content == b""

    def test_delete_not_found(self, client: TestClient):
        """Deleting non-existent ID returns 404."""
        response = client.delete("/api/todos/999")
        assert response.status_code == 404
        assert response.json()["detail"] == "Todo not found"

    def test_delete_verifies_gone(self, client: TestClient):
        """After deletion, GET returns 404."""
        resp = client.post("/api/todos", json={"title": "Temp"})
        todo_id = resp.json()["id"]
        client.delete(f"/api/todos/{todo_id}")

        response = client.get(f"/api/todos/{todo_id}")
        assert response.status_code == 404

    def test_delete_then_list_empty(self, client: TestClient):
        """After deleting the only todo, list returns empty."""
        resp = client.post("/api/todos", json={"title": "Solo"})
        client.delete(f"/api/todos/{resp.json()['id']}")

        response = client.get("/api/todos")
        assert response.status_code == 200
        assert response.json() == []


# ──────────────────────────────────────────────────────────────────────────────
# Health & root endpoints
# ──────────────────────────────────────────────────────────────────────────────

class TestHealthEndpoints:
    def test_root(self, client: TestClient):
        """Root endpoint returns a running message."""
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()

    def test_health_check(self, client: TestClient):
        """Health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


# ──────────────────────────────────────────────────────────────────────────────
# Database dependency & ORM model (coverage for db/database.py, db/models.py)
# ──────────────────────────────────────────────────────────────────────────────

class TestDatabaseDependency:
    def test_get_db_yields_and_closes(self):
        """get_db yields a session and closes it on StopIteration."""
        from db.database import get_db

        gen = get_db()
        session = next(gen)
        assert session is not None
        with pytest.raises(StopIteration):
            next(gen)

    def test_todo_repr(self):
        """TodoItem.__repr__ includes id, title, and completed."""
        from db.models import TodoItem

        todo = TodoItem(id=1, title="Test", completed=False)
        result = repr(todo)
        assert "TodoItem" in result
        assert "Test" in result
