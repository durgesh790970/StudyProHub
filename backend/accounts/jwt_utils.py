import time
import jwt
from django.conf import settings

# Simple JWT helpers for demo. In production use robust library + key management.
JWT_SECRET = getattr(settings, 'JWT_SECRET', 'change-me-in-prod')
JWT_ALGO = 'HS256'
JWT_EXP_SECONDS = int(getattr(settings, 'JWT_EXP_SECONDS', 60 * 60 * 24))


def create_token(payload: dict) -> str:
    data = payload.copy()
    data['exp'] = int(time.time()) + JWT_EXP_SECONDS
    token = jwt.encode(data, JWT_SECRET, algorithm=JWT_ALGO)
    # PyJWT returns bytes in older versions; ensure string
    if isinstance(token, bytes):
        token = token.decode('utf-8')
    return token


def verify_token(token: str) -> dict:
    try:
        data = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return data
    except Exception:
        return None
