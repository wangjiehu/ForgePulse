from __future__ import annotations

import json

import pytest

from forgepulse_api.services.case_loader import CaseValidationError, validate_case_directory
from forgepulse_api.services.diagnosis import build_diagnosis


INCOMPLETE_CASE = "coating_line_incomplete_evidence_004"
CONFLICT_CASE = "coating_line_conflicting_evidence_005"


def write_minimal_case(tmp_path, *, sensor_timestamp: str = "2026-01-01T00:00:00+08:00"):
    manifest = {
        "case_id": "temporary_validation_case",
        "title": "Temporary validation case",
        "industry": "battery manufacturing",
        "line": "test line",
        "station": "test station",
        "incident_window": {
            "start": "2026-01-01T00:00:00+08:00",
            "end": "2026-01-01T00:10:00+08:00",
        },
        "expected_sensor_fields": ["timestamp", "dryer_zone_2_temp_c"],
        "files": {
            "sensors": "sensor.csv",
            "alarms": "alarms.csv",
            "sop": "sop.md",
            "maintenance_records": "maintenance.md",
        },
    }
    (tmp_path / "case_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    (tmp_path / "sensor.csv").write_text(
        f"timestamp,dryer_zone_2_temp_c\n{sensor_timestamp},89.0\n",
        encoding="utf-8",
    )
    (tmp_path / "alarms.csv").write_text(
        "timestamp,alarm_code,severity,message,status\n"
        "2026-01-01T00:02:00+08:00,DRY-122,major,Deviation,active\n",
        encoding="utf-8",
    )
    (tmp_path / "sop.md").write_text("# SOP\n\n## Check\n\n1. Inspect sensor.\n", encoding="utf-8")
    (tmp_path / "maintenance.md").write_text(
        "# Maintenance\n\n## Record M-2026-001\n\nChecked sensor.\n",
        encoding="utf-8",
    )
    return manifest


def test_validate_case_directory_accepts_valid_case(tmp_path):
    write_minimal_case(tmp_path)
    result = validate_case_directory(tmp_path)
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_case_directory_rejects_invalid_timestamp(tmp_path):
    write_minimal_case(tmp_path, sensor_timestamp="not-a-timestamp")
    result = validate_case_directory(tmp_path)
    assert result["valid"] is False
    assert any("ISO-8601" in issue for issue in result["errors"])


def test_validate_case_directory_rejects_path_escape(tmp_path):
    manifest = write_minimal_case(tmp_path)
    manifest["files"]["sop"] = "../outside.md"
    (tmp_path / "case_manifest.json").write_text(json.dumps(manifest), encoding="utf-8")
    result = validate_case_directory(tmp_path)
    assert result["valid"] is False
    assert any("outside the case directory" in issue for issue in result["errors"])


def test_validate_case_directory_rejects_symbolic_links(tmp_path, monkeypatch):
    write_minimal_case(tmp_path)
    linked_file = tmp_path / "linked.txt"
    linked_file.write_text("external content", encoding="utf-8")
    original_is_symlink = type(linked_file).is_symlink
    monkeypatch.setattr(
        type(linked_file),
        "is_symlink",
        lambda self: self.name == "linked.txt" or original_is_symlink(self),
    )

    result = validate_case_directory(tmp_path)

    assert result["valid"] is False
    assert any("symbolic links" in issue for issue in result["errors"])


def test_diagnosis_preserves_structured_case_validation_error(monkeypatch):
    expected = CaseValidationError(["sensor CSV is missing required columns: timestamp"])
    monkeypatch.setattr(
        "forgepulse_api.services.diagnosis.load_case_manifest",
        lambda _case_id: (_ for _ in ()).throw(expected),
    )

    with pytest.raises(CaseValidationError) as captured:
        build_diagnosis("coating_line_dryer_tension_001")

    assert captured.value.issues == expected.issues


def test_incomplete_case_abstains_and_requests_data():
    diagnosis = build_diagnosis(INCOMPLETE_CASE)
    assert diagnosis.diagnosis_status == "insufficient_evidence"
    assert "dryer_zone_2_temp_c" in diagnosis.data_quality.missing_fields
    assert diagnosis.primary_root_cause.confidence <= 0.49
    assert "collect_data" in {action.type for action in diagnosis.recommended_actions}


def test_conflict_case_requires_verification():
    diagnosis = build_diagnosis(CONFLICT_CASE)
    assert diagnosis.diagnosis_status == "conflicting_evidence"
    assert diagnosis.conflicting_evidence
    assert diagnosis.primary_root_cause.confidence <= 0.59
    assert "verify" in {action.type for action in diagnosis.recommended_actions}


def test_diagnosis_output_is_deterministic():
    first = build_diagnosis("coating_line_dryer_tension_001").model_dump(mode="json")
    second = build_diagnosis("coating_line_dryer_tension_001").model_dump(mode="json")
    assert first == second
