from __future__ import annotations

from typing import Literal

TrafficStatus = Literal["low", "moderate", "high"]
ServerStatus = Literal["normal", "busy", "high_load"]


def classify_traffic(count_last_5m: int) -> TrafficStatus:
    if count_last_5m >= 50:
        return "high"
    if count_last_5m >= 10:
        return "moderate"
    return "low"


def classify_server_status(
    load_ratio: float,
    available_memory_ratio: float,
    api_p95_ms: float,
) -> ServerStatus:
    if (
        load_ratio > 0.90
        or available_memory_ratio < 0.15
        or api_p95_ms > 1000
    ):
        return "high_load"

    if (
        load_ratio >= 0.60
        or available_memory_ratio <= 0.30
        or api_p95_ms >= 500
    ):
        return "busy"

    return "normal"