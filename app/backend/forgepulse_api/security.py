"""Runtime security for ForgePulse API.

API-key authentication, role-based authorization, per-key rate limiting, and
structured audit logging. Implemented with FastAPI dependencies and the standard
library only — no extra runtime dependencies.

Configuration (environment):
- ``FORGEPULSE_API_KEYS``: comma-separated ``<key>:<role>`` entries, e.g.
  ``"alice-key:admin,bob-key:viewer"``. Role is one of viewer|engineer|admin.
  When unset or empty the API runs in **open mode** (no auth) for local
  development; a warning is logged. Open mode must NOT be used in production.
- ``FORGEPULSE_RATE_LIMIT``: max requests per key per minute (default 60).
"""

from __future__ import annotations

import json
import logging
import os
import time
from collections import deque
from pathlib import Path
from typing import Literal

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader

logger = logging.getLogger(__name__)

Role = Literal["viewer", "engineer", "admin"]
_VALID_ROLES: set[str] = {"viewer", "engineer", "admin"}

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


def _load_api_keys() -> dict[str, str]:
    """Parse ``FORGEPULSE_API_KEYS`` into a ``{key: role}`` mapping."""
    raw = os.getenv("FORGEPULSE_API_KEYS", "").strip()
    if not raw:
        return {}
    keys: dict[str, str] = {}
    for entry in raw.split(","):
        entry = entry.strip()
        if not entry:
            continue
        if ":" not in entry:
            logger.warning("Ignoring malformed API key entry (missing role): %r", entry)
            continue
        key, role = entry.rsplit(":", 1)
        key, role = key.strip(), role.strip().lower()
        if role not in _VALID_ROLES:
            logger.warning("Ignoring API key with unknown role %r (expected viewer|engineer|admin)", role)
            continue
        if not key:
            continue
        keys[key] = role
    return keys


def _rate_limit_per_minute() -> int:
    try:
        value = int(os.getenv("FORGEPULSE_RATE_LIMIT", "60"))
    except ValueError:
        return 60
    return max(0, value)


def is_open_mode() -> bool:
    """True when no API keys are configured (open/dev mode)."""
    return not _load_api_keys()


# Per-key sliding window of request timestamps (minute window).
_request_log: dict[str, deque[float]] = {}
# Per-IP fallback bucket for open mode (so a stray open deployment still caps abuse).
_ip_log: dict[str, deque[float]] = {}

_AUDIT_PATH = Path(os.getenv("FORGEPULSE_AUDIT_LOG", "logs/audit.jsonl"))


def _prune(window: deque[float], now: float) -> None:
    cutoff = now - 60.0
    while window and window[0] < cutoff:
        window.popleft()


def _rate_exceeded(bucket_id: str, store: dict[str, deque[float]]) -> bool:
    limit = _rate_limit_per_minute()
    if limit <= 0:
        return False
    now = time.monotonic()
    window = store.setdefault(bucket_id, deque())
    _prune(window, now)
    if len(window) >= limit:
        return True
    window.append(now)
    return False


def _audit(request: Request, status_code: int, latency_ms: float, *, key_id: str, role: str) -> None:
    record = {
        "ts": int(time.time()),
        "key_id": key_id,
        "role": role,
        "method": request.method,
        "path": request.url.path,
        "status": status_code,
        "latency_ms": round(latency_ms, 2),
        "client": request.client.host if request.client else None,
    }
    try:
        _AUDIT_PATH.parent.mkdir(parents=True, exist_ok=True)
        with _AUDIT_PATH.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    except OSError:
        logger.warning("Failed to write audit log entry", exc_info=True)


class Principal:
    """The authenticated caller (or the open-mode surrogate)."""

    __slots__ = ("key_id", "role", "open_mode")

    def __init__(self, key_id: str, role: str, open_mode: bool):
        self.key_id = key_id
        self.role = role
        self.open_mode = open_mode


async def verify_api_key(request: Request, api_key: str | None = Depends(_api_key_header)) -> Principal:
    """Resolve the caller. In open mode any request is allowed as a viewer."""
    keys = _load_api_keys()
    if not keys:
        # Open mode: rate-limit by IP to avoid runaway abuse.
        ip = request.client.host if request.client else "unknown"
        if _rate_exceeded(ip, _ip_log):
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail={"code": "rate_limited", "detail": "Too many requests from this address."},
            )
        return Principal(key_id="open", role="viewer", open_mode=True)

    if not api_key or api_key not in keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": "invalid_api_key", "detail": "A valid X-API-Key header is required."},
            headers={"WWW-Authenticate": 'ApiKey realm="forgepulse"'},
        )
    role = keys[api_key]
    # Mask key for logging/audit (first 4 chars only).
    masked = api_key[:4] + "…" if len(api_key) > 4 else api_key[:1] + "…"
    # Set the principal BEFORE the rate-limit check so a 429 is still audited
    # against the correct caller.
    request.state.principal = Principal(key_id=masked, role=role, open_mode=False)
    if _rate_exceeded(api_key, _request_log):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={"code": "rate_limited", "detail": "Rate limit exceeded for this API key."},
        )
    return request.state.principal


def require_role(*allowed: str):
    """Dependency factory: require the caller's role to be in ``allowed``."""

    async def _dep(principal: Principal = Depends(verify_api_key)) -> Principal:
        if principal.open_mode:
            return principal
        if principal.role not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={"code": "forbidden", "detail": f"Role '{principal.role}' is not permitted for this action."},
            )
        return principal

    return _dep


async def audit_dispatch(request: Request, call_next):
    """Starlette HTTP middleware dispatch: structured audit log per request."""
    start = time.monotonic()
    response = await call_next(request)
    latency_ms = (time.monotonic() - start) * 1000.0
    principal: Principal = getattr(request.state, "principal", None) or Principal("open", "viewer", True)
    _audit(request, response.status_code, latency_ms, key_id=principal.key_id, role=principal.role)
    return response
