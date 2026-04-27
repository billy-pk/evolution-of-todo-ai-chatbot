"""
Phase 3 API Contract Tests

Verifies that the Phase 3 API endpoints follow the expected contract:
- Health endpoint structure
- Chat endpoint requires authentication
- Correct HTTP status codes
"""
import pytest
from fastapi.testclient import TestClient
from main import app


@pytest.fixture
def app_client():
    with TestClient(app) as c:
        yield c


def test_health_endpoint_returns_200(app_client):
    response = app_client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_structure(app_client):
    response = app_client.get("/health")
    data = response.json()
    assert "status" in data
    assert "database" in data
    assert data["status"] in ["healthy", "unhealthy"]


def test_api_health_endpoint_returns_200(app_client):
    response = app_client.get("/api/health")
    assert response.status_code == 200


def test_chat_endpoint_requires_auth(app_client):
    """Chat endpoint must return 401 without a JWT token."""
    response = app_client.post(
        "/api/test_user/chat",
        json={"message": "hello"}
    )
    assert response.status_code == 401


def test_chatkit_endpoint_requires_auth(app_client):
    """ChatKit endpoint must return 401 without a JWT token."""
    response = app_client.post("/chatkit", json={})
    assert response.status_code == 401


def test_unknown_endpoint_returns_404(app_client):
    response = app_client.get("/api/nonexistent")
    assert response.status_code == 404
