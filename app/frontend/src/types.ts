export interface TimelineEvent {
  timestamp: string;
  title: string;
  detail: string;
  severity: "info" | "warning" | "major" | "critical";
  evidence_ids: string[];
}

export interface Evidence {
  id: string;
  source: string;
  summary: string;
  timestamp?: string;
  field?: string;
  value?: string;
}

export interface ScoreBreakdown {
  alarm_match: number;
  sensor_correlation: number;
  sop_match: number;
  maintenance_similarity: number;
  operator_note_match: number;
  total: number;
}

export type DiagnosticRole = "equipment_cause" | "coupled_secondary_factor" | "quality_effect";
export type DiagnosisStatus = "confirmed" | "provisional" | "insufficient_evidence" | "conflicting_evidence";

export interface RootCauseCandidate {
  candidate_id: string;
  title: string;
  title_zh?: string;
  confidence: number;
  priority: "low" | "medium" | "high";
  evidence_ids: string[];
  rationale: string;
  score_breakdown?: ScoreBreakdown;
  fault_mode_id?: string;
  diagnostic_role: DiagnosticRole;
  why_ranked: string;
  missing_evidence: string[];
}

export interface RecommendedAction {
  action_id: string;
  title: string;
  type: string;
  linked_candidate_ids: string[];
  detail: string;
  role?: string;
}

export interface WorkOrderDraft {
  title: string;
  priority: string;
  assignee_role: string;
  tasks: string[];
  safety_notes: string[];
}

export interface ProcessStep {
  step: string;
  status: "completed" | "skipped" | "error";
  detail: string;
  duration_ms?: number;
}

export interface AgentDecision {
  state: string;
  decision: string;
  reason: string;
}

export interface DataQualityReport {
  sensor_rows: number;
  alarm_events: number;
  sop_sections: number;
  maintenance_records: number;
  missing_fields: string[];
  warnings: string[];
  invalid_fields: string[];
  completeness_score: number;
}

export interface EvidenceLink {
  source_id: string;
  target_id: string;
  relation: string;
}

export interface ValueEstimate {
  metric: string;
  baseline: string;
  projected: string;
  assumption: string;
  configured: boolean;
}

export interface CandidateNote {
  candidate_id: string;
  rationale_refined: string;
  why_ranked_refined: string;
}

export interface AgentReasoning {
  mode: string;
  review_summary: string;
  candidate_notes: CandidateNote[];
  uncertainties: string[];
  safety_reaffirmation: string;
  referenced_evidence_ids: string[];
  warning: string | null;
}

export interface Diagnosis {
  case_id: string;
  diagnosis_status: DiagnosisStatus;
  incident_summary: string;
  timeline: TimelineEvent[];
  evidence: Evidence[];
  root_cause_candidates: RootCauseCandidate[];
  primary_root_cause?: RootCauseCandidate;
  contributing_factors: RootCauseCandidate[];
  downstream_effects: RootCauseCandidate[];
  business_risks: string[];
  missing_evidence: string[];
  conflicting_evidence: string[];
  recommended_actions: RecommendedAction[];
  work_order_draft: WorkOrderDraft;
  postmortem_summary: string;
  limitations: string[];
  diagnostic_process: ProcessStep[];
  agent_decisions: AgentDecision[];
  evidence_links: EvidenceLink[];
  data_quality?: DataQualityReport;
  value_estimates: ValueEstimate[];
  agent_reasoning?: AgentReasoning | null;
}

export interface CaseMeta {
  case_id: string;
  title: string;
  title_zh?: string;
  industry: string;
  line: string;
  station: string;
}
