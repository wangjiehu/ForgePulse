"""Tests for ForgePulse diagnosis engine – verify evidence-backed root causes across all cases."""

from forgepulse_api.services.diagnosis import build_diagnosis
from forgepulse_api.services.case_loader import (
    load_case_manifest,
    load_sensor_readings,
    load_alarms,
    load_sop,
    load_maintenance_records,
    list_available_cases,
)
from forgepulse_api.services.sensor_analyzer import analyze_sensor_data
from forgepulse_api.services.alarm_parser import parse_alarms
from forgepulse_api.services.retriever import retrieve_relevant


CASE_1 = "coating_line_dryer_tension_001"
CASE_2 = "coating_line_airflow_002"
CASE_3 = "coating_line_drive_resistance_003"


# ── Case Loader ──────────────────────────────────────────────────────────────

class TestCaseLoader:
    def test_list_available_cases(self):
        cases = list_available_cases()
        assert CASE_1 in cases
        assert CASE_2 in cases
        assert CASE_3 in cases

    def test_load_manifest_case1(self):
        m = load_case_manifest(CASE_1)
        assert m["case_id"] == CASE_1
        assert "title" in m
        assert "files" in m

    def test_load_manifest_case2(self):
        m = load_case_manifest(CASE_2)
        assert m["case_id"] == CASE_2

    def test_load_manifest_case3(self):
        m = load_case_manifest(CASE_3)
        assert m["case_id"] == CASE_3

    def test_load_sensor_readings_case1(self):
        rows = load_sensor_readings(CASE_1)
        assert len(rows) > 0
        assert "timestamp" in rows[0]
        assert "dryer_zone_2_temp_c" in rows[0]

    def test_load_sensor_readings_case2(self):
        rows = load_sensor_readings(CASE_2)
        assert len(rows) > 0
        assert "fan_frequency_hz" in rows[0]

    def test_load_sensor_readings_case3(self):
        rows = load_sensor_readings(CASE_3)
        assert len(rows) > 0
        assert "drive_current_a" in rows[0]

    def test_load_alarms_case1(self):
        rows = load_alarms(CASE_1)
        assert len(rows) > 0
        assert "alarm_code" in rows[0]

    def test_load_alarms_case2(self):
        rows = load_alarms(CASE_2)
        assert len(rows) > 0

    def test_load_alarms_case3(self):
        rows = load_alarms(CASE_3)
        assert len(rows) > 0

    def test_load_sop_case1(self):
        text = load_sop(CASE_1)
        assert "DRY-122" in text
        assert "TEN-204" in text

    def test_load_sop_case2(self):
        text = load_sop(CASE_2)
        assert "AIR-305" in text

    def test_load_sop_case3(self):
        text = load_sop(CASE_3)
        assert "DRV-410" in text

    def test_load_maintenance_records_case1(self):
        text = load_maintenance_records(CASE_1)
        assert "M-2026-041" in text

    def test_load_maintenance_records_case2(self):
        text = load_maintenance_records(CASE_2)
        assert "M-2026-057" in text

    def test_load_maintenance_records_case3(self):
        text = load_maintenance_records(CASE_3)
        assert "M-2026-103" in text


# ── Sensor Analyzer ──────────────────────────────────────────────────────────

class TestSensorAnalyzer:
    def test_detects_zone2_anomaly(self):
        rows = load_sensor_readings(CASE_1)
        result = analyze_sensor_data(rows)
        fields = [a["field"] for a in result["anomalies"]]
        assert "dryer_zone_2_temp_c" in fields

    def test_detects_tension_anomaly(self):
        rows = load_sensor_readings(CASE_1)
        result = analyze_sensor_data(rows)
        fields = [a["field"] for a in result["anomalies"]]
        assert "web_tension_n" in fields

    def test_detects_thickness_drift(self):
        rows = load_sensor_readings(CASE_1)
        result = analyze_sensor_data(rows)
        fields = [a["field"] for a in result["anomalies"]]
        assert "thickness_um" in fields

    def test_correlated_findings(self):
        rows = load_sensor_readings(CASE_1)
        result = analyze_sensor_data(rows)
        obs = [f["observation"] for f in result["correlated_findings"]]
        assert any("temperature" in o for o in obs)
        assert any("thickness" in o or "tension" in o for o in obs)

    def test_case2_fan_anomaly(self):
        rows = load_sensor_readings(CASE_2)
        result = analyze_sensor_data(rows)
        fields = [a["field"] for a in result["anomalies"]]
        assert "fan_frequency_hz" in fields

    def test_case3_drive_anomaly(self):
        rows = load_sensor_readings(CASE_3)
        result = analyze_sensor_data(rows)
        fields = [a["field"] for a in result["anomalies"]]
        assert "drive_current_a" in fields


# ── Alarm Parser ─────────────────────────────────────────────────────────────

class TestAlarmParser:
    def test_parse_alarms_case1(self):
        rows = load_alarms(CASE_1)
        events = parse_alarms(rows)
        assert len(events) > 0
        codes = {e["alarm_code"] for e in events}
        assert "DRY-122" in codes
        assert "TEN-204" in codes
        assert "QCS-318" in codes

    def test_parse_alarms_case2(self):
        rows = load_alarms(CASE_2)
        events = parse_alarms(rows)
        assert len(events) > 0
        codes = {e["alarm_code"] for e in events}
        assert "AIR-305" in codes

    def test_parse_alarms_case3(self):
        rows = load_alarms(CASE_3)
        events = parse_alarms(rows)
        assert len(events) > 0
        codes = {e["alarm_code"] for e in events}
        assert "DRV-410" in codes

    def test_alarms_sorted_by_timestamp(self):
        rows = load_alarms(CASE_1)
        events = parse_alarms(rows)
        timestamps = [e["timestamp"] for e in events]
        assert timestamps == sorted(timestamps)


# ── Retriever ────────────────────────────────────────────────────────────────

class TestRetriever:
    def test_retrieve_sop_for_dry122(self):
        sop = load_sop(CASE_1)
        from forgepulse_api.services.retriever import retrieve_from_sop
        results = retrieve_from_sop(sop, ["DRY-122"])
        assert len(results) > 0
        assert any("DRY-122" in r["section_title"] or "DRY-122" in r["content"] for r in results)

    def test_retrieve_maintenance_m041(self):
        maint = load_maintenance_records(CASE_1)
        from forgepulse_api.services.retriever import retrieve_from_maintenance
        results = retrieve_from_maintenance(maint, ["DRY-122", "TEN-204"])
        assert len(results) > 0
        assert any("M-2026-041" in r["record_id"] for r in results)

    def test_retrieve_sop_for_air305(self):
        sop = load_sop(CASE_2)
        from forgepulse_api.services.retriever import retrieve_from_sop
        results = retrieve_from_sop(sop, ["AIR-305"])
        assert len(results) > 0

    def test_retrieve_sop_for_drv410(self):
        sop = load_sop(CASE_3)
        from forgepulse_api.services.retriever import retrieve_from_sop
        results = retrieve_from_sop(sop, ["DRV-410"])
        assert len(results) > 0


# ── Diagnosis – Case 1 ──────────────────────────────────────────────────────

class TestDiagnosisCase1:
    CASE = CASE_1

    def test_diagnosis_has_correct_case_id(self):
        d = build_diagnosis(self.CASE)
        assert d.case_id == self.CASE

    def test_root_cause_evidence_exists(self):
        d = build_diagnosis(self.CASE)
        evidence_ids = {ev.id for ev in d.evidence}
        for rc in d.root_cause_candidates:
            assert rc.evidence_ids, f"{rc.candidate_id} has no evidence"
            assert set(rc.evidence_ids).issubset(evidence_ids), (
                f"{rc.candidate_id} references missing evidence: "
                f"{set(rc.evidence_ids) - evidence_ids}"
            )

    def test_contains_dryer_zone2_root_cause(self):
        d = build_diagnosis(self.CASE)
        titles = " ".join(rc.title.lower() for rc in d.root_cause_candidates)
        assert "temperature control loop" in titles or "dryer zone 2" in titles

    def test_top_ranked_root_cause_is_dryer_zone2(self):
        d = build_diagnosis(self.CASE)
        assert d.root_cause_candidates
        top_title = d.root_cause_candidates[0].title.lower()
        assert "dryer" in top_title
        assert "temperature" in top_title

    def test_contains_tension_root_cause(self):
        d = build_diagnosis(self.CASE)
        titles = " ".join(rc.title.lower() for rc in d.root_cause_candidates)
        assert "tension" in titles

    def test_contains_thickness_drift_root_cause(self):
        d = build_diagnosis(self.CASE)
        titles = " ".join(rc.title.lower() for rc in d.downstream_effects)
        assert "thickness" in titles or "yield" in titles

    def test_evidence_includes_dry122(self):
        d = build_diagnosis(self.CASE)
        values = [ev.value for ev in d.evidence if ev.value]
        assert "DRY-122" in values

    def test_evidence_includes_ten204(self):
        d = build_diagnosis(self.CASE)
        values = [ev.value for ev in d.evidence if ev.value]
        assert "TEN-204" in values

    def test_evidence_includes_qcs318(self):
        d = build_diagnosis(self.CASE)
        values = [ev.value for ev in d.evidence if ev.value]
        assert "QCS-318" in values

    def test_evidence_includes_maintenance_m041(self):
        d = build_diagnosis(self.CASE)
        summaries = " ".join(ev.summary for ev in d.evidence)
        assert "M-2026-041" in summaries

    def test_timeline_has_events(self):
        d = build_diagnosis(self.CASE)
        assert len(d.timeline) >= 3

    def test_timeline_evidence_ids_valid(self):
        d = build_diagnosis(self.CASE)
        evidence_ids = {ev.id for ev in d.evidence}
        for evt in d.timeline:
            for eid in evt.evidence_ids:
                assert eid in evidence_ids, f"Timeline event references missing evidence {eid}"

    def test_work_order_exists(self):
        d = build_diagnosis(self.CASE)
        assert d.work_order_draft is not None
        assert len(d.work_order_draft.tasks) > 0

    def test_postmortem_exists(self):
        d = build_diagnosis(self.CASE)
        assert d.postmortem_summary
        assert len(d.postmortem_summary) > 20

    def test_limitations_exist(self):
        d = build_diagnosis(self.CASE)
        assert len(d.limitations) >= 2

    def test_recommended_actions_exist(self):
        d = build_diagnosis(self.CASE)
        assert len(d.recommended_actions) >= 2

    def test_score_breakdown_present(self):
        d = build_diagnosis(self.CASE)
        for rc in d.root_cause_candidates:
            assert rc.score_breakdown is not None
            assert rc.score_breakdown.total > 0

    def test_diagnostic_process_present(self):
        d = build_diagnosis(self.CASE)
        assert len(d.diagnostic_process) >= 3
        steps = [s.step for s in d.diagnostic_process]
        assert "Data Loading" in steps
        assert "Root Cause Ranking" in steps

    def test_evidence_links_present(self):
        d = build_diagnosis(self.CASE)
        assert len(d.evidence_links) > 0

    def test_data_quality_report(self):
        d = build_diagnosis(self.CASE)
        assert d.data_quality is not None
        assert d.data_quality.sensor_rows > 0
        assert d.data_quality.alarm_events > 0

    def test_value_estimates(self):
        d = build_diagnosis(self.CASE)
        assert len(d.value_estimates) >= 1


# ── Diagnosis – Case 2 ──────────────────────────────────────────────────────

class TestDiagnosisCase2:
    CASE = CASE_2

    def test_diagnosis_has_correct_case_id(self):
        d = build_diagnosis(self.CASE)
        assert d.case_id == self.CASE

    def test_root_cause_evidence_exists(self):
        d = build_diagnosis(self.CASE)
        evidence_ids = {ev.id for ev in d.evidence}
        for rc in d.root_cause_candidates:
            assert rc.evidence_ids, f"{rc.candidate_id} has no evidence"
            assert set(rc.evidence_ids).issubset(evidence_ids)

    def test_contains_fan_root_cause(self):
        d = build_diagnosis(self.CASE)
        titles = " ".join(rc.title.lower() for rc in d.root_cause_candidates)
        assert "fan" in titles or "airflow" in titles or "inverter" in titles

    def test_top_ranked_root_cause_is_airflow_frequency(self):
        d = build_diagnosis(self.CASE)
        assert d.root_cause_candidates
        top_title = d.root_cause_candidates[0].title.lower()
        assert "fan" in top_title
        assert "frequency" in top_title

    def test_evidence_includes_air305(self):
        d = build_diagnosis(self.CASE)
        values = [ev.value for ev in d.evidence if ev.value]
        assert "AIR-305" in values

    def test_evidence_includes_dry122(self):
        d = build_diagnosis(self.CASE)
        values = [ev.value for ev in d.evidence if ev.value]
        assert "DRY-122" in values

    def test_evidence_includes_maintenance_m057(self):
        d = build_diagnosis(self.CASE)
        summaries = " ".join(ev.summary for ev in d.evidence)
        assert "M-2026-057" in summaries

    def test_score_breakdown_present(self):
        d = build_diagnosis(self.CASE)
        for rc in d.root_cause_candidates:
            assert rc.score_breakdown is not None

    def test_diagnostic_process_present(self):
        d = build_diagnosis(self.CASE)
        assert len(d.diagnostic_process) >= 3

    def test_data_quality_report(self):
        d = build_diagnosis(self.CASE)
        assert d.data_quality is not None
        assert d.data_quality.sensor_rows > 0


# ── Diagnosis – Case 3 ──────────────────────────────────────────────────────

class TestDiagnosisCase3:
    CASE = CASE_3

    def test_diagnosis_has_correct_case_id(self):
        d = build_diagnosis(self.CASE)
        assert d.case_id == self.CASE

    def test_root_cause_evidence_exists(self):
        d = build_diagnosis(self.CASE)
        evidence_ids = {ev.id for ev in d.evidence}
        for rc in d.root_cause_candidates:
            assert rc.evidence_ids, f"{rc.candidate_id} has no evidence"
            assert set(rc.evidence_ids).issubset(evidence_ids)

    def test_contains_roller_root_cause(self):
        d = build_diagnosis(self.CASE)
        titles = " ".join(rc.title.lower() for rc in d.root_cause_candidates)
        assert "roller" in titles or "contamination" in titles or "drive" in titles

    def test_top_ranked_root_cause_is_drive_resistance(self):
        d = build_diagnosis(self.CASE)
        assert d.root_cause_candidates
        top_title = d.root_cause_candidates[0].title.lower()
        assert "drive" in top_title
        assert "resistance" in top_title

    def test_evidence_includes_drv410(self):
        d = build_diagnosis(self.CASE)
        values = [ev.value for ev in d.evidence if ev.value]
        assert "DRV-410" in values

    def test_evidence_includes_maintenance_m103(self):
        d = build_diagnosis(self.CASE)
        summaries = " ".join(ev.summary for ev in d.evidence)
        assert "M-2026-103" in summaries

    def test_score_breakdown_present(self):
        d = build_diagnosis(self.CASE)
        for rc in d.root_cause_candidates:
            assert rc.score_breakdown is not None

    def test_diagnostic_process_present(self):
        d = build_diagnosis(self.CASE)
        assert len(d.diagnostic_process) >= 3

    def test_data_quality_report(self):
        d = build_diagnosis(self.CASE)
        assert d.data_quality is not None
        assert d.data_quality.sensor_rows > 0
