"""Report writer – render diagnosis as Markdown."""

from __future__ import annotations

from forgepulse_api.schemas import Diagnosis


def render_markdown_report(diagnosis: Diagnosis) -> str:
    lines = [
        f"# Diagnosis Report: {diagnosis.case_id}",
        "",
        f"**Diagnosis status:** `{diagnosis.diagnosis_status}`",
        "",
        "## Incident Summary",
        diagnosis.incident_summary,
        "",
    ]

    if diagnosis.primary_root_cause:
        lines.extend([
            "## Primary Root Cause",
            f"**{diagnosis.primary_root_cause.title}** "
            f"(confidence: {diagnosis.primary_root_cause.confidence:.2f})",
            "",
            diagnosis.primary_root_cause.why_ranked,
            "",
        ])

    if diagnosis.missing_evidence:
        lines.append("## Missing Evidence")
        lines.extend(f"- {item}" for item in diagnosis.missing_evidence)
        lines.append("")

    if diagnosis.conflicting_evidence:
        lines.append("## Conflicting Evidence")
        lines.extend(f"- {item}" for item in diagnosis.conflicting_evidence)
        lines.append("")

    # Data Quality
    if diagnosis.data_quality:
        dq = diagnosis.data_quality
        lines.append("## Data Quality")
        lines.append(f"- Sensor rows: {dq.sensor_rows}")
        lines.append(f"- Alarm events: {dq.alarm_events}")
        lines.append(f"- SOP sections: {dq.sop_sections}")
        lines.append(f"- Maintenance records: {dq.maintenance_records}")
        if dq.missing_fields:
            lines.append(f"- ⚠ Missing fields: {', '.join(dq.missing_fields)}")
        if dq.warnings:
            for w in dq.warnings:
                lines.append(f"- ⚠ {w}")
        lines.append("")

    # Diagnostic Process
    if diagnosis.diagnostic_process:
        lines.append("## Diagnostic Process")
        for step in diagnosis.diagnostic_process:
            status_icon = "✅" if step.status == "completed" else "⏭" if step.status == "skipped" else "❌"
            duration = f" ({step.duration_ms:.0f}ms)" if step.duration_ms else ""
            lines.append(f"- {status_icon} **{step.step}**{duration}: {step.detail}")
        lines.append("")

    # Timeline
    lines.append("## Event Timeline")
    for evt in diagnosis.timeline:
        lines.append(f"- **{evt.timestamp}** [{evt.severity}] {evt.title}: {evt.detail}")

    lines.append("")
    lines.append("## Root Cause Candidates")
    for rc in diagnosis.root_cause_candidates:
        lines.append(f"### {rc.candidate_id}: {rc.title}")
        lines.append(f"- **Confidence**: {rc.confidence:.2f} | **Priority**: {rc.priority}")
        if rc.fault_mode_id:
            lines.append(f"- **Fault Mode**: {rc.fault_mode_id}")
        lines.append(f"- **Diagnostic Role**: {rc.diagnostic_role}")
        if rc.score_breakdown:
            sb = rc.score_breakdown
            lines.append(f"- **Score Breakdown**: alarm={sb.alarm_match:.2f}, sensor={sb.sensor_correlation:.2f}, "
                         f"sop={sb.sop_match:.2f}, maint={sb.maintenance_similarity:.2f}, "
                         f"note={sb.operator_note_match:.2f} → total={sb.total:.2f}")
        lines.append(f"- **Evidence**: {', '.join(rc.evidence_ids)}")
        lines.append(f"- **Rationale**: {rc.rationale}")
        lines.append(f"- **Why Ranked**: {rc.why_ranked}")
        if rc.missing_evidence:
            lines.append(f"- **Missing Evidence**: {', '.join(rc.missing_evidence)}")
        lines.append("")

    if diagnosis.contributing_factors:
        lines.append("## Contributing Factors")
        for item in diagnosis.contributing_factors:
            lines.append(f"- **{item.candidate_id}** {item.title} ({item.confidence:.2f})")
        lines.append("")

    if diagnosis.downstream_effects:
        lines.append("## Downstream Effects and Business Risks")
        for item in diagnosis.downstream_effects:
            lines.append(f"- **{item.candidate_id}** {item.title} ({item.confidence:.2f})")
        lines.append("")

    # Evidence
    lines.append("## Evidence")
    for ev in diagnosis.evidence:
        ts = f" at {ev.timestamp}" if ev.timestamp else ""
        fld = f" [{ev.field}]" if ev.field else ""
        val = f" = {ev.value}" if ev.value else ""
        lines.append(f"- **{ev.id}** ({ev.source}{ts}): {ev.summary}{fld}{val}")

    # Evidence Graph
    if diagnosis.evidence_links:
        lines.append("")
        lines.append("## Evidence Graph")
        for link in diagnosis.evidence_links:
            lines.append(f"- {link.source_id} --[{link.relation}]--> {link.target_id}")

    # Actions
    lines.append("")
    lines.append("## Recommended Actions")
    for act in diagnosis.recommended_actions:
        role_tag = f" [{act.role}]" if act.role else ""
        lines.append(f"- **{act.action_id}** ({act.type}){role_tag}: {act.title}")
        lines.append(f"  {act.detail}")
        if act.linked_candidate_ids:
            lines.append(f"  Linked: {', '.join(act.linked_candidate_ids)}")

    # Work Order
    if diagnosis.work_order_draft:
        wo = diagnosis.work_order_draft
        lines.append("")
        lines.append("## Work Order Draft")
        lines.append(f"**{wo.title}** (priority: {wo.priority}, assignee: {wo.assignee_role})")
        lines.append("")
        lines.append("**Tasks:**")
        for t in wo.tasks:
            lines.append(f"  1. {t}")
        if wo.safety_notes:
            lines.append("**Safety:**")
            for s in wo.safety_notes:
                lines.append(f"  ⚠ {s}")

    # Value Estimates
    if diagnosis.value_estimates:
        lines.append("")
        lines.append("## Business Value Estimates")
        for ve in diagnosis.value_estimates:
            lines.append(f"### {ve.metric}")
            lines.append(f"- **Baseline**: {ve.baseline}")
            lines.append(f"- **Projected**: {ve.projected}")
            lines.append(f"- **Assumption**: {ve.assumption}")
            lines.append(f"- **Configured**: {'yes' if ve.configured else 'no'}")
            lines.append("")

    if diagnosis.agent_decisions:
        lines.append("## Agent Decisions")
        for decision in diagnosis.agent_decisions:
            lines.append(f"- **{decision.state}** -> `{decision.decision}`: {decision.reason}")
        lines.append("")

    # Postmortem
    lines.append("")
    lines.append("## Postmortem Summary")
    lines.append(diagnosis.postmortem_summary)

    lines.append("")
    lines.append("## Limitations")
    lines.extend(f"- {item}" for item in diagnosis.limitations)

    return "\n".join(lines) + "\n"
