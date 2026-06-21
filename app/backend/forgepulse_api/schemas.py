from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


DiagnosisStatus = Literal[
    "confirmed",
    "provisional",
    "insufficient_evidence",
    "conflicting_evidence",
]
DiagnosticRole = Literal[
    "equipment_cause",
    "coupled_secondary_factor",
    "quality_effect",
]


class Evidence(BaseModel):
    id: str
    source: str
    summary: str
    timestamp: str | None = None
    field: str | None = None
    value: str | None = None


class TimelineEvent(BaseModel):
    timestamp: str
    title: str
    detail: str
    severity: Literal["info", "warning", "major", "critical"] = "info"
    evidence_ids: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    alarm_match: float = 0.0
    sensor_correlation: float = 0.0
    sop_match: float = 0.0
    maintenance_similarity: float = 0.0
    operator_note_match: float = 0.0
    total: float = 0.0


class RootCauseCandidate(BaseModel):
    candidate_id: str
    title: str
    title_zh: str | None = None
    confidence: float
    priority: Literal["low", "medium", "high"]
    evidence_ids: list[str]
    rationale: str
    score_breakdown: ScoreBreakdown | None = None
    fault_mode_id: str | None = None
    diagnostic_role: DiagnosticRole = "equipment_cause"
    why_ranked: str = ""
    missing_evidence: list[str] = Field(default_factory=list)


class RecommendedAction(BaseModel):
    action_id: str
    title: str
    type: str
    linked_candidate_ids: list[str]
    detail: str
    role: str | None = None


class WorkOrderDraft(BaseModel):
    title: str
    priority: str
    assignee_role: str
    tasks: list[str]
    safety_notes: list[str]


class ProcessStep(BaseModel):
    step: str
    status: Literal["completed", "skipped", "error"]
    detail: str
    duration_ms: float | None = None


class DataQualityReport(BaseModel):
    sensor_rows: int
    alarm_events: int
    sop_sections: int
    maintenance_records: int
    missing_fields: list[str]
    warnings: list[str]
    invalid_fields: list[str] = Field(default_factory=list)
    completeness_score: float = 1.0


class EvidenceLink(BaseModel):
    source_id: str
    target_id: str
    relation: str


class ValueEstimate(BaseModel):
    metric: str
    baseline: str
    projected: str
    assumption: str
    configured: bool = False


class AgentDecision(BaseModel):
    state: str
    decision: str
    reason: str


class Diagnosis(BaseModel):
    case_id: str
    diagnosis_status: DiagnosisStatus = "provisional"
    incident_summary: str
    timeline: list[TimelineEvent]
    evidence: list[Evidence]
    root_cause_candidates: list[RootCauseCandidate]
    primary_root_cause: RootCauseCandidate | None = None
    contributing_factors: list[RootCauseCandidate] = Field(default_factory=list)
    downstream_effects: list[RootCauseCandidate] = Field(default_factory=list)
    business_risks: list[str] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    conflicting_evidence: list[str] = Field(default_factory=list)
    recommended_actions: list[RecommendedAction]
    work_order_draft: WorkOrderDraft
    postmortem_summary: str
    limitations: list[str]
    diagnostic_process: list[ProcessStep] = Field(default_factory=list)
    agent_decisions: list[AgentDecision] = Field(default_factory=list)
    evidence_links: list[EvidenceLink] = Field(default_factory=list)
    data_quality: DataQualityReport | None = None
    value_estimates: list[ValueEstimate] = Field(default_factory=list)
