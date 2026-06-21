"""Case loader – reads case_manifest, sensor CSV, alarm CSV, SOP and maintenance records."""

from __future__ import annotations

import csv
import json
import math
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[4]
SAMPLE_ROOT = PROJECT_ROOT / "data" / "samples"

# Cache: case_id -> directory Path
_case_dir_cache: dict[str, Path] | None = None

SENSOR_REQUIRED_BASE = {"timestamp"}
ALARM_REQUIRED_FIELDS = {"timestamp", "alarm_code", "severity", "message", "status"}
CASE_ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9_-]{2,79}$")


class CaseValidationError(ValueError):
    """Raised when a case cannot be safely loaded."""

    def __init__(self, issues: list[str]):
        self.issues = issues
        super().__init__("; ".join(issues))


def reset_case_cache() -> None:
    """Clear the manifest-to-directory cache after importing a case."""
    global _case_dir_cache
    _case_dir_cache = None


def _parse_iso_timestamp(value: str, label: str, issues: list[str]) -> datetime | None:
    try:
        return datetime.fromisoformat(value)
    except (TypeError, ValueError):
        issues.append(f"{label} must be an ISO-8601 timestamp: {value!r}")
        return None


def _resolve_case_file(case_dir: Path, filename: str, label: str, issues: list[str]) -> Path | None:
    if not isinstance(filename, str) or not filename.strip():
        issues.append(f"{label} must reference a non-empty relative path")
        return None
    candidate = (case_dir / filename).resolve()
    case_root = case_dir.resolve()
    if candidate != case_root and case_root not in candidate.parents:
        issues.append(f"{label} points outside the case directory: {filename}")
        return None
    if not candidate.is_file():
        issues.append(f"{label} references a missing file: {filename}")
        return None
    return candidate


def _read_csv(path: Path, label: str, issues: list[str]) -> tuple[list[dict[str, str]], list[str]]:
    try:
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            fields = list(reader.fieldnames or [])
            rows = [dict(row) for row in reader]
    except (OSError, UnicodeError, csv.Error) as exc:
        issues.append(f"{label} could not be read: {exc}")
        return [], []
    if not fields:
        issues.append(f"{label} has no header row")
    if not rows:
        issues.append(f"{label} has no data rows")
    return rows, fields


def validate_case_directory(case_dir: Path) -> dict[str, Any]:
    """Validate a case directory without registering or diagnosing it."""
    case_dir = case_dir.resolve()
    errors: list[str] = []
    warnings: list[str] = []
    manifest_path = case_dir / "case_manifest.json"

    try:
        linked_entries = sorted(
            str(path.relative_to(case_dir))
            for path in case_dir.rglob("*")
            if path.is_symlink()
        )
    except OSError as exc:
        errors.append(f"case directory could not be inspected safely: {exc}")
        linked_entries = []
    if linked_entries:
        errors.append(
            "case directory must not contain symbolic links: "
            + ", ".join(linked_entries)
        )

    if not manifest_path.is_file():
        errors.append("case_manifest.json is missing")
        return {"valid": False, "errors": errors, "warnings": []}

    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return {"valid": False, "errors": [f"case_manifest.json is invalid: {exc}"], "warnings": []}

    required_manifest_fields = ["case_id", "title", "industry", "line", "station", "incident_window", "files"]
    for field in required_manifest_fields:
        if field not in manifest:
            errors.append(f"manifest is missing required field: {field}")

    case_id = manifest.get("case_id")
    if not isinstance(case_id, str) or not CASE_ID_PATTERN.fullmatch(case_id):
        errors.append("case_id must contain only lowercase letters, digits, hyphens, or underscores")

    window = manifest.get("incident_window")
    start_dt = end_dt = None
    if not isinstance(window, dict):
        errors.append("incident_window must be an object")
    else:
        start_dt = _parse_iso_timestamp(window.get("start", ""), "incident_window.start", errors)
        end_dt = _parse_iso_timestamp(window.get("end", ""), "incident_window.end", errors)
        if start_dt and end_dt and start_dt >= end_dt:
            errors.append("incident_window.start must be earlier than incident_window.end")

    files = manifest.get("files")
    resolved_files: dict[str, Path] = {}
    if not isinstance(files, dict):
        errors.append("files must be an object")
    else:
        for key in ["sensors", "alarms", "sop", "maintenance_records"]:
            path = _resolve_case_file(case_dir, files.get(key, ""), f"files.{key}", errors)
            if path:
                resolved_files[key] = path

    sensor_rows: list[dict[str, str]] = []
    sensor_fields: list[str] = []
    if "sensors" in resolved_files:
        sensor_rows, sensor_fields = _read_csv(resolved_files["sensors"], "sensor CSV", errors)
        missing_base = sorted(SENSOR_REQUIRED_BASE.difference(sensor_fields))
        if missing_base:
            errors.append(f"sensor CSV is missing required columns: {', '.join(missing_base)}")

        expected_fields = set(manifest.get("expected_sensor_fields", []))
        missing_expected = sorted(expected_fields.difference(sensor_fields))
        if missing_expected:
            warnings.append(f"expected sensor evidence is missing: {', '.join(missing_expected)}")

        timestamps: list[datetime] = []
        for index, row in enumerate(sensor_rows, 2):
            parsed = _parse_iso_timestamp(row.get("timestamp", ""), f"sensor row {index} timestamp", errors)
            if parsed:
                timestamps.append(parsed)
            for field, raw_value in row.items():
                if field == "timestamp" or raw_value in (None, ""):
                    continue
                try:
                    value = float(raw_value)
                    if not math.isfinite(value):
                        raise ValueError
                except ValueError:
                    errors.append(f"sensor row {index} field {field} must be a finite number")
        if timestamps and timestamps != sorted(timestamps):
            errors.append("sensor timestamps must be sorted in ascending order")
        if len(timestamps) != len(set(timestamps)):
            errors.append("sensor timestamps must not contain duplicates")

    alarm_rows: list[dict[str, str]] = []
    alarm_fields: list[str] = []
    if "alarms" in resolved_files:
        alarm_rows, alarm_fields = _read_csv(resolved_files["alarms"], "alarm CSV", errors)
        missing_alarm = sorted(ALARM_REQUIRED_FIELDS.difference(alarm_fields))
        if missing_alarm:
            errors.append(f"alarm CSV is missing required columns: {', '.join(missing_alarm)}")
        alarm_timestamps: list[datetime] = []
        for index, row in enumerate(alarm_rows, 2):
            parsed = _parse_iso_timestamp(row.get("timestamp", ""), f"alarm row {index} timestamp", errors)
            if parsed:
                alarm_timestamps.append(parsed)
                if start_dt and end_dt and not (start_dt <= parsed <= end_dt):
                    warnings.append(f"alarm row {index} is outside the incident window")
            if not row.get("alarm_code", "").strip():
                errors.append(f"alarm row {index} has an empty alarm_code")
        if alarm_timestamps and alarm_timestamps != sorted(alarm_timestamps):
            errors.append("alarm timestamps must be sorted in ascending order")

    for key in ["sop", "maintenance_records"]:
        path = resolved_files.get(key)
        if path and not path.read_text(encoding="utf-8").strip():
            warnings.append(f"{key} document is empty")

    return {
        "valid": not errors,
        "errors": errors,
        "warnings": list(dict.fromkeys(warnings)),
        "manifest": manifest,
        "sensor_rows": len(sensor_rows),
        "alarm_rows": len(alarm_rows),
        "sensor_fields": sensor_fields,
        "alarm_fields": alarm_fields,
    }


def import_case_directory(source_dir: Path, replace: bool = False) -> str:
    """Validate and copy a case directory into the local sample registry."""
    source_dir = source_dir.resolve()
    result = validate_case_directory(source_dir)
    if not result["valid"]:
        raise CaseValidationError(result["errors"])

    case_id = result["manifest"]["case_id"]
    destination = (SAMPLE_ROOT / case_id).resolve()
    sample_root = SAMPLE_ROOT.resolve()
    if sample_root not in destination.parents:
        raise CaseValidationError(["destination would be outside the sample registry"])
    if destination.exists():
        if not replace:
            raise FileExistsError(f"Case '{case_id}' already exists")
        shutil.rmtree(destination)
    shutil.copytree(source_dir, destination)
    reset_case_cache()
    return case_id


def _build_case_dir_cache() -> dict[str, Path]:
    """Scan SAMPLE_ROOT subdirectories and map case_id -> Path via manifest."""
    global _case_dir_cache
    if _case_dir_cache is not None:
        return _case_dir_cache
    cache: dict[str, Path] = {}
    if not SAMPLE_ROOT.is_dir():
        _case_dir_cache = cache
        return cache
    for d in SAMPLE_ROOT.iterdir():
        if not d.is_dir():
            continue
        manifest_path = d / "case_manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, encoding="utf-8") as f:
                    manifest = json.load(f)
                case_id = manifest.get("case_id", "")
                if case_id:
                    cache[case_id] = d
            except (json.JSONDecodeError, OSError):
                pass
    _case_dir_cache = cache
    return cache


def get_case_dir(case_id: str) -> Path:
    """Return the directory for a given case_id, or raise FileNotFoundError."""
    cache = _build_case_dir_cache()
    if case_id not in cache:
        available = ", ".join(sorted(cache.keys())) if cache else "none"
        raise FileNotFoundError(
            f"Case '{case_id}' not found. Available cases: {available}"
        )
    return cache[case_id]


def load_case_manifest(case_id: str) -> dict[str, Any]:
    """Load and validate a case manifest JSON file."""
    d = get_case_dir(case_id)
    result = validate_case_directory(d)
    if not result["valid"]:
        raise CaseValidationError(result["errors"])
    manifest = result["manifest"]
    if manifest["case_id"] != case_id:
        raise CaseValidationError([f"manifest case_id '{manifest['case_id']}' does not match requested id '{case_id}'"])
    return manifest


def load_sensor_readings(case_id: str) -> list[dict[str, str]]:
    """Load sensor CSV data as list of dicts."""
    manifest = load_case_manifest(case_id)
    filename = manifest["files"]["sensors"]
    path = get_case_dir(case_id) / filename

    rows: list[dict[str, str]] = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))

    if not rows:
        raise ValueError(f"Sensor CSV for case '{case_id}' is empty")

    return rows


def load_alarms(case_id: str) -> list[dict[str, str]]:
    """Load alarm CSV data as list of dicts."""
    manifest = load_case_manifest(case_id)
    filename = manifest["files"]["alarms"]
    path = get_case_dir(case_id) / filename

    rows: list[dict[str, str]] = []
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))

    if not rows:
        raise ValueError(f"Alarm CSV for case '{case_id}' is empty")

    return rows


def load_sop(case_id: str) -> str:
    """Load SOP markdown text."""
    manifest = load_case_manifest(case_id)
    filename = manifest["files"]["sop"]
    path = get_case_dir(case_id) / filename
    return path.read_text(encoding="utf-8")


def load_maintenance_records(case_id: str) -> str:
    """Load maintenance records markdown text."""
    manifest = load_case_manifest(case_id)
    filename = manifest["files"]["maintenance_records"]
    path = get_case_dir(case_id) / filename
    return path.read_text(encoding="utf-8")


def list_available_cases() -> list[str]:
    """Return list of case_ids that have a case_manifest.json."""
    cache = _build_case_dir_cache()
    return sorted(cache.keys())
