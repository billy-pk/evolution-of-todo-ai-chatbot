from slowapi import Limiter
from slowapi.util import get_remote_address
from config import settings


def _get_user_id(request) -> str:
    """Rate limit key: authenticated user_id, fallback to IP."""
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return user_id
    return get_remote_address(request)


limiter = Limiter(key_func=_get_user_id)
CHAT_RATE_LIMIT = f"{settings.RATE_LIMIT_REQUESTS_PER_HOUR}/hour"
