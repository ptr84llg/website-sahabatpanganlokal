BEGIN;

CREATE SCHEMA IF NOT EXISTS site;

CREATE TABLE IF NOT EXISTS site.release_metadata (
    platform TEXT PRIMARY KEY CHECK (platform IN ('android', 'windows')),
    version TEXT NOT NULL,
    version_code INTEGER,
    file_path TEXT NOT NULL CHECK (file_path LIKE '/downloads/%'),
    file_size_bytes BIGINT NOT NULL CHECK (file_size_bytes > 0),
    sha256 TEXT NOT NULL CHECK (sha256 ~ '^[0-9a-fA-F]{64}$'),
    is_available BOOLEAN NOT NULL DEFAULT FALSE,
    published_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE TABLE IF NOT EXISTS site.download_events (
    download_id UUID PRIMARY KEY,
    preflight_nonce UUID NOT NULL UNIQUE,
    platform TEXT NOT NULL CHECK (platform IN ('android', 'windows')),
    release_version TEXT NOT NULL,
    release_version_code INTEGER,

    device_type TEXT NOT NULL CHECK (device_type IN ('mobile', 'tablet', 'desktop', 'unknown')),
    os_family TEXT NOT NULL,
    os_version TEXT,
    browser_family TEXT NOT NULL,
    browser_version TEXT,

    country_code TEXT,
    country_name TEXT,
    region TEXT,
    region_code TEXT,
    city TEXT,
    location_granularity TEXT NOT NULL
        CHECK (location_granularity IN ('city', 'region', 'country', 'unknown')),
    location_source TEXT NOT NULL,

    latency_ms INTEGER CHECK (latency_ms IS NULL OR latency_ms >= 0),
    estimated_mbps DOUBLE PRECISION
        CHECK (estimated_mbps IS NULL OR estimated_mbps >= 0),
    network_quality TEXT NOT NULL
        CHECK (network_quality IN ('excellent', 'good', 'fair', 'slow', 'unknown')),
    server_status TEXT NOT NULL
        CHECK (server_status IN ('normal', 'busy', 'high_load')),

    client_timezone TEXT,
    client_utc_offset_minutes INTEGER,
    preflight_duration_ms INTEGER NOT NULL CHECK (preflight_duration_ms >= 0),
    decision_delay_ms INTEGER NOT NULL CHECK (decision_delay_ms >= 0),

    started_at_server TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp(),
    created_at_server TIMESTAMPTZ NOT NULL DEFAULT clock_timestamp()
);

CREATE INDEX IF NOT EXISTS idx_download_events_started_at
    ON site.download_events (started_at_server DESC);

CREATE INDEX IF NOT EXISTS idx_download_events_platform
    ON site.download_events (platform);

CREATE INDEX IF NOT EXISTS idx_download_events_location
    ON site.download_events (country_code, region, city);

COMMIT;