"""
Rate Limiting Tests

Verifies that:
- Limiter key function uses user_id from JWT
- Rate limit is configured to 50/hour
- HTTP 429 is returned when limit is exceeded
"""
import pytest
from unittest.mock import MagicMock
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

from limiter import _get_user_id, CHAT_RATE_LIMIT
from config import settings


def test_rate_limit_config_is_50_per_hour():
    """Rate limit must be set to 50/hour."""
    assert settings.RATE_LIMIT_REQUESTS_PER_HOUR == 50
    assert CHAT_RATE_LIMIT == "50/hour"


def test_limiter_key_uses_user_id_when_authenticated():
    """Key function returns user_id when JWT has been validated."""
    request = MagicMock()
    request.state.user_id = "user_abc123"
    assert _get_user_id(request) == "user_abc123"


def test_limiter_key_falls_back_when_no_user_id():
    """Key function falls back gracefully when user_id is absent."""
    request = MagicMock(spec=Request)
    request.state = MagicMock(spec=[])  # no user_id attribute
    request.client = MagicMock()
    request.client.host = "127.0.0.1"
    request.headers = {}
    key = _get_user_id(request)
    assert key is not None


def test_rate_limit_returns_429_when_exceeded():
    """After exceeding the rate limit, endpoint returns HTTP 429."""
    test_limiter = Limiter(key_func=get_remote_address)
    test_app = FastAPI()
    test_app.state.limiter = test_limiter
    test_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    test_app.add_middleware(SlowAPIMiddleware)

    @test_app.get("/test-limit")
    @test_limiter.limit("2/minute")
    async def limited_endpoint(request: Request):
        return {"ok": True}

    with TestClient(test_app) as client:
        r1 = client.get("/test-limit")
        r2 = client.get("/test-limit")
        r3 = client.get("/test-limit")

    assert r1.status_code == 200
    assert r2.status_code == 200
    assert r3.status_code == 429


def test_different_users_have_independent_limits():
    """Rate limit counters are independent per user_id."""
    def key_by_header(request: Request):
        return request.headers.get("X-User-ID", "anonymous")

    test_limiter = Limiter(key_func=key_by_header)
    test_app = FastAPI()
    test_app.state.limiter = test_limiter
    test_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    test_app.add_middleware(SlowAPIMiddleware)

    @test_app.get("/test-user-limit")
    @test_limiter.limit("2/minute")
    async def limited_endpoint(request: Request):
        return {"ok": True}

    with TestClient(test_app) as client:
        # User A uses up their limit
        client.get("/test-user-limit", headers={"X-User-ID": "user_a"})
        client.get("/test-user-limit", headers={"X-User-ID": "user_a"})
        r_a_exceeded = client.get("/test-user-limit", headers={"X-User-ID": "user_a"})

        # User B still has their full limit available
        r_b = client.get("/test-user-limit", headers={"X-User-ID": "user_b"})

    assert r_a_exceeded.status_code == 429
    assert r_b.status_code == 200
