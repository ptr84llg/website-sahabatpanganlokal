from __future__ import annotations

from dataclasses import dataclass
from uuid import UUID, uuid4

import psycopg
from psycopg.rows import dict_row


@dataclass(frozen=True)
class CoarseLocation:
    country_code: str | None
    country_name: str | None
    region: str | None
    region_code: str | None
    city: str | None
    granularity: str
    source: str


def connect(database_url: str):
    return psycopg.connect(database_url, row_factory=dict_row)


def get_download_stats(conn) -> dict:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
              COUNT(*) FILTER (WHERE platform = 'android') AS android,
              COUNT(*) FILTER (WHERE platform = 'windows') AS windows,
              COUNT(*) AS total
            FROM site.download_events
            """
        )
        row = cur.fetchone()
    return {
        "android": int(row["android"] or 0),
        "windows": int(row["windows"] or 0),
        "total": int(row["total"] or 0),
    }


def count_recent_downloads(conn) -> int:
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT COUNT(*)
            FROM site.download_events
            WHERE started_at_server >= clock_timestamp() - interval '5 minutes'
            """
        )
        return int(cur.fetchone()["count"])


def get_active_release(conn, platform: str):
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT platform, version, version_code, file_path, file_size_bytes,
                   sha256, is_available, published_at, updated_at
            FROM site.release_metadata
            WHERE platform = %s AND is_available = TRUE
            """,
            (platform,),
        )
        return cur.fetchone()


def record_download_start(
    conn,
    *,
    preflight_nonce: UUID,
    platform: str,
    release_version: str,
    release_version_code: int | None,
    device_type: str,
    os_family: str,
    os_version: str | None,
    browser_family: str,
    browser_version: str | None,
    location: CoarseLocation,
    latency_ms: int | None,
    estimated_mbps: float | None,
    network_quality: str,
    server_status: str,
    client_timezone: str | None,
    client_utc_offset_minutes: int | None,
    preflight_duration_ms: int,
    decision_delay_ms: int,
):
    download_id = uuid4()

    with conn.transaction():
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO site.download_events (
                    download_id, preflight_nonce, platform,
                    release_version, release_version_code,
                    device_type, os_family, os_version,
                    browser_family, browser_version,
                    country_code, country_name, region, region_code, city,
                    location_granularity, location_source,
                    latency_ms, estimated_mbps, network_quality, server_status,
                    client_timezone, client_utc_offset_minutes,
                    preflight_duration_ms, decision_delay_ms
                )
                VALUES (
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s
                )
                ON CONFLICT (preflight_nonce) DO NOTHING
                RETURNING download_id, started_at_server
                """,
                (
                    download_id,
                    preflight_nonce,
                    platform,
                    release_version,
                    release_version_code,
                    device_type,
                    os_family,
                    os_version,
                    browser_family,
                    browser_version,
                    location.country_code,
                    location.country_name,
                    location.region,
                    location.region_code,
                    location.city,
                    location.granularity,
                    location.source,
                    latency_ms,
                    estimated_mbps,
                    network_quality,
                    server_status,
                    client_timezone,
                    client_utc_offset_minutes,
                    preflight_duration_ms,
                    decision_delay_ms,
                ),
            )
            inserted = cur.fetchone()

            if inserted:
                return {
                    "status": "recorded",
                    "download_id": str(inserted["download_id"]),
                    "started_at": inserted["started_at_server"],
                }

            cur.execute(
                """
                SELECT download_id, started_at_server
                FROM site.download_events
                WHERE preflight_nonce = %s
                """,
                (preflight_nonce,),
            )
            existing = cur.fetchone()

    return {
        "status": "already_recorded",
        "download_id": str(existing["download_id"]),
        "started_at": existing["started_at_server"],
    }