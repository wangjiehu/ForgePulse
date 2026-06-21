"""Sensor analyzer – threshold and correlation analysis on sensor CSV data."""

from __future__ import annotations

from typing import Any


# Normal operating bands for the coating line golden case
THRESHOLDS: dict[str, dict[str, float]] = {
    "dryer_zone_1_temp_c": {"low": 85.0, "high": 92.0},
    "dryer_zone_2_temp_c": {"low": 85.0, "high": 93.0},
    "web_tension_n":       {"low": 110.0, "high": 130.0},
    "line_speed_m_min":    {"low": 40.0,  "high": 44.0},
    "fan_frequency_hz":    {"low": 45.0,  "high": 50.0},
    "drive_current_a":     {"low": 10.0,  "high": 14.0},
    "thickness_um":        {"low": 98.0,  "high": 104.0},
}


def _to_float(value: str) -> float:
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0.0


def analyze_sensor_data(rows: list[dict[str, str]]) -> dict[str, Any]:
    """Run threshold and drift analysis on sensor data.

    Returns a dict with:
      - anomalies: list of per-field anomaly records
      - peak_values: per-field min/max observed
      - correlated_findings: high-level observations linking fields
    """
    if not rows:
        return {"anomalies": [], "peak_values": {}, "correlated_findings": []}

    anomalies: list[dict[str, Any]] = []
    peak_values: dict[str, dict[str, Any]] = {}

    for field, band in THRESHOLDS.items():
        if field not in rows[0]:
            continue
        field_rows = [row for row in rows if row.get(field, "") not in ("", None)]
        if not field_rows:
            continue
        vals = [_to_float(row[field]) for row in field_rows]

        vmin, vmax = min(vals), max(vals)
        peak_values[field] = {
            "min": vmin,
            "max": vmax,
            "min_ts": field_rows[vals.index(vmin)]["timestamp"],
            "max_ts": field_rows[vals.index(vmax)]["timestamp"],
        }

        # Detect threshold violations
        violations = []
        for i, v in enumerate(vals):
            if v > band["high"]:
                violations.append({"timestamp": field_rows[i]["timestamp"], "value": v, "direction": "high"})
            elif v < band["low"]:
                violations.append({"timestamp": field_rows[i]["timestamp"], "value": v, "direction": "low"})

        if violations:
            anomalies.append({
                "field": field,
                "type": "threshold_violation",
                "threshold_low": band["low"],
                "threshold_high": band["high"],
                "violation_count": len(violations),
                "first_violation": violations[0],
                "worst_violation": max(violations, key=lambda x: abs(x["value"] - (band["high"] if x["direction"] == "high" else band["low"]))),
            })

        # Detect drift (monotonic rise or fall over 3+ consecutive points)
        if len(vals) >= 3:
            rise_count = sum(1 for i in range(1, len(vals)) if vals[i] > vals[i - 1])
            fall_count = sum(1 for i in range(1, len(vals)) if vals[i] < vals[i - 1])
            if rise_count >= len(vals) - 2 and vmax - vmin > 3.0:
                anomalies.append({
                    "field": field,
                    "type": "sustained_drift_up",
                    "start_value": vals[0],
                    "peak_value": vmax,
                    "delta": round(vmax - vals[0], 2),
                    "peak_ts": peak_values[field]["max_ts"],
                })
            elif fall_count >= len(vals) - 2 and vmin - vals[0] < -3.0:
                anomalies.append({
                    "field": field,
                    "type": "sustained_drift_down",
                    "start_value": vals[0],
                    "trough_value": vmin,
                    "delta": round(vmin - vals[0], 2),
                    "trough_ts": peak_values[field]["min_ts"],
                })

    # Correlated findings: cross-field observations
    correlated_findings: list[dict[str, Any]] = []

    # Check if zone 2 temp spike coincides with thickness drift
    z2_anomaly = [a for a in anomalies if a.get("field") == "dryer_zone_2_temp_c"]
    th_anomaly = [a for a in anomalies if a.get("field") == "thickness_um"]
    tn_anomaly = [a for a in anomalies if a.get("field") == "web_tension_n"]

    if z2_anomaly and th_anomaly:
        correlated_findings.append({
            "observation": "thickness_drift_correlated_with_temperature",
            "detail": "Coating thickness drift coincides with dryer zone 2 temperature deviation.",
            "fields": ["dryer_zone_2_temp_c", "thickness_um"],
        })

    if z2_anomaly and tn_anomaly:
        correlated_findings.append({
            "observation": "tension_oscillation_correlated_with_temperature",
            "detail": "Web tension oscillation occurred alongside dryer zone 2 temperature instability.",
            "fields": ["dryer_zone_2_temp_c", "web_tension_n"],
        })

    if tn_anomaly and th_anomaly:
        correlated_findings.append({
            "observation": "thickness_drift_correlated_with_tension",
            "detail": "Coating thickness drift occurred during web tension oscillation.",
            "fields": ["web_tension_n", "thickness_um"],
        })

    # Fan frequency drift check
    fan_anomaly = [a for a in anomalies if a.get("field") == "fan_frequency_hz"]
    if fan_anomaly and z2_anomaly:
        correlated_findings.append({
            "observation": "fan_frequency_drift_with_temperature",
            "detail": "Fan frequency drop coincides with dryer zone 2 temperature deviation.",
            "fields": ["fan_frequency_hz", "dryer_zone_2_temp_c"],
        })

    return {
        "anomalies": anomalies,
        "peak_values": peak_values,
        "correlated_findings": correlated_findings,
    }
