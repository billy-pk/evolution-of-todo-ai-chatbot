"""
Unit tests for MCP tools (add_task, list_tasks, complete_task, update_task, delete_task)

Following TDD discipline: Tests written FIRST before implementation
"""
import pytest
from sqlmodel import Session, create_engine, SQLModel, select
from models import Task
from uuid import uuid4, UUID


@pytest.fixture(scope="function")
def test_engine():
    """Create an in-memory SQLite database for testing"""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def session(test_engine):
    """Create a database session for testing"""
    with Session(test_engine) as session:
        yield session


# ========================================
# Phase 3: User Story 1 - add_task Tests
# ========================================

def test_add_task_creates_task(session):
    """
    T015: Test that add_task creates a task successfully

    Expected behavior:
    - Creates task with title and user_id
    - Returns success status
    - Task is persisted in database
    - Returns task_id, title, completed=False, created_at
    """
    from tools.server import add_task

    # Arrange
    user_id = "test_user_123"
    title = "Buy groceries"

    # Act
    result = add_task(user_id=user_id, title=title, _session=session)

    # Assert
    assert result["status"] == "success"
    assert result["data"]["title"] == title
    assert result["data"]["completed"] is False
    assert "task_id" in result["data"]
    assert "created_at" in result["data"]

    # Verify task exists in database
    task_id_str = result["data"]["task_id"]
    task_id = UUID(task_id_str)  # Convert string to UUID
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    assert task is not None
    assert task.user_id == user_id
    assert task.title == title
    assert task.description is None


def test_add_task_with_description(session):
    """
    T016: Test that add_task creates a task with description

    Expected behavior:
    - Creates task with title, description, and user_id
    - Returns success status with description
    - Description is persisted in database
    """
    from tools.server import add_task

    # Arrange
    user_id = "test_user_456"
    title = "Write report"
    description = "Q4 financial report with charts"

    # Act
    result = add_task(user_id=user_id, title=title, description=description, _session=session)

    # Assert
    assert result["status"] == "success"
    assert result["data"]["title"] == title
    assert result["data"]["description"] == description

    # Verify description is persisted
    task_id_str = result["data"]["task_id"]
    task_id = UUID(task_id_str)  # Convert string to UUID
    statement = select(Task).where(Task.id == task_id)
    task = session.exec(statement).first()
    assert task.description == description


def test_add_task_validation_errors(session):
    """
    T017: Test that add_task validates input parameters

    Expected behavior:
    - Empty title returns error
    - Title >200 characters returns error
    - Description >1000 characters returns error
    """
    from tools.server import add_task

    user_id = "test_user_789"

    # Test 1: Empty title
    result = add_task(user_id=user_id, title="", _session=session)
    assert result["status"] == "error"
    assert "title" in result["error"].lower() or "between 1 and 200" in result["error"].lower()

    # Test 2: Title too long
    long_title = "x" * 201
    result = add_task(user_id=user_id, title=long_title, _session=session)
    assert result["status"] == "error"
    assert "title" in result["error"].lower() or "200" in result["error"]

    # Test 3: Description too long
    long_description = "x" * 1001
    result = add_task(user_id=user_id, title="Valid title", description=long_description, _session=session)
    assert result["status"] == "error"
    assert "description" in result["error"].lower() or "1000" in result["error"]
