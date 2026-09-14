from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class DownloadStartInput(StrictModel):
    preflight_token: str = Field(min_length=20, max_length=4096)
    device_type: str = Field(min_length=1, max_length=24)
    os_family: str = Field(min_length=1, max_length=80)
    os_version: str | None = Field(default=None, max_length=40)
    browser_family: str = Field(min_length=1, max_length=80)
    browser_version: str | None = Field(default=None, max_length=40)
    latency_ms: int | None = Field(default=None, ge=0, le=120000)
    estimated_mbps: float | None = Field(default=None, ge=0, le=100000)
    network_quality: str = Field(pattern="^(excellent|good|fair|slow|unknown)$")
    client_timezone: str | None = Field(default=None, max_length=80)
    client_utc_offset_minutes: int | None = Field(default=None, ge=-840, le=840)
    preflight_duration_ms: int = Field(ge=0, le=120000)
    decision_delay_ms: int = Field(ge=0, le=3600000)