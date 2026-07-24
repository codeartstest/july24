"""Test configuration — in-memory SQLite, dependency override, TestClient fixtures.

Sets up an isolated in-memory SQLite database (StaticPool for shared connection),
overrides FastAPI's get_db dependency, and provides client/db_session fixtures.
"""
import os
import sys
from pathlib import Path

# Use in-memory SQLite for the app's default engine (prevents file creation)
os.environ.setdefault("DATABASE_URL", "sqlite://")

# Add repo root so the 'backend' package is importable for --cov=backend
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from db.database import Base, get_db
from db.models import TodoItem  # noqa: F401  — register model with Base.metadata
from main import app

# Shared in-memory SQLite engine — StaticPool keeps a single connection
# so every session sees the same tables and data.
test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def _override_get_db():
    """FastAPI dependency override — yields a session bound to the test engine."""
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(autouse=True)
def _setup_database():
    """Create tables before each test, drop them after for isolation."""
    Base.metadata.create_all(bind=test_engine)
    yield
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client() -> TestClient:
    """FastAPI TestClient for API-level tests."""
    return TestClient(app)


@pytest.fixture
def db_session():
    """SQLAlchemy session for service-layer tests."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
