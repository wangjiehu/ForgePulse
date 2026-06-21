"""Alarm parser – parse alarm CSV into structured events."""

from __future__ import annotations

from typing import Any


def parse_alarms(alarm_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    """Convert raw alarm CSV rows into structured alarm events.

    Returns a list of dicts with keys:
      - alarm_code, severity, message, status, timestamp
    """
    events: list[dict[str, Any]] = []
    for row in alarm_rows:
        code = row.get("alarm_code", "").strip()
        if not code:
            continue
        events.append({
            "alarm_code": code,
            "severity": row.get("severity", "info").strip(),
            "message": row.get("message", "").strip(),
            "status": row.get("status", "unknown").strip(),
            "timestamp": row.get("timestamp", "").strip(),
        })
    # Sort by timestamp
    events.sort(key=lambda e: e["timestamp"])
    return events


def get_alarm_by_code(events: list[dict[str, Any]], code: str) -> list[dict[str, Any]]:
    """Filter alarm events by alarm code."""
    return [e for e in events if e["alarm_code"] == code]
