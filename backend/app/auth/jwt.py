import base64
import hashlib
import hmac
import json
from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import HTTPException, status

from app.core.config import settings


ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
SUPPORTED_ALGORITHM: str = "HS256"
SECRET_KEY: str = getattr(settings, "SECRET_KEY", "change-this-secret-key")
ALGORITHM: str = getattr(settings, "ALGORITHM", SUPPORTED_ALGORITHM)


def _base64url_encode(data: bytes) -> str:
    """Encode bytes using JWT-compatible base64url without padding."""

    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _base64url_decode(data: str) -> bytes:
    """Decode JWT-compatible base64url data."""

    padding: str = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(f"{data}{padding}".encode("ascii"))


def _json_to_base64url(data: dict[str, Any]) -> str:
    """Serialize JSON in a stable compact form for token signing."""

    serialized = json.dumps(data, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return _base64url_encode(serialized)


def _sign(message: str) -> str:
    """Create an HS256 signature for a JWT header and payload."""

    if ALGORITHM != SUPPORTED_ALGORITHM:
        raise ValueError(f"Unsupported JWT algorithm: {ALGORITHM}")

    signature = hmac.new(
        SECRET_KEY.encode("utf-8"),
        message.encode("ascii"),
        hashlib.sha256,
    ).digest()

    return _base64url_encode(signature)


def create_access_token(
    *,
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a signed JWT access token for the provided subject."""

    now = datetime.now(UTC)
    expires_at = now + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))

    header: dict[str, str] = {"alg": ALGORITHM, "typ": "JWT"}
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }

    signing_input = f"{_json_to_base64url(header)}.{_json_to_base64url(payload)}"
    return f"{signing_input}.{_sign(signing_input)}"


def verify_access_token(token: str) -> dict[str, Any]:
    """Verify a JWT access token and return its payload."""

    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        header_segment, payload_segment, signature = token.split(".")
        signing_input = f"{header_segment}.{payload_segment}"
        expected_signature = _sign(signing_input)

        if not hmac.compare_digest(signature, expected_signature):
            raise credentials_error

        header = json.loads(_base64url_decode(header_segment))
        payload = json.loads(_base64url_decode(payload_segment))

        if header.get("alg") != ALGORITHM:
            raise credentials_error

        expires_at = int(payload["exp"])
        if datetime.now(UTC).timestamp() >= expires_at:
            raise credentials_error

        if not payload.get("sub"):
            raise credentials_error

        return payload
    except (KeyError, ValueError, json.JSONDecodeError):
        raise credentials_error
