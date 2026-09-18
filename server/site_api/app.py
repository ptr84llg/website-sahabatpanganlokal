from __future__ import annotations

from collections import deque
from datetime import datetime, timezone
import os
from pathlib import Path
import time
from uuid import uuid4

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from .config import get_settings
from .db import (
    CoarseLocation,
    connect,
    count_recent_downloads,
    get_active_release,
    get_download_stats,
    record_download_start,
)
from .health import classify_server_status, classify_traffic
from .integrity import sha256_file
from .models import DownloadStartInput
from .tokens import TokenError, create_preflight_token, verify_preflight_token


app = FastAPI(
    title="Sahabat Pangan Lokal Site API",
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

RECENT_LATENCY_MS: deque[float] = deque(maxlen=200)
RATE_BUCKETS: dict[str, deque[float]] = {}


def _p95_ms() -> float:
    if not RECENT_LATENCY_MS:
        return 0.0
    values = sorted(RECENT_LATENCY_MS)
    index = min(len(values) - 1, int(len(values) * 0.95))
    return float(values[index])


def _available_memory_ratio() -> float:
    try:
        values = {}
        for line in Path("/proc/meminfo").read_text(encoding="utf-8").splitlines():
            key, raw = line.split(":", 1)
            values[key] = int(raw.strip().split()[0])
        return values["MemAvailable"] / values["MemTotal"]
    except Exception:
        return 1.0


def _server_status() -> str:
    cpu_count = max(1, os.cpu_count() or 1)
    try:
        load_ratio = os.getloadavg()[0] / cpu_count
    except (AttributeError, OSError):
        load_ratio = 0.0
    return classify_server_status(
        load_ratio=load_ratio,
        available_memory_ratio=_available_memory_ratio(),
        api_p95_ms=_p95_ms(),
    )


def _trusted_location(
    settings,
    cf_country: str | None,
    cf_region: str | None,
    cf_region_code: str | None,
    cf_city: str | None,
) -> CoarseLocation:
    if not settings.trust_cloudflare_headers:
        return CoarseLocation(None, None, None, None, None, "unknown", "none")

    country_code = (cf_country or "").strip().upper()[:2] or None
    region = (cf_region or "").strip()[:120] or None
    region_code = (cf_region_code or "").strip()[:24] or None
    city = (cf_city or "").strip()[:120] or None

    if city:
        granularity = "city"
    elif region:
        granularity = "region"
    elif country_code:
        granularity = "country"
    else:
        granularity = "unknown"

    return CoarseLocation(
        country_code=country_code,
        country_name=None,
        region=region,
        region_code=region_code,
        city=city,
        granularity=granularity,
        source="cloudflare" if country_code or region or city else "none",
    )


@app.middleware("http")
async def timing_and_rate_limit(request: Request, call_next):
    started = time.perf_counter()

    if request.url.path.startswith("/api/site/v1/"):
        client_key = request.headers.get("CF-Connecting-IP") or (
            request.client.host if request.client else "unknown"
        )
        now = time.monotonic()
        bucket = RATE_BUCKETS.setdefault(client_key, deque())
        while bucket and bucket[0] < now - 60:
            bucket.popleft()
        if len(bucket) >= 120:
            return JSONResponse(
                status_code=429,
                content={"ok": False, "detail": "Terlalu banyak permintaan."},
            )
        bucket.append(now)

    try:
        return await call_next(request)
    finally:
        RECENT_LATENCY_MS.append((time.perf_counter() - started) * 1000)


@app.get("/api/site/v1/download-stats")
def download_stats():
    settings = get_settings()
    with connect(settings.database_url) as conn:
        stats = get_download_stats(conn)
    return {
        "ok": True,
        **stats,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


@app.get("/api/site/v1/download-preflight")
def download_preflight(platform: str):
    platform = platform.strip().lower()
    if platform not in {"android", "windows"}:
        raise HTTPException(status_code=400, detail="Platform tidak didukung.")

    settings = get_settings()

    with connect(settings.database_url) as conn:
        release = get_active_release(conn, platform)
        traffic = classify_traffic(count_recent_downloads(conn))

    if not release:
        raise HTTPException(status_code=404, detail="Paket belum tersedia.")

    relative = str(release["file_path"])
    if not relative.startswith("/downloads/"):
        raise HTTPException(status_code=503, detail="Metadata paket tidak valid.")

    package_path = settings.downloads_root / relative.removeprefix("/downloads/")
    if not package_path.is_file():
        raise HTTPException(status_code=404, detail="Paket belum tersedia.")

    if package_path.stat().st_size != int(release["file_size_bytes"]):
        raise HTTPException(status_code=503, detail="Ukuran paket tidak sesuai metadata.")

    stored_hash = str(release["sha256"] or "").lower()
    if len(stored_hash) != 64:
        raise HTTPException(status_code=503, detail="Metadata integritas belum tersedia.")

    actual_hash = sha256_file(package_path)
    if actual_hash != stored_hash:
        raise HTTPException(status_code=503, detail="Integritas paket tidak sesuai metadata.")

    nonce = uuid4()
    token = create_preflight_token(
        platform=platform,
        version=str(release["version"]),
        nonce=nonce,
        now=datetime.now(timezone.utc),
        secret=settings.hmac_secret,
        ttl_seconds=settings.token_ttl_seconds,
    )

    return {
        "ok": True,
        "platform": platform,
        "release": {
            "version": release["version"],
            "version_code": release["version_code"],
            "size_bytes": int(release["file_size_bytes"]),
            "integrity": "verified",
        },
        "server": {
            "status": _server_status(),
            "traffic": traffic,
        },
        "preflight_token": token,
        "expires_in_seconds": settings.token_ttl_seconds,
    }


@app.post("/api/site/v1/download-start")
def download_start(
    payload: DownloadStartInput,
    cf_country: str | None = Header(default=None, alias="CF-IPCountry"),
    cf_region: str | None = Header(default=None, alias="CF-Region"),
    cf_region_code: str | None = Header(default=None, alias="CF-Region-Code"),
    cf_city: str | None = Header(default=None, alias="CF-IPCity"),
):
    settings = get_settings()

    try:
        claims = verify_preflight_token(
            payload.preflight_token,
            now=datetime.now(timezone.utc),
            secret=settings.hmac_secret,
        )
    except TokenError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    location = _trusted_location(
        settings,
        cf_country=cf_country,
        cf_region=cf_region,
        cf_region_code=cf_region_code,
        cf_city=cf_city,
    )

    with connect(settings.database_url) as conn:
        release = get_active_release(conn, claims.platform)
        if not release or str(release["version"]) != claims.version:
            raise HTTPException(status_code=409, detail="Rilis telah berubah. Ulangi pemeriksaan.")

        status = _server_status()
        result = record_download_start(
            conn,
            preflight_nonce=claims.nonce,
            platform=claims.platform,
            release_version=claims.version,
            release_version_code=release["version_code"],
            device_type=payload.device_type,
            os_family=payload.os_family,
            os_version=payload.os_version,
            browser_family=payload.browser_family,
            browser_version=payload.browser_version,
            location=location,
            latency_ms=payload.latency_ms,
            estimated_mbps=payload.estimated_mbps,
            network_quality=payload.network_quality,
            server_status=status,
            client_timezone=payload.client_timezone,
            client_utc_offset_minutes=payload.client_utc_offset_minutes,
            preflight_duration_ms=payload.preflight_duration_ms,
            decision_delay_ms=payload.decision_delay_ms,
        )

    return {
        "ok": True,
        **result,
        "download_url": release["file_path"],
    }