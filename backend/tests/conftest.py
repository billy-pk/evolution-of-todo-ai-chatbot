import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from sqlmodel import create_engine, Session, SQLModel
from fastapi import Request

from main import create_app
from db import get_session
from middleware import JWTBearer

TEST_USER_ID = "test_user_123"


@pytest.fixture(scope="function")
def test_engine():
    """In-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    SQLModel.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def client(test_engine):
    """Test client with JWT mocked and in-memory DB."""
    app = create_app()

    def override_get_session():
        with Session(test_engine) as session:
            yield session

    async def override_jwt_bearer(request: Request):
        request.state.user_id = TEST_USER_ID
        return TEST_USER_ID

    app.dependency_overrides[get_session] = override_get_session
    app.dependency_overrides[JWTBearer] = override_jwt_bearer

    with TestClient(app) as c:
        yield c
