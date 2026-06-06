"""
Unit tests for ChatKit integration endpoints.

Tests cover:
- Thread management (create, list, get)
- Message validation
- Authentication (missing/invalid token)
- User isolation
"""

import pytest
import jwt
from datetime import datetime, UTC, timedelta
from uuid import uuid4
from sqlmodel import Session, select

from main import app
from config import settings
from models import Conversation, Message


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def test_user_id():
    return str(uuid4())


@pytest.fixture
def test_jwt_token(test_user_id):
    """HS256 test token — accepted by the monkeypatched verify_token below."""
    now = datetime.now(UTC)
    payload = {
        "sub": test_user_id,
        "user_id": test_user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(hours=1)).timestamp()),
    }
    return jwt.encode(payload, settings.BETTER_AUTH_SECRET, algorithm="HS256")


@pytest.fixture
def client():
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture
def db_session():
    from db import engine
    from sqlmodel import Session as SQLModelSession
    session = SQLModelSession(engine)
    yield session
    session.close()


@pytest.fixture(autouse=True)
def mock_verify_token(monkeypatch):
    """
    Patch verify_token in chatkit routes to accept HS256 test tokens,
    bypassing the JWKS endpoint (which requires the frontend to be running).
    """
    def fake_verify(token: str):
        try:
            payload = jwt.decode(
                token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"]
            )
            return payload.get("user_id") or payload.get("sub")
        except Exception:
            return None

    monkeypatch.setattr("routes.chatkit.verify_token", fake_verify)


# ============================================================================
# Authentication Tests
# ============================================================================

class TestAuthentication:
    """All chatkit routes require a valid Bearer JWT."""

    def test_missing_auth_header_returns_401(self, client):
        response = client.get("/api/chatkit/threads")
        assert response.status_code == 401
        assert "Missing Authorization header" in response.json()["detail"]

    def test_invalid_token_returns_401(self, client):
        response = client.get(
            "/api/chatkit/threads",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401
        assert "Invalid or expired token" in response.json()["detail"]

    def test_valid_token_accepted(self, client, test_jwt_token):
        response = client.get(
            "/api/chatkit/threads",
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )
        assert response.status_code == 200


# ============================================================================
# Thread Management Tests
# ============================================================================

class TestThreadEndpoints:

    def test_create_thread(self, client, test_jwt_token, db_session):
        response = client.post(
            "/api/chatkit/threads",
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "created_at" in data

        stmt = select(Conversation).where(Conversation.id == data["id"])
        conv = db_session.exec(stmt).first()
        assert conv is not None

    def test_list_threads(self, client, test_jwt_token, test_user_id, db_session):
        conv = Conversation(user_id=test_user_id)
        db_session.add(conv)
        db_session.commit()

        response = client.get(
            "/api/chatkit/threads",
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "threads" in data
        assert len(data["threads"]) >= 1

    def test_get_thread_with_messages(self, client, test_jwt_token, test_user_id, db_session):
        conv = Conversation(user_id=test_user_id)
        db_session.add(conv)
        db_session.commit()
        db_session.refresh(conv)

        msg = Message(
            conversation_id=conv.id,
            user_id=test_user_id,
            role="user",
            content="Test message"
        )
        db_session.add(msg)
        db_session.commit()

        response = client.get(
            f"/api/chatkit/threads/{conv.id}",
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(conv.id)
        assert len(data["messages"]) == 1
        assert data["messages"][0]["content"] == "Test message"

    def test_get_nonexistent_thread_returns_404(self, client, test_jwt_token):
        response = client.get(
            f"/api/chatkit/threads/{uuid4()}",
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )
        assert response.status_code == 404


# ============================================================================
# Message Validation Tests
# ============================================================================

class TestMessageEndpoint:

    def test_missing_thread_id_returns_400(self, client, test_jwt_token):
        response = client.post(
            "/api/chatkit/messages",
            json={"message": "Hello"},
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )
        assert response.status_code == 400
        assert "Missing thread_id or message" in response.json()["detail"]

    def test_missing_message_text_returns_400(self, client, test_jwt_token):
        response = client.post(
            "/api/chatkit/messages",
            json={"thread_id": str(uuid4())},
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )
        assert response.status_code == 400

    def test_nonexistent_thread_returns_404(self, client, test_jwt_token):
        response = client.post(
            "/api/chatkit/messages",
            json={"thread_id": str(uuid4()), "message": "Test"},
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )
        assert response.status_code == 404
        assert "Thread not found" in response.json()["detail"]


# ============================================================================
# User Isolation Tests
# ============================================================================

class TestUserIsolation:

    def test_user_cannot_access_another_users_thread(
        self, client, test_jwt_token, db_session
    ):
        """User A's JWT cannot retrieve User B's thread."""
        user_b_id = str(uuid4())
        conv_b = Conversation(user_id=user_b_id)
        db_session.add(conv_b)
        db_session.commit()
        db_session.refresh(conv_b)

        response = client.get(
            f"/api/chatkit/threads/{conv_b.id}",
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )
        assert response.status_code == 404

    def test_list_threads_only_returns_own_threads(
        self, client, test_jwt_token, test_user_id, db_session
    ):
        """List threads returns only the authenticated user's conversations."""
        # Create thread for current user
        conv_own = Conversation(user_id=test_user_id)
        db_session.add(conv_own)

        # Create thread for another user
        conv_other = Conversation(user_id=str(uuid4()))
        db_session.add(conv_other)
        db_session.commit()

        response = client.get(
            "/api/chatkit/threads",
            headers={"Authorization": f"Bearer {test_jwt_token}"}
        )

        assert response.status_code == 200
        thread_ids = [t["id"] for t in response.json()["threads"]]
        assert str(conv_own.id) in thread_ids
        assert str(conv_other.id) not in thread_ids
