from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_url: str
    hmac_secret: str
    downloads_root: Path
    token_ttl_seconds: int = 300
    trust_cloudflare_headers: bool = True


def get_settings() -> Settings:
    database_url = os.environ.get("SPL_SITE_DATABASE_URL", "").strip()
    hmac_secret = os.environ.get("SPL_SITE_HMAC_SECRET", "").strip()
    downloads_root = Path(
        os.environ.get("SPL_SITE_DOWNLOADS_ROOT", "/var/www/sahabatpanganlokal/downloads")
    ).resolve()

    if not database_url:
        raise RuntimeError("SPL_SITE_DATABASE_URL is required")
    if len(hmac_secret) < 32:
        raise RuntimeError("SPL_SITE_HMAC_SECRET must contain at least 32 characters")

    return Settings(
        database_url=database_url,
        hmac_secret=hmac_secret,
        downloads_root=downloads_root,
        token_ttl_seconds=300,
        trust_cloudflare_headers=os.environ.get(
            "SPL_SITE_TRUST_CLOUDFLARE_HEADERS", "1"
        ) == "1",
    )