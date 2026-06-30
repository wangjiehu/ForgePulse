import type { AgentReasoning, CaseMeta, Diagnosis } from "../types";

export function makeCase(over: Partial<CaseMeta> = {}): CaseMeta {
  return {
    case_id: "CASE-001",
    title: "Dryer tension drift",
    title_zh: "干燥张力漂移",
    industry: "battery",
    line: "coating-1",
    station: "dryer",
    ...over,
  };
}

export function makeDiagnosis(over: Partial<Diagnosis> = {}): Diagnosis {
  return {
    case_id: "CASE-001",
    diagnosis_status: "confirmed",
    incident_summary: "Primary root cause: dryer zone 2 temperature drift.",
    timeline: [
      {
        timestamp: "2024-03-17T08:00:00Z",
        title: "温度异常",
        detail: "干燥二区温度偏离阈值",
        severity: "major",
        evidence_ids: ["EV-1"],
      },
    ],
    evidence: [
      { id: "EV-1", source: "alarm", summary: "DRY-122 raised", value: "DRY-122" },
      { id: "EV-2", source: "sensor", summary: "dryer zone 2 temp high", field: "dryer_zone_2_temp_c" },
    ],
    root_cause_candidates: [
      {
        candidate_id: "RC-1",
        title: "Dryer zone 2 temperature control drift",
        title_zh: "干燥二区温控偏差",
        confidence: 0.91,
        priority: "high",
        evidence_ids: ["EV-1", "EV-2"],
        rationale: "Sensor and alarm evidence converge on zone 2.",
        diagnostic_role: "equipment_cause",
        why_ranked: "Highest score across alarm and sensor dimensions.",
        missing_evidence: [],
      },
    ],
    primary_root_cause: {
      candidate_id: "RC-1",
      title: "Dryer zone 2 temperature control drift",
      title_zh: "干燥二区温控偏差",
      confidence: 0.91,
      priority: "high",
      evidence_ids: ["EV-1", "EV-2"],
      rationale: "Sensor and alarm evidence converge on zone 2.",
      diagnostic_role: "equipment_cause",
      why_ranked: "Highest score across alarm and sensor dimensions.",
      missing_evidence: [],
    },
    contributing_factors: [],
    downstream_effects: [],
    business_risks: [],
    missing_evidence: [],
    conflicting_evidence: [],
    recommended_actions: [
      { action_id: "ACT-1", title: "Inspect heater", type: "inspect", linked_candidate_ids: ["RC-1"], detail: "Check zone 2 heater.", role: "equipment_engineer" },
    ],
    work_order_draft: { title: "WO-1", priority: "high", assignee_role: "equipment_engineer", tasks: ["Inspect"], safety_notes: ["Lockout"] },
    postmortem_summary: "Likely originated from zone 2 drift.",
    limitations: ["Deterministic analysis only – no LLM reasoning applied."],
    diagnostic_process: [],
    agent_decisions: [
      { state: "load", decision: "continue", reason: "loaded" },
      { state: "assess_evidence", decision: "confirmed", reason: "sufficient" },
    ],
    evidence_links: [],
    value_estimates: [],
    ...over,
  };
}

export function makeReasoning(over: Partial<AgentReasoning> = {}): AgentReasoning {
  return {
    mode: "openai_compatible",
    review_summary: "Evidence supports the primary candidate.",
    candidate_notes: [{ candidate_id: "RC-1", rationale_refined: "refined", why_ranked_refined: "refined why" }],
    uncertainties: ["Confirm fan inspection record."],
    safety_reaffirmation: "Confirm with engineer before repair.",
    referenced_evidence_ids: ["EV-1"],
    warning: null,
    ...over,
  };
}
