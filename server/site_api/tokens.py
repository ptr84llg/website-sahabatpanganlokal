from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import base64
import hashlib
import hmac
import json
from uuid import UUID


@dataclass(frozen=True)
class PreflightClaims:
    platform: str
    version: str
    nonce: UUID
    issued_at: int
    expires_at: int


class TokenError(ValueError):
    pass


def _b64encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def create_preflight_token(
    platform: str,
    version: str,
    nonce: UUID,
    now: datetime,
    secret: str,
    ttl_seconds: int = 300,
) -> str:
    if platform not in {"android", "windows"}:
        raise TokenError("unsupported platform")
    issued_at = int(now.astimezone(timezone.utc).timestamp())
    payload = {
        "p": platform,
        "v": version,
        "n": str(nonce),
        "iat": issued_at,
        "exp": issued_at + ttl_seconds,
    }
    body = _b64encode(
        json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    )
    signature = _b64encode(
        hmac.new(secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).digest()
    )
    return f"{body}.{signature}"


def verify_preflight_token(
    token: str,
    now: datetime,
    secret: str,
) -> PreflightClaims:
    try:
        body, supplied_signature = token.split(".", 1)
    except ValueError as exc:
        raise TokenError("invalid token format") from exc

    expected_signature = _b64encode(
        hmac.new(secret.encode("utf-8"), body.encode("ascii"), hashlib.sha256).digest()
    )
    if not hmac.compare_digest(supplied_signature, expected_signature):
        raise TokenError("invalid token signature")

    try:
        payload = json.loads(_b64decode(body).decode("utf-8"))
        platform = str(payload["p"])
        version = str(payload["v"])
        nonce = UUID(str(payload["n"]))
        issued_at = int(payload["iat"])
        expires_at = int(payload["exp"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise TokenError("invalid token claims") from exc

    now_epoch = int(now.astimezone(timezone.utc).timestamp())
    if expires_at < now_epoch:
        raise TokenError("expired token")
    if issued_at > now_epoch + 30:
        raise TokenError("token issued in the future")
    if platform not in {"android", "windows"}:
        raise TokenError("unsupported platform")

    return PreflightClaims(
        platform=platform,
        version=version,
        nonce=nonce,
        issued_at=issued_at,
        expires_at=expires_at,
    )