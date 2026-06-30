#!/usr/bin/env python3
"""Evaluate ForgePulse behavior, evidence integrity, and determinism."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EVALUATION_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT / "app" / "backend"))

from forgepulse_api.services.case_loader import (
    get_case_dir,
    list_available_cases,
    load_alarms,
    load_case_manifest,
    load_maintenance_records,
    load_sensor_readings,
    load_sop,
)
from forgepulse_api.services.diagnosis import build_diagnosis, build_diagnosis_from_data
from forgepulse_api.services.report_writer import render_markdown_report


def add_check(result: dict, name: str, passed: bool, detail: str) -> None:
    result["checks"].append({"check": name, "passed": passed, "detail": detail})
    result["max_score"] += 1
    if passed:
        result["score"] += 1


def load_golden_cases() -> list[dict]:
    cases: list[dict] = []
    for case_id in list_available_cases():
        golden_path = get_case_dir(case_id) / "golden_expectations.json"
        if not golden_path.is_file():
            continue
        payload = json.loads(golden_path.read_text(encoding="utf-8"))
        golden = payload.get("golden_expectations", {})
        cases.append({"case_id": case_id, **golden})
    return cases


def candidate_ids(diagnosis) -> set[str]:
    return {
        item.candidate_id
        for item in (
            diagnosis.root_cause_candidates
            + diagnosis.contributing_factors
            + diagnosis.downstream_effects
        )
    }


def evaluate_case(golden: dict) -> dict:
    case_id = golden["case_id"]
    result = {"case_id": case_id, "checks": [], "score": 0, "max_score": 0}

    try:
        diagnosis = build_diagnosis(case_id)
    except Exception as exc:
        add_check(result, "diagnosis_build", False, str(exc))
        return result

    expected_status = golden.get("expected_status", "confirmed")
    add_check(
        result,
        "diagnosis_status",
        diagnosis.diagnosis_status == expected_status,
        f"actual={diagnosis.diagnosis_status}, expected={expected_status}",
    )

    primary_keywords = golden.get("expected_primary_root_cause_keywords", [])
    if primary_keywords:
        primary_title = diagnosis.primary_root_cause.title.lower() if diagnosis.primary_root_cause else ""
        hits = sum(keyword.lower() in primary_title for keyword in primary_keywords)
        add_check(
            result,
            "top_ranked_primary_root_cause",
            hits >= max(1, len(primary_keywords) // 2),
            f"matched {hits}/{len(primary_keywords)} keywords in {primary_title or 'none'}",
        )

    evidence_values = {item.value for item in diagnosis.evidence if item.value}
    required_codes = set(golden.get("required_evidence_codes", []))
    add_check(
        result,
        "required_evidence_codes",
        required_codes.issubset(evidence_values),
        f"found={sorted(required_codes.intersection(evidence_values))}",
    )

    required_fields = set(golden.get("required_evidence_fields", []))
    if required_fields:
        evidence_fields = {item.field for item in diagnosis.evidence if item.field}
        add_check(
            result,
            "required_evidence_fields",
            required_fields.issubset(evidence_fields),
            f"found={sorted(required_fields.intersection(evidence_fields))}",
        )

    required_missing = set(golden.get("required_missing_fields", []))
    if required_missing:
        missing_fields = set(diagnosis.data_quality.missing_fields if diagnosis.data_quality else [])
        add_check(
            result,
            "required_missing_fields",
            required_missing.issubset(missing_fields),
            f"missing={sorted(missing_fields)}",
        )

    required_records = golden.get("required_maintenance_records", [])
    if required_records:
        evidence_text = " ".join(item.summary for item in diagnosis.evidence)
        add_check(
            result,
            "required_maintenance_records",
            all(record in evidence_text for record in required_records),
            f"required={required_records}",
        )

    ids = candidate_ids(diagnosis)
    evidence_ids = {item.id for item in diagnosis.evidence}
    root_refs_valid = all(
        set(item.evidence_ids).issubset(evidence_ids)
        for item in (
            diagnosis.root_cause_candidates
            + diagnosis.contributing_factors
            + diagnosis.downstream_effects
        )
    )
    add_check(result, "root_cause_evidence_ids", root_refs_valid, "all evidence references must exist")

    action_refs_valid = all(set(action.linked_candidate_ids).issubset(ids) for action in diagnosis.recommended_actions)
    add_check(result, "action_candidate_links", action_refs_valid, "all action candidate references must exist")

    source_nodes = ids | evidence_ids
    target_nodes = evidence_ids | {item.source for item in diagnosis.evidence}
    link_refs_valid = all(
        link.source_id in source_nodes and link.target_id in target_nodes
        for link in diagnosis.evidence_links
    )
    add_check(result, "evidence_graph_links", link_refs_valid, "all evidence graph endpoints must exist")

    action_types = {item.type for item in diagnosis.recommended_actions}
    expected_actions = set(golden.get("expected_action_types", []))
    add_check(
        result,
        "expected_action_types",
        expected_actions.issubset(action_types),
        f"actual={sorted(action_types)}",
    )

    root_range = golden.get("expected_root_cause_count_range", [0, 10])
    root_count = len(diagnosis.root_cause_candidates)
    add_check(
        result,
        "root_cause_count",
        root_range[0] <= root_count <= root_range[1],
        f"actual={root_count}, expected={root_range}",
    )

    maximum_confidence = golden.get("maximum_primary_confidence")
    if maximum_confidence is not None:
        actual = diagnosis.primary_root_cause.confidence if diagnosis.primary_root_cause else 0
        add_check(
            result,
            "confidence_cap",
            actual <= maximum_confidence,
            f"actual={actual:.2f}, maximum={maximum_confidence:.2f}",
        )

    report = render_markdown_report(diagnosis)
    required_sections = [
        "## Incident Summary",
        "## Data Quality",
        "## Diagnostic Process",
        "## Event Timeline",
        "## Recommended Actions",
        "## Work Order Draft",
        "## Postmortem Summary",
        "## Limitations",
        "## Agent Decisions",
    ]
    add_check(
        result,
        "report_sections",
        all(section in report for section in required_sections),
        "required Markdown report sections are present",
    )

    first_dump = diagnosis.model_dump(mode="json")
    second_dump = build_diagnosis(case_id).model_dump(mode="json")
    add_check(result, "deterministic_output", first_dump == second_dump, "two runs must produce identical JSON")

    # Offline evaluation must not attach any LLM reasoning (keeps determinism).
    add_check(
        result,
        "offline_no_agent_reasoning",
        diagnosis.agent_reasoning is None,
        "offline evaluation must not attach LLM reasoning",
    )

    manifest = load_case_manifest(case_id)
    sensor_rows = load_sensor_readings(case_id)
    alarm_rows = load_alarms(case_id)
    sop_text = load_sop(case_id)
    maintenance_text = load_maintenance_records(case_id)

    manifest_without_labels = copy.deepcopy(manifest)
    manifest_without_labels.pop("expected_outputs", None)
    no_label_diagnosis = build_diagnosis_from_data(
        case_id,
        manifest_without_labels,
        sensor_rows,
        alarm_rows,
        sop_text,
        maintenance_text,
    )
    add_check(
        result,
        "no_golden_label_dependency",
        (
            no_label_diagnosis.diagnosis_status == diagnosis.diagnosis_status
            and (
                no_label_diagnosis.primary_root_cause.title if no_label_diagnosis.primary_root_cause else None
            )
            == (diagnosis.primary_root_cause.title if diagnosis.primary_root_cause else None)
        ),
        "removing expected_outputs must not change the diagnosis",
    )

    if primary_keywords and diagnosis.primary_root_cause:
        primary_codes = golden.get("required_evidence_codes", [])[:1]
        counterfactual_alarms = [
            row for row in alarm_rows if row.get("alarm_code") not in primary_codes
        ]
        counterfactual = build_diagnosis_from_data(
            case_id,
            manifest,
            sensor_rows,
            counterfactual_alarms,
            sop_text,
            maintenance_text,
        )
        same_candidate = next(
            (
                item
                for item in counterfactual.root_cause_candidates
                if item.fault_mode_id == diagnosis.primary_root_cause.fault_mode_id
            ),
            None,
        )
        counterfactual_confidence = same_candidate.confidence if same_candidate else 0
        add_check(
            result,
            "counterfactual_alarm_reduces_confidence",
            counterfactual_confidence < diagnosis.primary_root_cause.confidence,
            f"baseline={diagnosis.primary_root_cause.confidence:.2f}, counterfactual={counterfactual_confidence:.2f}",
        )

    forbidden = golden.get("forbidden_claims", [])
    output_text = json.dumps(first_dump, ensure_ascii=False).lower()
    violations = [claim for claim in forbidden if claim.lower() in output_text]
    add_check(result, "forbidden_claims", not violations, f"violations={violations}")

    return result


def main() -> int:
    golden_cases = load_golden_cases()
    if not golden_cases:
        print("ERROR: no golden_expectations.json files found")
        return 1

    print(f"Evaluating {len(golden_cases)} golden cases...\n")
    results = [evaluate_case(case) for case in golden_cases]
    total_score = sum(item["score"] for item in results)
    total_max = sum(item["max_score"] for item in results)
    all_passed = all(all(check["passed"] for check in item["checks"]) for item in results)

    for item in results:
        passed = all(check["passed"] for check in item["checks"])
        print(f"{'PASS' if passed else 'FAIL'} {item['case_id']} ({item['score']}/{item['max_score']})")
        for check in item["checks"]:
            print(f"  {'OK' if check['passed'] else 'XX'} {check['check']}: {check['detail']}")
        print()

    percentage = round(total_score / total_max * 100, 1) if total_max else 0
    output = {
        "overall_score": total_score,
        "overall_max": total_max,
        "overall_pct": percentage,
        "all_passed": all_passed,
        "case_results": results,
    }
    output_path = EVALUATION_ROOT / "evaluation_results.json"
    output_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Overall: {total_score}/{total_max} ({percentage}%)")
    print(f"Status: {'ALL PASS' if all_passed else 'FAILURES'}")
    print(f"Results: {output_path}")
    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
