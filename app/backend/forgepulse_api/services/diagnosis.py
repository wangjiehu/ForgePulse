"""Diagnosis engine – data-driven, fault-mode-matched, with score breakdown and process trace."""

from __future__ import annotations

import json
import re
from pathlib import Path

from forgepulse_api.schemas import (
    Diagnosis,
    Evidence,
    EvidenceLink,
    RecommendedAction,
    RootCauseCandidate,
    ScoreBreakdown,
    TimelineEvent,
    WorkOrderDraft,
    ProcessStep,
    DataQualityReport,
    ValueEstimate,
    AgentDecision,
)
from forgepulse_api.services.case_loader import (
    CaseValidationError,
    load_case_manifest,
    load_sensor_readings,
    load_alarms,
    load_maintenance_records,
    load_sop,
)
from forgepulse_api.services.model_provider import get_model_provider
from forgepulse_api.services.alarm_parser import parse_alarms
from forgepulse_api.services.sensor_analyzer import analyze_sensor_data
from forgepulse_api.services.retriever import retrieve_relevant


PROJECT_ROOT = Path(__file__).resolve().parents[4]
FAULT_MODES_PATH = PROJECT_ROOT / "data" / "fault_modes.json"


def _load_fault_modes() -> list[dict]:
    """Load fault mode definitions."""
    if FAULT_MODES_PATH.exists():
        with open(FAULT_MODES_PATH, encoding="utf-8") as f:
            return json.load(f).get("fault_modes", [])
    return []


def _build_evidence(
    alarm_events: list[dict],
    sensor_results: dict,
    retrieval: dict,
) -> list[Evidence]:
    """Build evidence list from alarms, sensor analysis, and retrieval results."""
    evidence_list: list[Evidence] = []
    ev_counter = 0

    def next_id() -> str:
        nonlocal ev_counter
        ev_counter += 1
        return f"EV-{ev_counter:03d}"

    # Alarm-based evidence
    for event in alarm_events:
        code = event["alarm_code"]
        evidence_list.append(Evidence(
            id=next_id(),
            source="alarms.csv",
            timestamp=event["timestamp"],
            summary=f"{code} {event['severity']} alarm: {event['message']}",
            value=code,
        ))

    # Sensor anomaly evidence
    for anomaly in sensor_results.get("anomalies", []):
        field = anomaly["field"]
        atype = anomaly["type"]
        if atype == "threshold_violation":
            worst = anomaly["worst_violation"]
            direction_text = "above" if worst["direction"] == "high" else "below"
            evidence_list.append(Evidence(
                id=next_id(),
                source="sensor_readings.csv",
                timestamp=worst["timestamp"],
                field=field,
                value=f"{worst['value']}",
                summary=f"{field} {direction_text} threshold at {worst['value']}",
            ))
        elif atype == "sustained_drift_up":
            evidence_list.append(Evidence(
                id=next_id(),
                source="sensor_readings.csv",
                timestamp=anomaly["peak_ts"],
                field=field,
                value=f"{anomaly['peak_value']}",
                summary=f"{field} sustained upward drift, peak {anomaly['peak_value']} (Δ+{anomaly['delta']})",
            ))
        elif atype == "sustained_drift_down":
            evidence_list.append(Evidence(
                id=next_id(),
                source="sensor_readings.csv",
                timestamp=anomaly["trough_ts"],
                field=field,
                value=f"{anomaly['trough_value']}",
                summary=f"{field} sustained downward drift, trough {anomaly['trough_value']} (Δ{anomaly['delta']})",
            ))

    # SOP match evidence – use actual filename from retrieval
    for match in retrieval.get("sop_matches", []):
        title = match["section_title"]
        source = match.get("source", "sop")
        evidence_list.append(Evidence(
            id=next_id(),
            source=source,
            summary=f"SOP section '{title}' is relevant to observed anomalies.",
        ))

    # Maintenance record evidence
    for match in retrieval.get("maintenance_matches", []):
        rid = match["record_id"]
        lines = match["content"].strip().split("\n")
        summary_line = ""
        for line in lines[1:]:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                summary_line = stripped
                break
        evidence_list.append(Evidence(
            id=next_id(),
            source="maintenance_records.md",
            summary=f"Maintenance record {rid}: {summary_line}",
            value=rid,
        ))

    return evidence_list


def _build_timeline(
    alarm_events: list[dict],
    sensor_results: dict,
    evidence_list: list[Evidence],
) -> list[TimelineEvent]:
    """Build timeline from alarm events and sensor anomalies."""
    ev_by_source_value: dict[str, str] = {}
    for ev in evidence_list:
        key_parts = [ev.source]
        if ev.value:
            key_parts.append(ev.value)
        if ev.timestamp:
            key_parts.append(ev.timestamp)
        if len(key_parts) > 1:
            ev_by_source_value["|".join(key_parts)] = ev.id

    def _find_ev_ids(source: str, value: str = "", timestamp: str = "") -> list[str]:
        key = f"{source}|{value}|{timestamp}"
        if key in ev_by_source_value:
            return [ev_by_source_value[key]]
        ids = []
        for k, vid in ev_by_source_value.items():
            parts = k.split("|")
            if parts[0] != source:
                continue
            if value and (len(parts) < 2 or parts[1] != value):
                continue
            if timestamp and parts[-1] != timestamp:
                continue
            ids.append(vid)
        return ids

    timeline: list[TimelineEvent] = []

    # Alarm events
    for event in alarm_events:
        code = event["alarm_code"]
        sev = severity_label(event.get("severity", "info"))
        timeline.append(TimelineEvent(
            timestamp=event["timestamp"],
            title=f"Alarm {code}",
            detail=f"{event['severity'].capitalize()}: {event['message']} (status: {event['status']})",
            severity=sev,
            evidence_ids=_find_ev_ids("alarms.csv", code, event["timestamp"]),
        ))

    # Sensor anomaly events
    for anomaly in sensor_results.get("anomalies", []):
        field = anomaly["field"]
        atype = anomaly["type"]
        if atype == "threshold_violation":
            worst = anomaly["worst_violation"]
            ts = worst["timestamp"]
            direction = "exceeded" if worst["direction"] == "high" else "fell below"
            timeline.append(TimelineEvent(
                timestamp=ts,
                title=f"{field} threshold violation",
                detail=f"{field} {direction} threshold at {worst['value']}.",
                severity="major",
                evidence_ids=_find_ev_ids("sensor_readings.csv", "", ts),
            ))
        elif atype == "sustained_drift_up":
            ts = anomaly["peak_ts"]
            timeline.append(TimelineEvent(
                timestamp=ts,
                title=f"{field} reached peak",
                detail=f"{field} drifted upward to {anomaly['peak_value']} (Δ+{anomaly['delta']}).",
                severity="major",
                evidence_ids=_find_ev_ids("sensor_readings.csv", "", ts),
            ))
        elif atype == "sustained_drift_down":
            ts = anomaly["trough_ts"]
            timeline.append(TimelineEvent(
                timestamp=ts,
                title=f"{field} reached trough",
                detail=f"{field} drifted downward to {anomaly['trough_value']} (Δ{anomaly['delta']}).",
                severity="major",
                evidence_ids=_find_ev_ids("sensor_readings.csv", "", ts),
            ))

    timeline.sort(key=lambda e: e.timestamp)
    return timeline


def _compute_score(
    fault_mode: dict,
    alarm_codes: list[str],
    anomaly_fields: list[str],
    sop_match_count: int,
    maint_match_count: int,
    operator_note: str,
) -> ScoreBreakdown:
    """Compute root cause score breakdown per the AGENT_WORKFLOW formula."""
    fm_alarms = set(fault_mode.get("primary_alarm_codes") or fault_mode.get("related_alarm_codes", []))
    fm_fields = set(fault_mode.get("primary_sensor_fields") or fault_mode.get("related_sensor_fields", []))

    # alarm_match: fraction of primary fault-mode alarms present.
    if fm_alarms:
        alarm_match = len(fm_alarms.intersection(alarm_codes)) / len(fm_alarms)
    else:
        alarm_match = 0.0

    # sensor_correlation: fraction of primary fault-mode sensor fields with anomalies.
    if fm_fields:
        sensor_correlation = len(fm_fields.intersection(anomaly_fields)) / len(fm_fields)
    else:
        sensor_correlation = 0.0

    # sop_match: 1.0 if any SOP section matched, 0.0 otherwise
    sop_match = min(1.0, sop_match_count * 0.5)

    # maintenance_similarity: 1.0 if any maintenance record matched, 0.0 otherwise
    maintenance_similarity = min(1.0, maint_match_count * 0.5)

    # operator_note_match: token overlap with the title, symptoms, and causes.
    note_lower = operator_note.lower()
    keyword_text = " ".join(
        [fault_mode.get("title", ""), fault_mode.get("category", "")]
        + fault_mode.get("typical_symptoms", [])
        + fault_mode.get("common_causes", [])
    ).lower()
    keywords = {
        token
        for token in re.findall(r"[a-z0-9]+", keyword_text)
        if len(token) > 2 and token not in {"and", "the", "with", "from", "due", "for"}
    }
    note_tokens = set(re.findall(r"[a-z0-9]+", note_lower))
    if keywords and note_tokens:
        operator_note_match = len(keywords.intersection(note_tokens)) / len(keywords)
    else:
        operator_note_match = 0.0

    total = (
        alarm_match * 0.30
        + sensor_correlation * 0.25
        + sop_match * 0.20
        + maintenance_similarity * 0.15
        + operator_note_match * 0.10
    )

    diagnostic_role = fault_mode.get("diagnostic_role", "equipment_cause")
    if diagnostic_role == "quality_effect":
        total = min(total, 0.74)
    elif diagnostic_role == "coupled_secondary_factor":
        total = min(total, 0.82)

    return ScoreBreakdown(
        alarm_match=round(alarm_match, 3),
        sensor_correlation=round(sensor_correlation, 3),
        sop_match=round(sop_match, 3),
        maintenance_similarity=round(maintenance_similarity, 3),
        operator_note_match=round(operator_note_match, 3),
        total=round(total, 3),
    )


def _candidate_retrieval_matches(fault_mode: dict, retrieval: dict) -> tuple[list[dict], list[dict]]:
    """Return only SOP and maintenance matches relevant to one fault mode."""
    exact_identifiers = {
        value.lower()
        for value in (
            fault_mode.get("related_alarm_codes", [])
            + fault_mode.get("primary_alarm_codes", [])
            + fault_mode.get("related_sensor_fields", [])
            + fault_mode.get("primary_sensor_fields", [])
        )
    }
    semantic_text = " ".join(
        [fault_mode.get("title", ""), fault_mode.get("category", "")]
        + fault_mode.get("typical_symptoms", [])
        + fault_mode.get("common_causes", [])
    ).lower()
    semantic_terms = {
        token
        for token in re.findall(r"[a-z0-9]+", semantic_text)
        if len(token) > 3 and token not in {"with", "from", "above", "below", "control", "operating"}
    }

    def relevant_sop(match: dict) -> bool:
        matched_keywords = [str(item).lower() for item in match.get("matched_keywords", [])]
        content = f"{match.get('section_title', '')} {match.get('content', '')}".lower()
        if match.get("section_title") == "Overview":
            return False
        if any(identifier in content for identifier in exact_identifiers):
            return True
        return any(
            term in content and any(term in keyword or keyword in term for keyword in matched_keywords)
            for term in semantic_terms
        )

    def relevant_maintenance(match: dict) -> bool:
        content = match.get("content", "").lower()
        if any(identifier in content for identifier in exact_identifiers):
            return True
        matched_terms = sum(term in content for term in semantic_terms)
        return matched_terms >= 2

    sop_matches = [item for item in retrieval.get("sop_matches", []) if relevant_sop(item)]
    maintenance_matches = [
        item for item in retrieval.get("maintenance_matches", []) if relevant_maintenance(item)
    ]
    return sop_matches, maintenance_matches


def _build_root_causes(
    sensor_results: dict,
    alarm_events: list[dict],
    retrieval: dict,
    evidence_list: list[Evidence],
    manifest: dict,
    fault_modes: list[dict],
) -> list[RootCauseCandidate]:
    """Build root cause candidates from fault mode matching + evidence."""
    ev_id_set = {ev.id for ev in evidence_list}
    alarm_codes = [e["alarm_code"] for e in alarm_events]
    anomaly_fields = [a["field"] for a in sensor_results.get("anomalies", [])]
    operator_note = manifest.get("operator_note", "")

    # Map helpers
    def ev_ids_for_codes(*codes: str) -> list[str]:
        code_set = set(codes)
        return [
            ev.id
            for ev in evidence_list
            if ev.value in code_set and ev.id in ev_id_set
        ]

    def ev_ids_for_fields(*fields: str) -> list[str]:
        ids = []
        for ev in evidence_list:
            if ev.field in fields:
                ids.append(ev.id)
        return [i for i in ids if i in ev_id_set]

    def ev_ids_for_records(*record_ids: str) -> list[str]:
        ids = []
        for ev in evidence_list:
            for rid in record_ids:
                if ev.value == rid or rid in (ev.summary or ""):
                    ids.append(ev.id)
        return [i for i in ids if i in ev_id_set]

    candidates: list[RootCauseCandidate] = []
    rc_counter = 0

    # Match each fault mode against observed data
    for fm in fault_modes:
        fm_alarms = set(fm.get("related_alarm_codes", []))
        fm_fields = set(fm.get("related_sensor_fields", []))
        primary_alarms = set(fm.get("primary_alarm_codes", []))
        primary_fields = set(fm.get("primary_sensor_fields", []))
        role = fm.get("diagnostic_role", "equipment_cause")

        # Check if any alarm code or anomaly field matches this fault mode
        alarm_hit = bool(fm_alarms.intersection(alarm_codes))
        sensor_hit = bool(fm_fields.intersection(anomaly_fields))
        primary_hit = bool(
            primary_alarms.intersection(alarm_codes)
            or primary_fields.intersection(anomaly_fields)
        )

        if (not alarm_hit and not sensor_hit) or (role == "equipment_cause" and not primary_hit):
            continue

        sop_matches, maintenance_matches = _candidate_retrieval_matches(fm, retrieval)

        # Compute score breakdown using candidate-specific retrieval evidence.
        score = _compute_score(
            fm,
            alarm_codes,
            anomaly_fields,
            len(sop_matches),
            len(maintenance_matches),
            operator_note,
        )

        # Skip very low scores
        if score.total < 0.10:
            continue

        # Collect evidence IDs
        ev_ids = ev_ids_for_codes(*fm_alarms) + ev_ids_for_fields(*fm_fields)

        relevant_sop_titles = {item.get("section_title", "") for item in sop_matches}
        relevant_record_ids = {item.get("record_id", "") for item in maintenance_matches}
        for ev in evidence_list:
            if ev.source == "maintenance_records.md" and ev.value in relevant_record_ids and ev.id not in ev_ids:
                ev_ids.append(ev.id)
            if ev.source != "maintenance_records.md" and any(
                title and title in ev.summary for title in relevant_sop_titles
            ) and ev.id not in ev_ids:
                ev_ids.append(ev.id)

        # Determine priority
        if score.total >= 0.55:
            priority = "high"
        elif score.total >= 0.30:
            priority = "medium"
        else:
            priority = "low"

        rc_counter += 1
        candidate_id = f"RC-{rc_counter:03d}"

        # Build rationale
        rationale_parts = []
        if alarm_hit:
            matched_alarms = fm_alarms.intersection(alarm_codes)
            rationale_parts.append(f"Matched alarm codes: {', '.join(sorted(matched_alarms))}.")
        if sensor_hit:
            matched_fields = fm_fields.intersection(anomaly_fields)
            rationale_parts.append(f"Anomalous sensor fields: {', '.join(sorted(matched_fields))}.")
        if sop_matches:
            rationale_parts.append("SOP sections provide relevant check procedures.")
        if maintenance_matches:
            rationale_parts.append("Historical maintenance records show similar patterns.")

        rationale = " ".join(rationale_parts) if rationale_parts else "Pattern match based on fault mode library."
        missing_evidence = []
        if primary_alarms and not primary_alarms.intersection(alarm_codes):
            missing_evidence.append(f"primary alarm: {', '.join(sorted(primary_alarms))}")
        if primary_fields and not primary_fields.intersection(anomaly_fields):
            missing_evidence.append(f"primary sensor anomaly: {', '.join(sorted(primary_fields))}")
        why_ranked = (
            f"Ranked from alarm {score.alarm_match:.0%}, sensor {score.sensor_correlation:.0%}, "
            f"SOP {score.sop_match:.0%}, maintenance {score.maintenance_similarity:.0%}, "
            f"and operator note {score.operator_note_match:.0%} evidence."
        )

        candidates.append(RootCauseCandidate(
            candidate_id=candidate_id,
            title=fm["title"],
            title_zh=fm.get("title_zh"),
            confidence=round(score.total, 2),
            priority=priority,
            evidence_ids=ev_ids,
            rationale=rationale,
            score_breakdown=score,
            fault_mode_id=fm.get("fault_mode_id"),
            diagnostic_role=role,
            why_ranked=why_ranked,
            missing_evidence=missing_evidence,
        ))

    # Sort by the underlying score to avoid rounded confidence ties changing RC-001.
    role_rank = {
        "equipment_cause": 2,
        "coupled_secondary_factor": 1,
        "quality_effect": 0,
    }
    candidates.sort(
        key=lambda c: (
            role_rank.get(c.diagnostic_role, 0),
            c.score_breakdown.total if c.score_breakdown else c.confidence,
        ),
        reverse=True,
    )

    # Re-number after sort
    for i, c in enumerate(candidates, 1):
        c.candidate_id = f"RC-{i:03d}"

    return candidates


def _build_actions(
    root_causes: list[RootCauseCandidate],
    retrieval: dict,
    manifest: dict,
    diagnosis_status: str = "provisional",
    missing_evidence: list[str] | None = None,
    conflicting_evidence: list[str] | None = None,
) -> list[RecommendedAction]:
    """Build recommended actions from root causes, SOP, and manifest context."""
    actions: list[RecommendedAction] = []
    act_counter = 0
    missing_evidence = missing_evidence or []
    conflicting_evidence = conflicting_evidence or []

    def next_id() -> str:
        nonlocal act_counter
        act_counter += 1
        return f"ACT-{act_counter:03d}"

    if diagnosis_status == "insufficient_evidence":
        actions.append(RecommendedAction(
            action_id=next_id(),
            title="Collect missing diagnostic evidence",
            type="collect_data",
            linked_candidate_ids=[],
            detail=(
                "Collect and validate the following evidence before confirming a root cause: "
                + "; ".join(missing_evidence)
            ),
            role="equipment_engineer",
        ))
        actions.append(RecommendedAction(
            action_id=next_id(),
            title="Perform bounded manual inspection",
            type="inspect",
            linked_candidate_ids=[
                rc.candidate_id
                for rc in root_causes
                if rc.diagnostic_role != "quality_effect"
            ][:2],
            detail="Inspect the affected station using the applicable SOP without replacing interlocks or making automatic control changes.",
            role="equipment_engineer",
        ))

    if diagnosis_status == "conflicting_evidence":
        actions.append(RecommendedAction(
            action_id=next_id(),
            title="Reconcile conflicting evidence before repair",
            type="verify",
            linked_candidate_ids=[rc.candidate_id for rc in root_causes[:2]],
            detail=(
                "Verify sensor calibration, alarm timestamps, and equipment state because the evidence channels disagree: "
                + "; ".join(conflicting_evidence)
            ),
            role="equipment_engineer",
        ))

    # Generate actions from SOP retrieval results
    for match in retrieval.get("sop_matches", []):
        title = match["section_title"]
        content = match["content"]
        # Extract recommended checks from SOP section
        checks = []
        for line in content.split("\n"):
            line = line.strip()
            if line and line[0].isdigit() and "." in line[:3]:
                check_text = line.split(".", 1)[1].strip()
                if check_text:
                    checks.append(check_text)

        if checks:
            linked_rcs = []
            # Link to root causes whose alarm codes or fields match
            for rc in root_causes:
                fm_id = rc.fault_mode_id or ""
                section_lower = title.lower()
                rc_lower = rc.title.lower()
                if any(kw in section_lower for kw in rc_lower.split()) or fm_id in section_lower:
                    linked_rcs.append(rc.candidate_id)

            act_counter += 1
            actions.append(RecommendedAction(
                action_id=f"ACT-{act_counter:03d}",
                title=f"Follow SOP: {title}",
                type="inspect",
                linked_candidate_ids=linked_rcs or [rc.candidate_id for rc in root_causes[:1]],
                detail=f"Per SOP section '{title}': {'; '.join(checks[:3])}",
                role="equipment_engineer",
            ))

    # Quality action if thickness drift detected
    has_thickness_rc = any("thickness" in rc.title.lower() or "yield" in rc.title.lower() or "quality" in rc.title.lower() for rc in root_causes)
    if has_thickness_rc:
        act_counter += 1
        actions.append(RecommendedAction(
            action_id=f"ACT-{act_counter:03d}",
            title="Quality engineer review of affected material",
            type="quality",
            linked_candidate_ids=[rc.candidate_id for rc in root_causes if "thickness" in rc.title.lower() or "yield" in rc.title.lower()],
            detail="Isolate affected material roll range. Request quality engineer review before release. Document thickness deviation for batch record.",
            role="quality_engineer",
        ))

    # Production supervisor notification
    high_rcs = [rc for rc in root_causes if rc.priority == "high"]
    if high_rcs and diagnosis_status not in {"insufficient_evidence", "conflicting_evidence"}:
        act_counter += 1
        actions.append(RecommendedAction(
            action_id=f"ACT-{act_counter:03d}",
            title="Notify production supervisor",
            type="escalate",
            linked_candidate_ids=[rc.candidate_id for rc in high_rcs],
            detail=f"High-priority root causes detected: {', '.join(rc.title for rc in high_rcs)}. Production supervisor should be notified for resource allocation and scheduling decisions.",
            role="production_supervisor",
        ))

    # Safety action
    act_counter += 1
    actions.append(RecommendedAction(
        action_id=f"ACT-{act_counter:03d}",
        title="Confirm safety procedures before equipment intervention",
        type="safety",
        linked_candidate_ids=[rc.candidate_id for rc in root_causes],
        detail="All equipment inspections and interventions must follow factory safety procedures. Do not bypass interlocks or overcurrent protection. Final equipment operation requires on-site engineer confirmation.",
        role="safety_reviewer",
    ))

    return actions


def _build_work_order(
    root_causes: list[RootCauseCandidate],
    actions: list[RecommendedAction],
    manifest: dict,
) -> WorkOrderDraft:
    """Build a work order draft from root causes and actions."""
    has_high = any(rc.priority == "high" for rc in root_causes)
    tasks = [a.detail for a in actions if a.type != "safety"]
    safety_notes = [a.detail for a in actions if a.type == "safety"]
    if not safety_notes:
        safety_notes = ["Final equipment operation requires on-site engineer confirmation."]

    line = manifest.get("line", "production line")
    station = manifest.get("station", "equipment")

    return WorkOrderDraft(
        title=f"Check {line} {station}",
        priority="high" if has_high else "medium",
        assignee_role="equipment engineer",
        tasks=tasks,
        safety_notes=safety_notes,
    )


def _build_evidence_links(
    root_causes: list[RootCauseCandidate],
    evidence_list: list[Evidence],
) -> list[EvidenceLink]:
    """Build evidence graph links: root_cause -> evidence -> source."""
    links: list[EvidenceLink] = []
    for rc in root_causes:
        for eid in rc.evidence_ids:
            links.append(EvidenceLink(
                source_id=rc.candidate_id,
                target_id=eid,
                relation="supported_by",
            ))
    # Evidence source links
    for ev in evidence_list:
        if ev.source:
            links.append(EvidenceLink(
                source_id=ev.id,
                target_id=ev.source,
                relation="from_source",
            ))
    return links


def _build_data_quality(
    sensor_rows: list[dict],
    alarm_events: list[dict],
    sop_text: str,
    maintenance_text: str,
    manifest: dict,
) -> DataQualityReport:
    """Build data quality report for the case."""
    import re

    sop_sections = len(re.findall(r"^## ", sop_text, re.MULTILINE))
    maint_records = len(re.findall(r"^## Record ", maintenance_text, re.MULTILINE))

    # Expected evidence fields are case-specific. Missing fields are warnings, not malformed input.
    required_sensor_fields = manifest.get("expected_sensor_fields", ["timestamp"])
    missing = []
    if sensor_rows:
        present_fields = set(sensor_rows[0].keys())
        missing = [f for f in required_sensor_fields if f not in present_fields]

    warnings = []
    invalid_fields: list[str] = []
    if len(sensor_rows) < 5:
        warnings.append("Very few sensor data points – analysis may be unreliable.")
    if len(alarm_events) == 0:
        warnings.append("No alarm events in the incident window.")
    if missing:
        warnings.append(f"Missing sensor fields: {', '.join(missing)}")
    expected_count = max(len(required_sensor_fields), 1)
    completeness_score = max(0.0, 1.0 - len(missing) / expected_count)
    if not sop_text.strip():
        completeness_score -= 0.1
    if not maintenance_text.strip():
        completeness_score -= 0.1
    completeness_score = round(max(0.0, min(1.0, completeness_score)), 3)

    return DataQualityReport(
        sensor_rows=len(sensor_rows),
        alarm_events=len(alarm_events),
        sop_sections=sop_sections,
        maintenance_records=maint_records,
        missing_fields=missing,
        warnings=warnings,
        invalid_fields=invalid_fields,
        completeness_score=completeness_score,
    )


def _assess_diagnosis(
    candidates: list[RootCauseCandidate],
    data_quality: DataQualityReport,
    manifest: dict,
) -> tuple[str, RootCauseCandidate | None, list[RootCauseCandidate], list[RootCauseCandidate], list[str], list[str]]:
    """Assess evidence sufficiency and separate causes, factors, and effects."""
    equipment_causes = [item for item in candidates if item.diagnostic_role == "equipment_cause"]
    contributing = [item for item in candidates if item.diagnostic_role == "coupled_secondary_factor"]
    effects = [item for item in candidates if item.diagnostic_role == "quality_effect"]
    primary = equipment_causes[0] if equipment_causes else None

    critical_fields = set(manifest.get("critical_evidence_fields", []))
    missing_critical = sorted(critical_fields.intersection(data_quality.missing_fields))
    missing_evidence = [f"critical sensor field: {field}" for field in missing_critical]
    if primary:
        missing_evidence.extend(primary.missing_evidence)

    conflicting_evidence: list[str] = []
    if len(equipment_causes) >= 2:
        alarm_leader = max(
            equipment_causes,
            key=lambda item: (
                item.score_breakdown.alarm_match if item.score_breakdown else 0,
                item.score_breakdown.total if item.score_breakdown else item.confidence,
            ),
        )
        sensor_leader = max(
            equipment_causes,
            key=lambda item: (
                item.score_breakdown.sensor_correlation if item.score_breakdown else 0,
                item.score_breakdown.total if item.score_breakdown else item.confidence,
            ),
        )
        alarm_score = alarm_leader.score_breakdown.alarm_match if alarm_leader.score_breakdown else 0
        sensor_score = sensor_leader.score_breakdown.sensor_correlation if sensor_leader.score_breakdown else 0
        if alarm_leader.fault_mode_id != sensor_leader.fault_mode_id and alarm_score >= 1.0 and sensor_score >= 1.0:
            conflicting_evidence.append(
                f"alarms favor {alarm_leader.title}, while sensor anomalies favor {sensor_leader.title}"
            )

    if conflicting_evidence:
        status = "conflicting_evidence"
    elif (
        primary is None
        or missing_critical
        or primary.confidence < 0.55
        or (
            primary.score_breakdown is not None
            and primary.score_breakdown.alarm_match + primary.score_breakdown.sensor_correlation < 1.0
        )
    ):
        status = "insufficient_evidence"
    elif primary.confidence >= 0.75 and not primary.missing_evidence:
        status = "confirmed"
    else:
        status = "provisional"

    if status in {"insufficient_evidence", "conflicting_evidence"}:
        cap = 0.49 if status == "insufficient_evidence" else 0.59
        for item in candidates:
            item.confidence = min(item.confidence, cap)

    return status, primary, contributing, effects, list(dict.fromkeys(missing_evidence)), conflicting_evidence


def _build_value_estimates(
    root_causes: list[RootCauseCandidate],
    manifest: dict,
    diagnosis_status: str,
) -> list[ValueEstimate]:
    """Build transparent estimates only from explicitly configured assumptions."""
    estimates: list[ValueEstimate] = []
    if diagnosis_status in {"insufficient_evidence", "conflicting_evidence"}:
        return estimates

    context = manifest.get("business_context", {})
    baseline_mttr = context.get("mttr_baseline_minutes")
    reduction_pct = context.get("target_mttr_reduction_pct")
    if isinstance(baseline_mttr, (int, float)) and isinstance(reduction_pct, (int, float)):
        projected = baseline_mttr * (1 - reduction_pct / 100)
        estimates.append(ValueEstimate(
            metric="MTTR reduction target",
            baseline=f"{baseline_mttr:.0f} min configured pilot baseline",
            projected=f"{projected:.0f} min at a {reduction_pct:.0f}% reduction target",
            assumption="Scenario calculation from case_manifest business_context; not a validated production result.",
            configured=True,
        ))

    downtime_cost = context.get("downtime_cost_per_minute")
    if (
        isinstance(downtime_cost, (int, float))
        and isinstance(baseline_mttr, (int, float))
        and isinstance(reduction_pct, (int, float))
    ):
        avoided_minutes = baseline_mttr * reduction_pct / 100
        estimates.append(ValueEstimate(
            metric="Avoided downtime scenario",
            baseline=f"{downtime_cost:.0f} currency units per downtime minute",
            projected=f"{avoided_minutes * downtime_cost:.0f} currency units per incident",
            assumption="Illustrative scenario only. Currency and plant cost must be configured and validated during a pilot.",
            configured=True,
        ))

    if not estimates:
        estimates.append(ValueEstimate(
            metric="Pilot value baseline",
            baseline="Not configured",
            projected="Not calculated",
            assumption="Add case_manifest.business_context before presenting quantified value.",
            configured=False,
        ))

    return estimates


def _execute_diagnosis(
    case_id: str,
    case_data: dict | None = None,
    agent_decisions: list[AgentDecision] | None = None,
) -> Diagnosis:
    """Execute the bounded diagnosis workflow for loaded or in-memory case data."""
    process_steps: list[ProcessStep] = []
    agent_decisions = agent_decisions if agent_decisions is not None else []

    # Step 1: Load case data
    try:
        if case_data is None:
            manifest = load_case_manifest(case_id)
            sensor_rows = load_sensor_readings(case_id)
            alarm_rows = load_alarms(case_id)
            sop_text = load_sop(case_id)
            maintenance_text = load_maintenance_records(case_id)
        else:
            manifest = case_data["manifest"]
            sensor_rows = case_data["sensor_rows"]
            alarm_rows = case_data["alarm_rows"]
            sop_text = case_data["sop_text"]
            maintenance_text = case_data["maintenance_text"]
    except (FileNotFoundError, CaseValidationError):
        raise
    except (OSError, KeyError, TypeError, ValueError) as e:
        raise ValueError(f"Failed to load case {case_id}: {e}") from e

    agent_decisions.append(AgentDecision(
        state="load",
        decision="continue",
        reason="All required case resources were loaded.",
    ))
    process_steps.append(ProcessStep(
        step="Data Loading",
        status="completed",
        detail=f"Loaded manifest, {len(sensor_rows)} sensor rows, {len(alarm_rows)} alarm rows, SOP and maintenance records.",
    ))

    # Step 2: Data quality check
    alarm_events = parse_alarms(alarm_rows)
    data_quality = _build_data_quality(sensor_rows, alarm_events, sop_text, maintenance_text, manifest)
    agent_decisions.append(AgentDecision(
        state="validate",
        decision="continue_with_caution" if data_quality.warnings else "continue",
        reason=(
            "; ".join(data_quality.warnings)
            if data_quality.warnings
            else "Case data passed quality checks without warnings."
        ),
    ))
    process_steps.append(ProcessStep(
        step="Data Validation",
        status="completed",
        detail=f"Sensor rows: {data_quality.sensor_rows}, Alarms: {data_quality.alarm_events}, "
               f"SOP sections: {data_quality.sop_sections}, Maintenance records: {data_quality.maintenance_records}."
               + (f" Warnings: {'; '.join(data_quality.warnings)}" if data_quality.warnings else ""),
    ))

    # Step 3: Signal anomaly detection
    sensor_results = analyze_sensor_data(sensor_rows)
    anomaly_count = len(sensor_results.get("anomalies", []))
    process_steps.append(ProcessStep(
        step="Signal Anomaly Detection",
        status="completed",
        detail=f"Detected {anomaly_count} anomalies across {len(set(a['field'] for a in sensor_results.get('anomalies', [])))} fields. "
               f"Correlated findings: {len(sensor_results.get('correlated_findings', []))}.",
    ))

    # Step 4: Alarm correlation
    process_steps.append(ProcessStep(
        step="Alarm Correlation",
        status="completed",
        detail=f"Parsed {len(alarm_events)} alarm events. Alarm codes: {', '.join(sorted(set(e['alarm_code'] for e in alarm_events)))}.",
    ))

    # Step 5: SOP and maintenance retrieval
    alarm_codes = [e["alarm_code"] for e in alarm_events]
    anomaly_fields = [a["field"] for a in sensor_results.get("anomalies", [])]
    sop_source_name = manifest.get("files", {}).get("sop", "sop")
    retrieval = retrieve_relevant(sop_text, maintenance_text, alarm_codes, anomaly_fields, sop_source_name)
    process_steps.append(ProcessStep(
        step="SOP & Maintenance Retrieval",
        status="completed",
        detail=f"Retrieved {len(retrieval.get('sop_matches', []))} SOP sections and {len(retrieval.get('maintenance_matches', []))} maintenance records.",
    ))

    # Step 6: Root cause ranking
    fault_modes = _load_fault_modes()
    evidence_list = _build_evidence(alarm_events, sensor_results, retrieval)
    all_candidates = _build_root_causes(sensor_results, alarm_events, retrieval, evidence_list, manifest, fault_modes)
    (
        diagnosis_status,
        primary_root_cause,
        contributing_factors,
        downstream_effects,
        missing_evidence,
        conflicting_evidence,
    ) = _assess_diagnosis(all_candidates, data_quality, manifest)
    causal_candidates = [item for item in all_candidates if item.diagnostic_role != "quality_effect"]
    if primary_root_cause:
        causal_candidates = [primary_root_cause] + [
            item for item in causal_candidates if item.candidate_id != primary_root_cause.candidate_id
        ]
    agent_decisions.append(AgentDecision(
        state="assess_evidence",
        decision=diagnosis_status,
        reason=(
            "; ".join(conflicting_evidence or missing_evidence)
            if conflicting_evidence or missing_evidence
            else f"Primary candidate has {primary_root_cause.confidence:.0%} confidence with sufficient evidence."
            if primary_root_cause
            else "No equipment root cause candidate was supported."
        ),
    ))
    process_steps.append(ProcessStep(
        step="Root Cause Ranking",
        status="completed",
        detail=f"Matched {len(all_candidates)} candidates from {len(fault_modes)} fault modes. "
               f"Primary: {primary_root_cause.title if primary_root_cause else 'none'} "
               f"(status: {diagnosis_status}).",
    ))
    process_steps.append(ProcessStep(
        step="Evidence Sufficiency Decision",
        status="completed",
        detail=(
            f"Decision: {diagnosis_status}. "
            + (
                f"Missing: {'; '.join(missing_evidence)}."
                if missing_evidence
                else ""
            )
            + (
                f" Conflicts: {'; '.join(conflicting_evidence)}."
                if conflicting_evidence
                else ""
            )
        ).strip(),
    ))

    # Step 7: Action planning
    actions = _build_actions(
        all_candidates,
        retrieval,
        manifest,
        diagnosis_status,
        missing_evidence,
        conflicting_evidence,
    )
    process_steps.append(ProcessStep(
        step="Action Planning",
        status="completed",
        detail=f"Generated {len(actions)} recommended actions across roles: {', '.join(sorted(set(a.role or 'unassigned' for a in actions)))}.",
    ))

    # Step 8: Report generation
    timeline = _build_timeline(alarm_events, sensor_results, evidence_list)
    work_order = _build_work_order(all_candidates, actions, manifest)
    evidence_links = _build_evidence_links(all_candidates, evidence_list)
    value_estimates = _build_value_estimates(all_candidates, manifest, diagnosis_status)
    process_steps.append(ProcessStep(
        step="Report Generation",
        status="completed",
        detail=f"Generated timeline ({len(timeline)} events), work order, evidence graph ({len(evidence_links)} links), and value estimates.",
    ))

    # Incident summary
    if diagnosis_status == "insufficient_evidence":
        incident_summary = (
            f"{manifest['title']}. Evidence is insufficient to confirm a root cause. "
            f"Incident window: {manifest['incident_window']['start']} to {manifest['incident_window']['end']}."
        )
    elif diagnosis_status == "conflicting_evidence":
        incident_summary = (
            f"{manifest['title']}. Alarm and sensor evidence conflict; verification is required before repair. "
            f"Incident window: {manifest['incident_window']['start']} to {manifest['incident_window']['end']}."
        )
    else:
        incident_summary = (
            f"{manifest['title']}. "
            f"Primary root cause: {primary_root_cause.title if primary_root_cause else 'unknown'}. "
            f"Incident window: {manifest['incident_window']['start']} to {manifest['incident_window']['end']}."
        )

    # Postmortem summary
    if diagnosis_status == "insufficient_evidence":
        postmortem = (
            "The available evidence does not support a reliable root-cause conclusion. "
            "Collect the listed missing evidence and repeat the bounded diagnosis before approving repair work."
        )
    elif diagnosis_status == "conflicting_evidence":
        postmortem = (
            "The incident contains conflicting alarm and sensor evidence. "
            "Validate instrumentation and timestamp alignment before selecting a repair path."
        )
    elif primary_root_cause:
        primary = primary_root_cause.title
        if contributing_factors:
            postmortem = (
                f"The incident likely originated from {primary}, "
                f"with {contributing_factors[0].title} as a coupled secondary factor. "
                f"Downstream effects should be reviewed by the quality team."
            )
        else:
            postmortem = (
                f"The incident likely originated from {primary}. "
                f"No coupled secondary factor was confirmed; downstream effects should be reviewed by the quality team."
            )
    else:
        postmortem = "Insufficient data to determine root cause."

    limitations = [
        "This diagnosis is generated from synthetic demo data.",
        "Real equipment actions require factory safety procedures and engineer confirmation.",
        "Configured value estimates are scenario calculations, not validated production results.",
    ]

    return Diagnosis(
        case_id=case_id,
        diagnosis_status=diagnosis_status,
        incident_summary=incident_summary,
        timeline=timeline,
        evidence=evidence_list,
        root_cause_candidates=causal_candidates,
        primary_root_cause=primary_root_cause,
        contributing_factors=contributing_factors,
        downstream_effects=downstream_effects,
        business_risks=[item.title for item in downstream_effects],
        missing_evidence=missing_evidence,
        conflicting_evidence=conflicting_evidence,
        recommended_actions=actions,
        work_order_draft=work_order,
        postmortem_summary=postmortem,
        limitations=limitations,
        diagnostic_process=process_steps,
        agent_decisions=agent_decisions,
        evidence_links=evidence_links,
        data_quality=data_quality,
        value_estimates=value_estimates,
    )


def _sanitize_reasoning(diagnosis: Diagnosis, review) -> None:
    """Drop any evidence/candidate references that do not belong to this case.

    Guarantees the engine invariants regardless of which provider produced the
    review. Mutates ``review`` in place.
    """
    allowed_evidence = {item.id for item in diagnosis.evidence}
    allowed_candidates = {
        item.candidate_id
        for item in (
            list(diagnosis.root_cause_candidates)
            + list(diagnosis.contributing_factors)
            + list(diagnosis.downstream_effects)
        )
    }
    clean_evidence = [i for i in review.referenced_evidence_ids if i in allowed_evidence]
    dropped_evidence = sorted(set(review.referenced_evidence_ids) - allowed_evidence)
    clean_notes = [n for n in review.candidate_notes if n.candidate_id in allowed_candidates]
    dropped_notes = len(review.candidate_notes) - len(clean_notes)
    review.referenced_evidence_ids = sorted(set(clean_evidence))
    review.candidate_notes = clean_notes
    notes = []
    if dropped_evidence:
        notes.append("dropped unknown evidence ids: " + ", ".join(dropped_evidence))
    if dropped_notes:
        notes.append(f"dropped {dropped_notes} candidate note(s) with unknown candidate_id")
    if notes:
        review.warning = (review.warning + "; " if review.warning else "") + "; ".join(notes)


def _apply_reasoning(
    diagnosis: Diagnosis,
    reasoning: str,
) -> None:
    """Attach the advisory LLM review layer (if enabled) and finalize limitations.

    The deterministic diagnosis is never modified structurally. When an LLM
    provider is configured and reasoning is not explicitly off, an advisory
    review is attached via ``agent_reasoning`` and an audit decision is
    appended to the agent decision trace. Mutations target the diagnosis
    model's own attributes directly (Pydantic v2 rebuilds list fields on
    validation, so the caller's list is not shared with the model).
    """
    if reasoning == "off":
        diagnosis.limitations.append("Deterministic analysis only – no LLM reasoning applied.")
        return

    review = get_model_provider().reason(diagnosis)
    if review is None:
        # Offline provider: no LLM reasoning available.
        diagnosis.limitations.append("Deterministic analysis only – no LLM reasoning applied.")
        return

    diagnosis.agent_reasoning = review
    # Defense in depth: sanitize the review regardless of which provider
    # produced it, so the engine guarantees the evidence/candidate invariants
    # even if a custom provider returns ids that do not belong to this case.
    _sanitize_reasoning(diagnosis, review)
    if review.warning:
        decision = "continue_with_caution"
        reason = review.warning
    else:
        decision = "confirmed"
        reason = (
            review.review_summary
            or "LLM review completed; advisory notes attached without changing structured diagnosis."
        )
    diagnosis.agent_decisions.append(AgentDecision(state="llm_review", decision=decision, reason=reason))
    diagnosis.limitations.append(
        "LLM reasoning is advisory; structured diagnosis is deterministic and evidence-validated."
    )


class DiagnosisAgent:
    """Bounded, auditable state machine for industrial diagnosis."""

    def __init__(
        self,
        case_id: str,
        case_data: dict | None = None,
        reasoning: str = "auto",
    ):
        self.case_id = case_id
        self.case_data = case_data
        self.reasoning = reasoning
        self.decisions: list[AgentDecision] = []

    def run(self) -> Diagnosis:
        diagnosis = _execute_diagnosis(self.case_id, self.case_data, self.decisions)
        _apply_reasoning(diagnosis, self.reasoning)
        return diagnosis


def build_diagnosis(case_id: str, reasoning: str = "auto") -> Diagnosis:
    """Build a diagnosis from the registered case directory."""
    return DiagnosisAgent(case_id, reasoning=reasoning).run()


def build_diagnosis_from_data(
    case_id: str,
    manifest: dict,
    sensor_rows: list[dict[str, str]],
    alarm_rows: list[dict[str, str]],
    sop_text: str,
    maintenance_text: str,
) -> Diagnosis:
    """Build a diagnosis from in-memory data for validation and counterfactual tests."""
    return DiagnosisAgent(
        case_id,
        {
            "manifest": manifest,
            "sensor_rows": sensor_rows,
            "alarm_rows": alarm_rows,
            "sop_text": sop_text,
            "maintenance_text": maintenance_text,
        },
    ).run()


def severity_label(sev: str) -> str:
    """Map severity to display label."""
    return {"info": "info", "warning": "warning", "major": "major", "critical": "critical"}.get(sev, "info")
