from slowapi import Limiter
from slowapi.util import get_remote_address
from fastapi import Request
from app.core.config import settings

def get_user_id_or_ip(request: Request) -> str:
    """Extract user ID from JWT token or fallback to IP"""
    try:
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.replace("Bearer ", "")
            from app.api.v1.auth import decode_token
            payload = decode_token(token)
            return f"user:{payload.get('sub')}"
    except:
        pass
    
    return f"ip:{get_remote_address(request)}"

# Global rate limiter (IP-based)
limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.REDIS_URL,
    default_limits=["100/minute"],
    headers_enabled=True
)

# User-based rate limiter
user_limiter = Limiter(
    key_func=get_user_id_or_ip,
    storage_uri=settings.REDIS_URL,
    headers_enabled=True
)
