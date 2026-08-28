"""Shared dependencies: authentication, role guards, login rate limiting."""
from __future__ import annotations

import time
from collections import defaultdict, deque
from typing import Annotated

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models.models import User
from ..security.tokens import decode_access_token

bearer_scheme = HTTPBearer(auto_error=False)

DbDep = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbDep,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)],
) -> User:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if payload is None or "sub" not in payload:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
    user = db.get(User, int(payload["sub"]))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, detail="User no longer exists")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(*roles: str):
    def _check(user: CurrentUser) -> User:
        if user.role not in roles:
            raise HTTPException(status.HTTP_403_FORBIDDEN, detail="Insufficient permissions")
        return user

    return _check


# ---------------------------------------------------------------------------
# Simple in-memory login rate limiter (per identity + IP).
# Documented limitation: for multi-worker production, use a shared store (Redis).
# ---------------------------------------------------------------------------

_rate_buckets: dict[str, deque[float]] = defaultdict(deque)


def _bucket_key(identity: str, request: Request) -> str:
    client_ip = request.client.host if request.client else "unknown"
    return f"{client_ip}|{identity.lower()}"


def check_login_rate_limit(identity: str, request: Request) -> None:
    key = _bucket_key(identity, request)
    now = time.monotonic()
    bucket = _rate_buckets[key]
    while bucket and now - bucket[0] > settings.login_rate_limit_window_seconds:
        bucket.popleft()
    if len(bucket) >= settings.login_rate_limit_attempts:
        raise HTTPException(
            status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many login attempts. Please try again later.",
        )
    bucket.append(now)


def reset_login_rate_limit(identity: str, request: Request) -> None:
    _rate_buckets.pop(_bucket_key(identity, request), None)
