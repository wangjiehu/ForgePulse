"""Retriever – keyword-based retrieval from SOP and maintenance records."""

from __future__ import annotations

import re
from typing import Any


def retrieve_from_sop(sop_text: str, keywords: list[str], source_name: str = "sop") -> list[dict[str, Any]]:
    """Retrieve relevant SOP sections matching any of the keywords.

    Returns list of dicts with:
      - source, section_title, content, matched_keywords
    """
    results: list[dict[str, Any]] = []
    # Split SOP into sections by ## headers
    sections = re.split(r"(?=^## )", sop_text, flags=re.MULTILINE)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        # Extract section title
        title_match = re.match(r"^## (.+)", section)
        title = title_match.group(1).strip() if title_match else "Overview"
        # Check keyword match (case-insensitive)
        section_lower = section.lower()
        matched = [kw for kw in keywords if kw.lower() in section_lower]
        if matched:
            results.append({
                "source": source_name,
                "section_title": title,
                "content": section,
                "matched_keywords": matched,
            })
    return results


def retrieve_from_maintenance(records_text: str, keywords: list[str]) -> list[dict[str, Any]]:
    """Retrieve relevant maintenance record sections matching any of the keywords.

    Returns list of dicts with:
      - source, record_id, content, matched_keywords
    """
    results: list[dict[str, Any]] = []
    # Split by ## Record markers
    sections = re.split(r"(?=^## Record )", records_text, flags=re.MULTILINE)
    for section in sections:
        section = section.strip()
        if not section:
            continue
        # Extract record ID
        id_match = re.match(r"^## Record (M-\d+-\d+)", section)
        record_id = id_match.group(1) if id_match else "unknown"
        # Check keyword match
        section_lower = section.lower()
        matched = [kw for kw in keywords if kw.lower() in section_lower]
        if matched:
            results.append({
                "source": "maintenance_records.md",
                "record_id": record_id,
                "content": section,
                "matched_keywords": matched,
            })
    return results


def retrieve_relevant(
    sop_text: str,
    maintenance_text: str,
    alarm_codes: list[str],
    anomaly_fields: list[str],
    sop_source_name: str = "sop",
) -> dict[str, list[dict[str, Any]]]:
    """Retrieve relevant SOP and maintenance record sections based on alarms and anomalies.

    Args:
        sop_text: Full SOP markdown text.
        maintenance_text: Full maintenance records markdown text.
        alarm_codes: List of alarm codes observed.
        anomaly_fields: List of sensor field names with anomalies.
        sop_source_name: Source filename for SOP evidence.
    """
    # Build keyword list from alarm codes and anomaly fields
    field_keywords: dict[str, list[str]] = {
        "dryer_zone_1_temp_c": ["temperature", "DRY-110", "zone 1", "dryer"],
        "dryer_zone_2_temp_c": ["temperature", "DRY-122", "zone 2", "dryer"],
        "web_tension_n": ["tension", "TEN-204", "web"],
        "thickness_um": ["thickness", "drift", "QCS-318", "coating"],
        "fan_frequency_hz": ["fan", "frequency", "airflow", "AIR-305"],
        "drive_current_a": ["drive", "current", "DRV-410", "roller"],
    }
    keywords: list[str] = list(alarm_codes)
    for field in anomaly_fields:
        keywords.extend(field_keywords.get(field, [field]))

    # Deduplicate while preserving order
    seen: set[str] = set()
    unique_kw: list[str] = []
    for kw in keywords:
        if kw.lower() not in seen:
            seen.add(kw.lower())
            unique_kw.append(kw)

    sop_matches = retrieve_from_sop(sop_text, unique_kw, sop_source_name)
    maintenance_matches = retrieve_from_maintenance(maintenance_text, unique_kw)

    return {
        "sop_matches": sop_matches,
        "maintenance_matches": maintenance_matches,
    }
