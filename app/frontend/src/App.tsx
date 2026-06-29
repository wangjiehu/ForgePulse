import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import {
  Activity,
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ChevronDown,
  ChevronRight,
  CircleHelp,
  Download,
  Factory,
  FileSearch,
  FileText,
  RefreshCw,
  ShieldCheck,
  Wrench,
} from "lucide-react";

interface TimelineEvent {
  timestamp: string;
  title: string;
  detail: string;
  severity: "info" | "warning" | "major" | "critical";
  evidence_ids: string[];
}

interface Evidence {
  id: string;
  source: string;
  summary: string;
  timestamp?: string;
  field?: string;
  value?: string;
}

interface ScoreBreakdown {
  alarm_match: number;
  sensor_correlation: number;
  sop_match: number;
  maintenance_similarity: number;
  operator_note_match: number;
  total: number;
}

type DiagnosticRole = "equipment_cause" | "coupled_secondary_factor" | "quality_effect";
type DiagnosisStatus = "confirmed" | "provisional" | "insufficient_evidence" | "conflicting_evidence";

interface RootCauseCandidate {
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

interface RecommendedAction {
  action_id: string;
  title: string;
  type: string;
  linked_candidate_ids: string[];
  detail: string;
  role?: string;
}

interface WorkOrderDraft {
  title: string;
  priority: string;
  assignee_role: string;
  tasks: string[];
  safety_notes: string[];
}

interface ProcessStep {
  step: string;
  status: "completed" | "skipped" | "error";
  detail: string;
}

interface AgentDecision {
  state: string;
  decision: string;
  reason: string;
}

interface DataQualityReport {
  sensor_rows: number;
  alarm_events: number;
  sop_sections: number;
  maintenance_records: number;
  missing_fields: string[];
  warnings: string[];
  invalid_fields: string[];
  completeness_score: number;
}

interface EvidenceLink {
  source_id: string;
  target_id: string;
  relation: string;
}

interface ValueEstimate {
  metric: string;
  baseline: string;
  projected: string;
  assumption: string;
  configured: boolean;
}

interface Diagnosis {
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
}

interface CaseMeta {
  case_id: string;
  title: string;
  title_zh?: string;
  industry: string;
  line: string;
  station: string;
}

const isProd = import.meta.env.PROD;
const API_BASE = isProd
  ? `${window.location.origin}${window.location.pathname.replace(/\/$/, "")}/api`
  : (import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000");

const USE_STATIC_API = isProd || import.meta.env.VITE_STATIC_API === "true";

const STATUS_LABEL: Record<DiagnosisStatus, string> = {
  confirmed: "\u8bc1\u636e\u5145\u5206",
  provisional: "\u6682\u5b9a\u8bca\u65ad",
  insufficient_evidence: "\u8bc1\u636e\u4e0d\u8db3",
  conflicting_evidence: "\u8bc1\u636e\u51b2\u7a81",
};

const ROLE_LABEL: Record<DiagnosticRole, string> = {
  equipment_cause: "\u8bbe\u5907\u6839\u56e0",
  coupled_secondary_factor: "\u4f34\u968f\u56e0\u7d20",
  quality_effect: "\u4e0b\u6e38\u5f71\u54cd",
};

const ACTION_LABEL: Record<string, string> = {
  collect_data: "\u8865\u91c7\u6570\u636e",
  inspect: "\u73b0\u573a\u68c0\u67e5",
  verify: "\u6838\u9a8c",
  quality: "\u8d28\u91cf\u5904\u7f6e",
  escalate: "\u5347\u7ea7\u901a\u77e5",
  safety: "\u5b89\u5168\u786e\u8ba4",
};

const OWNER_LABEL: Record<string, string> = {
  equipment_engineer: "\u8bbe\u5907\u5de5\u7a0b\u5e08",
  quality_engineer: "\u8d28\u91cf\u5de5\u7a0b\u5e08",
  production_supervisor: "\u751f\u4ea7\u4e3b\u7ba1",
  safety_reviewer: "\u5b89\u5168\u590d\u6838",
};

const DECISION_LABEL: Record<string, string> = {
  continue: "\u7ee7\u7eed",
  continue_with_caution: "\u8c28\u614e\u7ee7\u7eed",
  confirmed: "\u8bc1\u636e\u5145\u5206",
  provisional: "\u6682\u5b9a\u8bca\u65ad",
  insufficient_evidence: "\u505c\u6b62\u786e\u8ba4\uff0c\u8865\u5145\u8bc1\u636e",
  conflicting_evidence: "\u505c\u6b62\u5904\u7f6e\uff0c\u5148\u6838\u9a8c\u51b2\u7a81",
};

function translateEvidenceIssue(value: string) {
  return value
    .replace("critical sensor field:", "\u5173\u952e\u4f20\u611f\u5668\u5b57\u6bb5\uff1a")
    .replace("primary sensor anomaly:", "\u4e3b\u4f20\u611f\u5668\u5f02\u5e38\u8bc1\u636e\uff1a")
    .replace("primary alarm:", "\u4e3b\u62a5\u8b66\u8bc1\u636e\uff1a")
    .replace(
      /^alarms favor (.+), while sensor anomalies favor (.+)$/,
      "\u62a5\u8b66\u8bc1\u636e\u652f\u6301 $1\uff0c\u4f46\u4f20\u611f\u5668\u5f02\u5e38\u652f\u6301 $2",
    );
}

async function fetchCases(): Promise<CaseMeta[]> {
  const url = USE_STATIC_API ? `${API_BASE}/cases.json` : `${API_BASE}/cases`;
  const response = await fetch(url);
  if (!response.ok) throw new Error(`\u6848\u4f8b\u5217\u8868\u52a0\u8f7d\u5931\u8d25 (${response.status})`);
  return response.json();
}

async function fetchDiagnosis(caseId: string): Promise<Diagnosis> {
  const url = USE_STATIC_API
    ? `${API_BASE}/cases/${caseId}/diagnosis.json`
    : `${API_BASE}/cases/${caseId}/diagnosis`;
  const response = await fetch(url);
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = payload?.detail?.issues?.join("; ") ?? payload?.detail ?? response.status;
    throw new Error(`\u8bca\u65ad\u5931\u8d25\uff1a${detail}`);
  }
  return response.json();
}

function reportUrl(caseId: string) {
  return USE_STATIC_API
    ? `${API_BASE}/cases/${caseId}/report.md`
    : `${API_BASE}/cases/${caseId}/report`;
}

function formatTime(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function percentage(value: number) {
  return `${Math.round(value * 100)}%`;
}

function Section({
  icon,
  title,
  children,
  wide = false,
  scrollable = false,
  className = "",
}: {
  icon: ReactNode;
  title: string;
  children: ReactNode;
  wide?: boolean;
  scrollable?: boolean;
  className?: string;
}) {
  return (
    <section className={`section-block${wide ? " wide" : ""}${scrollable ? " scrollable" : ""} ${className}`}>
      <header className="section-header">
        {icon}
        <h3>{title}</h3>
      </header>
      <div className="section-body">{children}</div>
    </section>
  );
}

function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="score-row">
      <span>{label}</span>
      <div className="score-track">
        <div className="score-fill" style={{ width: percentage(value) }} />
      </div>
      <strong>{percentage(value)}</strong>
    </div>
  );
}

function EvidenceItem({
  evidence,
  open,
  focused,
  onToggle,
}: {
  evidence: Evidence;
  open: boolean;
  focused: boolean;
  onToggle: () => void;
}) {
  return (
    <article id={`evidence-${evidence.id}`} className={`evidence-item${focused ? " focused" : ""}`}>
      <button className="evidence-toggle" onClick={onToggle} aria-expanded={open}>
        {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        <code>{evidence.id}</code>
        <span>{evidence.source}</span>
      </button>
      {open && (
        <dl className="evidence-detail">
          {evidence.timestamp && (
            <>
              <dt>\u65f6\u95f4</dt>
              <dd>{evidence.timestamp}</dd>
            </>
          )}
          {evidence.field && (
            <>
              <dt>\u5b57\u6bb5</dt>
              <dd><code>{evidence.field}</code></dd>
            </>
          )}
          {evidence.value && (
            <>
              <dt>\u5024</dt>
              <dd>{evidence.value}</dd>
            </>
          )}
          <dt>\u6458\u8981</dt>
          <dd>{evidence.summary}</dd>
        </dl>
      )}
    </article>
  );
}

export default function App() {
  const [cases, setCases] = useState<CaseMeta[]>([]);
  const [selectedCase, setSelectedCase] = useState("");
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openEvidence, setOpenEvidence] = useState<Set<string>>(new Set());
  const [focusedEvidence, setFocusedEvidence] = useState<string | null>(null);

  useEffect(() => {
    fetchCases()
      .then((data) => {
        setCases(data);
        if (data.length > 0) {
          const requestedCase = new URLSearchParams(window.location.search).get("case");
          const initialCase = data.some((item) => item.case_id === requestedCase)
            ? requestedCase!
            : data[0].case_id;
          setSelectedCase((current) => current || initialCase);
        }
      })
      .catch((reason: Error) => setError(reason.message));
  }, []);

  const loadDiagnosis = useCallback(async (caseId: string) => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    setFocusedEvidence(null);
    setOpenEvidence(new Set());
    try {
      setDiagnosis(await fetchDiagnosis(caseId));
    } catch (reason) {
      setDiagnosis(null);
      setError(reason instanceof Error ? reason.message : "\u672a\u77e5\u9519\u8bef");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDiagnosis(selectedCase);
  }, [selectedCase, loadDiagnosis]);

  const selectedMeta = useMemo(
    () => cases.find((item) => item.case_id === selectedCase),
    [cases, selectedCase],
  );

  const localizedSummary = useMemo(() => {
    if (!diagnosis) return "";
    const title = selectedMeta?.title_zh || selectedMeta?.title || diagnosis.case_id;
    if (diagnosis.diagnosis_status === "insufficient_evidence") {
      return `${title}\u3002\u73b0\u6709\u8bc1\u636e\u4e0d\u8db3\u4ee5\u786e\u8ba4\u6839\u56e0\uff0c\u9700\u5148\u8865\u91c7\u5173\u952e\u6570\u636e\u3002`;
    }
    if (diagnosis.diagnosis_status === "conflicting_evidence") {
      return `${title}\u3002\u62a5\u8b66\u4e0e\u4f20\u611f\u5668\u8bc1\u636e\u4e0d\u4e00\u81f4\uff0c\u7ef4\u4fee\u524d\u5fc5\u987b\u5148\u6838\u9a8c\u4eea\u8868\u4e0e\u65f6\u95f4\u5bf9\u9f50\u3002`;
    }
    const primary = diagnosis.primary_root_cause?.title_zh ?? diagnosis.primary_root_cause?.title;
    return `${title}\u3002\u5f53\u524d\u4e3b\u6839\u56e0\uff1a${primary ?? "\u5c1a\u672a\u786e\u5b9a"}\u3002`;
  }, [diagnosis, selectedMeta]);

  const selectCase = useCallback((caseId: string) => {
    setSelectedCase(caseId);
    const url = new URL(window.location.href);
    url.searchParams.set("case", caseId);
    window.history.replaceState({}, "", url);
  }, []);

  const focusEvidence = useCallback((evidenceId: string) => {
    setFocusedEvidence(evidenceId);
    setOpenEvidence((current) => new Set(current).add(evidenceId));
    window.setTimeout(() => {
      document.getElementById(`evidence-${evidenceId}`)?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }, 20);
  }, []);

  const lineStatus = useMemo(() => {
    const status = {
      unwind: "normal",
      coater: "normal",
      dryer1: "normal",
      dryer2: "normal",
      tension: "normal",
      wind: "normal",
    };

    if (!diagnosis) return status;

    const alarmCodes = new Set(diagnosis.evidence.map(e => e.value).filter(Boolean));
    const anomalyFields = new Set(diagnosis.evidence.map(e => e.field).filter(Boolean));

    if (anomalyFields.has("dryer_zone_2_temp_c") || alarmCodes.has("DRY-122") || anomalyFields.has("fan_frequency_hz") || alarmCodes.has("AIR-305")) {
      status.dryer2 = diagnosis.diagnosis_status === "conflicting_evidence" ? "warning" : "critical";
    }
    if (anomalyFields.has("dryer_zone_1_temp_c") || alarmCodes.has("DRY-110")) {
      status.dryer1 = "warning";
    }
    if (anomalyFields.has("thickness_um") || alarmCodes.has("QCS-318")) {
      status.coater = "warning";
    }
    if (anomalyFields.has("web_tension_n") || alarmCodes.has("TEN-204") || anomalyFields.has("drive_current_a") || alarmCodes.has("DRV-410")) {
      status.tension = "critical";
    }

    return status;
  }, [diagnosis]);

  const renderEvidenceButtons = (ids: string[]) => (
    <span className="evidence-tags">
      {ids.map((id) => (
        <button key={id} className="evidence-tag" onClick={() => focusEvidence(id)} title="\u5b9a\u4f4d\u539f\u59cb\u8bc1\u636e">
          {id}
        </button>
      ))}
    </span>
  );

  const renderCandidate = (candidate: RootCauseCandidate, index: number) => (
    <article className="candidate-row" key={candidate.candidate_id}>
      <div className="candidate-heading">
        <span className="rank">#{index + 1}</span>
        <div>
          <div className="candidate-meta">
            <code>{candidate.candidate_id}</code>
            {candidate.fault_mode_id && <code>{candidate.fault_mode_id}</code>}
            <span className={`priority priority-${candidate.priority}`}>{candidate.priority}</span>
            <span>{ROLE_LABEL[candidate.diagnostic_role]}</span>
          </div>
          <h4>{candidate.title_zh ?? candidate.title}</h4>
          {candidate.title_zh && <small className="english-title">{candidate.title}</small>}
        </div>
        <strong className="confidence">{percentage(candidate.confidence)}</strong>
      </div>
      <p>{candidate.rationale}</p>
      <p className="why-ranked"><CircleHelp size={14} />{candidate.why_ranked}</p>
      {candidate.score_breakdown && (
        <div className="score-grid">
          <ScoreBar label="\u62a5\u8b66" value={candidate.score_breakdown.alarm_match} />
          <ScoreBar label="\u4f20\u611f\u5668" value={candidate.score_breakdown.sensor_correlation} />
          <ScoreBar label="SOP" value={candidate.score_breakdown.sop_match} />
          <ScoreBar label="\u7ef4\u4fee\u8bb0\u5f55" value={candidate.score_breakdown.maintenance_similarity} />
          <ScoreBar label="\u73b0\u573a\u63cf\u8ff0" value={candidate.score_breakdown.operator_note_match} />
        </div>
      )}
      <div className="candidate-evidence">
        <span>\u8bc1\u636e</span>
        {renderEvidenceButtons(candidate.evidence_ids)}
      </div>
      {candidate.missing_evidence.length > 0 && (
        <div className="candidate-missing">\u5c1a\u7f3a\uff1a{candidate.missing_evidence.map(translateEvidenceIssue).join("\uff1b")}</div>
      )}
    </article>
  );

  return (
    <main className="workspace">
      <aside className="sidebar">
        <div className="brand">
          <Factory size={28} />
          <div>
            <h1>ForgePulse</h1>
            <p>\u6d82\u5e03\u4ea7\u7ebf\u8bc1\u636e\u8bca\u65ad\u5de5\u4f5c\u53f0</p>
          </div>
        </div>

        <nav aria-label="\u8bca\u65ad\u6848\u4f8b">
          <h2>\u8bca\u65ad\u6848\u4f8b</h2>
          <div className="case-list">
            {cases.map((item) => (
              <button
                key={item.case_id}
                className={`case-button${selectedCase === item.case_id ? " active" : ""}`}
                onClick={() => selectCase(item.case_id)}
              >
                <span>{item.title_zh || item.title}</span>
                <code>{item.case_id}</code>
              </button>
            ))}
          </div>
        </nav>

        {diagnosis && (
          <section className="sidebar-metrics">
            <h2>\u5f53\u524d\u8bca\u65ad</h2>
            <div><span>\u72b6\u6001</span><strong>{STATUS_LABEL[diagnosis.diagnosis_status]}</strong></div>
            <div><span>\u6839\u56e0\u5019\u9009</span><strong>{diagnosis.root_cause_candidates.length}</strong></div>
            <div><span>\u8bc1\u636e</span><strong>{diagnosis.evidence.length}</strong></div>
            <div><span>\u52a8\u4f5c</span><strong>{diagnosis.recommended_actions.length}</strong></div>
            <div><span>\u8bc1\u636e\u5b8c\u6574\u5ea6</span><strong>{percentage(diagnosis.data_quality?.completeness_score ?? 0)}</strong></div>
          </section>
        )}
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <span className="eyebrow">{selectedMeta?.line ?? "\u672a\u9009\u62e9\u4ea7\u7ebf"} / {selectedMeta?.station ?? ""}</span>
            <h2>{selectedMeta?.title_zh || selectedMeta?.title || "\u8bf7\u9009\u62e9\u8bca\u65ad\u6848\u4f8b"}</h2>
          </div>
          <div className="toolbar">
            <button className="icon-command" onClick={() => void loadDiagnosis(selectedCase)} disabled={loading || !selectedCase} title="\u91cd\u65b0\u8bca\u65ad">
              <RefreshCw size={17} className={loading ? "spin" : ""} />
              <span>{loading ? "\u5206\u6790\u4e2d" : "\u91cd\u65b0\u8bca\u65ad"}</span>
            </button>
            <button className="icon-command" onClick={() => window.open(reportUrl(selectedCase), "_blank")} disabled={!selectedCase} title="\u5bfc\u51fa Markdown \u62a5\u544a">
              <Download size={17} />
              <span>\u5bfc\u51fa\u62a5\u544a</span>
            </button>
          </div>
        </header>

        {error && <div className="error-banner"><AlertTriangle size={18} />{error}</div>}
        {loading && !diagnosis && <div className="loading"><Activity className="spin" /><span>\u6b63\u5728\u6838\u9a8c\u6570\u636e\u3001\u62a5\u8b66\u548c\u7ef4\u4fee\u8bc1\u636e</span></div>}

        {diagnosis && (
          <div className="dashboard-body">
            {/* Top Row: Decision Banner + Process Map */}
            <div className="dashboard-row-top">
              <section className={`decision-banner status-${diagnosis.diagnosis_status}`}>
                <div>
                  <span>\u8bca\u65ad\u72b6\u6001</span>
                  <strong>{STATUS_LABEL[diagnosis.diagnosis_status]}</strong>
                </div>
                <p>{localizedSummary}</p>
              </section>

              <section className="process-map-card section-block">
                <header className="section-header">
                  <Factory size={16} />
                  <h3>\u6781\u7247\u6d82\u5e03\u4ea7\u7ebf\u7269\u7406\u76d1\u6d4b\u56fe (Coating Line Process Map)</h3>
                </header>
                <div className="process-map-body">
                  <div className="process-flow">
                    <div className={`process-node status-${lineStatus.unwind}`}>
                      <div className="node-icon">\u{1F300}</div>
                      <span className="node-name">\u653e\u5377 (Unwind)</span>
                      <span className="node-status">\u6b63\u5e38</span>
                    </div>
                    <div className="flow-arrow">&#10148;</div>
                    
                    <div className={`process-node status-${lineStatus.coater}`}>
                      <div className="node-icon">&#9881;&#65039;</div>
                      <span className="node-name">\u6d82\u5e03/QCS</span>
                      <span className="node-status">{lineStatus.coater === "normal" ? "\u6b63\u5e38" : "\u539a\u5ea6\u6f02\u79fb"}</span>
                    </div>
                    <div className="flow-arrow">&#10148;</div>

                    <div className={`process-node status-${lineStatus.dryer1}`}>
                      <div className="node-icon">\u{1F525}</div>
                      <span className="node-name">\u5e72\u71e5\u4e00\u533a (Z1)</span>
                      <span className="node-status">{lineStatus.dryer1 === "normal" ? "\u6b63\u5e38" : "\u6e29\u5347\u5f02\u5e38"}</span>
                    </div>
                    <div className="flow-arrow">&#10148;</div>

                    <div className={`process-node status-${lineStatus.dryer2}`}>
                      <div className="node-icon">\u{1F525}</div>
                      <span className="node-name">\u5e72\u71e5\u4e8c\u533a (Z2)</span>
                      <span className="node-status">{lineStatus.dryer2 === "normal" ? "\u6b63\u5e38" : "\u6e29\u63a7\u504f\u5dee"}</span>
                    </div>
                    <div className="flow-arrow">&#10148;</div>

                    <div className={`process-node status-${lineStatus.tension}`}>
                      <div className="node-icon">\u{1F504}</div>
                      <span className="node-name">\u5f20\u529b\u9a71\u52a8 (Tension)</span>
                      <span className="node-status">{lineStatus.tension === "normal" ? "\u6b63\u5e38" : "\u963b\u529b\u504f\u5927"}</span>
                    </div>
                    <div className="flow-arrow">&#10148;</div>

                    <div className={`process-node status-${lineStatus.wind}`}>
                      <div className="node-icon">\u{1F300}</div>
                      <span className="node-name">\u6536\u5377 (Wind)</span>
                      <span className="node-status">\u6b63\u5e38</span>
                    </div>
                  </div>
                </div>
              </section>
            </div>

            {/* Bottom Row: 3 Columns */}
            <div className="dashboard-grid-columns">
              {/* Column 1: Causal Evidence Map + Timeline + Raw Evidence */}
              <div className="dashboard-column">
                <section className="evidence-map-card section-block">
                  <header className="section-header">
                    <FileSearch size={16} />
                    <h3>\u8bca\u65ad\u56e0\u679c\u8bc1\u636e\u7f51\u7edc\u56fe (Causal Evidence Map)</h3>
                  </header>
                  <div className="evidence-map-body">
                    <div className="evidence-map-workspace">
                      <div className="map-column">
                        <span className="column-title">\u6839\u56e0 (Candidates)</span>
                        <div className="map-nodes">
                          {diagnosis.root_cause_candidates.slice(0, 2).map((rc) => (
                            <div key={rc.candidate_id} className={`map-node candidate-node priority-${rc.priority}`}>
                              <div className="node-header">
                                <code>{rc.candidate_id}</code>
                                <strong>{rc.title_zh || rc.title}</strong>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      <div className="map-connector-column">
                        <div className="connector-path"></div>
                      </div>

                      <div className="map-column">
                        <span className="column-title">\u5173\u8054\u8bc1\u636e (Evidence)</span>
                        <div className="map-nodes">
                          {diagnosis.evidence.slice(0, 4).map((ev) => {
                            const isAlarm = ev.source.includes("alarm");
                            const isSensor = ev.source.includes("sensor");
                            const typeClass = isAlarm ? "alarm" : isSensor ? "sensor" : "record";
                            return (
                              <button
                                key={ev.id}
                                className={`map-node evidence-node type-${typeClass}`}
                                onClick={() => focusEvidence(ev.id)}
                                title="\u70b9\u51fb\u5b9a\u4f4d\u5230\u4e0b\u65b9\u539f\u59cb\u6570\u636e"
                              >
                                <code>{ev.id}</code>
                                <span>{ev.summary}</span>
                              </button>
                            );
                          })}
                          {diagnosis.evidence.length > 4 && (
                            <div className="map-nodes-more">
                              + \u8fd8\u6709 {diagnosis.evidence.length - 4} \u9879\u5173\u8054
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="map-connector-column">
                        <div className="connector-path"></div>
                      </div>

                      <div className="map-column">
                        <span className="column-title">\u6570\u636e\u6e90 (Sources)</span>
                        <div className="map-nodes">
                          {Array.from(new Set(diagnosis.evidence.map((e) => e.source))).slice(0, 3).map((source) => (
                            <div key={source} className="map-node source-node">
                              <FileText size={12} />
                              <span>{source}</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                </section>

                <Section icon={<Activity size={16} />} title="\u4e8b\u4ef6\u65f6\u95f4\u7ebf" scrollable>
                  <div className="timeline">
                    {diagnosis.timeline.map((item, index) => (
                      <div className="timeline-row" key={`${item.timestamp}-${index}`}>
                        <time>{formatTime(item.timestamp)}</time>
                        <span className={`severity severity-${item.severity}`}>{item.severity}</span>
                        <div>
                          <strong>{item.title}</strong>
                          <p>{item.detail}</p>
                          {renderEvidenceButtons(item.evidence_ids)}
                        </div>
                      </div>
                    ))}
                  </div>
                </Section>

                <Section icon={<FileText size={16} />} title="\u539f\u59cb\u8bc1\u636e" scrollable>
                  <div className="evidence-list">
                    {diagnosis.evidence.map((item) => (
                      <EvidenceItem
                        key={item.id}
                        evidence={item}
                        open={openEvidence.has(item.id)}
                        focused={focusedEvidence === item.id}
                        onToggle={() => setOpenEvidence((current) => {
                          const next = new Set(current);
                          if (next.has(item.id)) next.delete(item.id);
                          else next.add(item.id);
                          return next;
                        })}
                      />
                    ))}
                  </div>
                </Section>
              </div>

              {/* Column 2: Data Quality + Alerts + Root Cause Candidates */}
              <div className="dashboard-column">
                {diagnosis.primary_root_cause && (
                  <div className="primary-finding-compact">
                    <div>
                      <span>\u4e3b\u6839\u56e0</span>
                      <h4>{diagnosis.primary_root_cause.title_zh ?? diagnosis.primary_root_cause.title}</h4>
                      <p>{diagnosis.primary_root_cause.why_ranked}</p>
                    </div>
                    <strong>{percentage(diagnosis.primary_root_cause.confidence)}</strong>
                  </div>
                )}

                {(diagnosis.missing_evidence.length > 0 || diagnosis.conflicting_evidence.length > 0) && (
                  <section className="evidence-alerts" style={{ flex: "0 0 auto", margin: 0, display: "flex", flexDirection: "column", gap: "6px" }}>
                    {diagnosis.missing_evidence.length > 0 && (
                      <div style={{ padding: "8px 12px", background: "#fef3c7", borderLeft: "3px solid #d97706", borderRadius: "6px", display: "flex", gap: "8px", alignItems: "center", fontSize: "11px" }}>
                        <FileSearch size={14} style={{ color: "#d97706" }} />
                        <span><strong>\u7f3a\u5931\uff1a</strong>{diagnosis.missing_evidence.map(translateEvidenceIssue).join("\uff1b")}</span>
                      </div>
                    )}
                    {diagnosis.conflicting_evidence.length > 0 && (
                      <div style={{ padding: "8px 12px", background: "#fee2e2", borderLeft: "3px solid #dc2626", borderRadius: "6px", display: "flex", gap: "8px", alignItems: "center", fontSize: "11px" }}>
                        <AlertTriangle size={14} style={{ color: "#dc2626" }} />
                        <span><strong>\u51b2\u7a81\uff1a</strong>{diagnosis.conflicting_evidence.map(translateEvidenceIssue).join("\uff1b")}</span>
                      </div>
                    )}
                  </section>
                )}

                <section className="data-quality-card section-block">
                  <header className="section-header">
                    <BarChart3 size={16} />
                    <h3>\u6570\u636e\u76d1\u6d4b\u8d28\u91cf (Data Quality)</h3>
                  </header>
                  <div className="section-body">
                    <div className="quality-metrics">
                      <div><span>\u4f20\u611f\u5668\u884c</span><strong>{diagnosis.data_quality?.sensor_rows ?? 0}</strong></div>
                      <div><span>\u62a5\u8b66\u4e8b\u4ef6</span><strong>{diagnosis.data_quality?.alarm_events ?? 0}</strong></div>
                      <div><span>SOP \u7ae0\u8282</span><strong>{diagnosis.data_quality?.sop_sections ?? 0}</strong></div>
                      <div><span>\u7ef4\u4fee\u8bb0\u5f55</span><strong>{diagnosis.data_quality?.maintenance_records ?? 0}</strong></div>
                    </div>
                  </div>
                </section>

                <Section icon={<Wrench size={16} />} title="\u6839\u56e0\u4e0e\u4f34\u968f\u56e0\u7d20" scrollable>
                  <div className="candidate-list">
                    {diagnosis.root_cause_candidates.map(renderCandidate)}
                  </div>
                  {diagnosis.downstream_effects.length > 0 && (
                    <div style={{ marginTop: "14px", borderTop: "1px dashed #cbd5e1", paddingTop: "12px" }}>
                      <h4 style={{ fontSize: "12px", margin: "0 0 8px", display: "flex", alignItems: "center", gap: "6px", color: "#475569" }}>
                        <AlertTriangle size={14} />\u4e0b\u6e38\u5f71\u54cd\u4e0e\u8d28\u91cf\u98ce\u9669
                      </h4>
                      <div className="effect-list">
                        {diagnosis.downstream_effects.map((item) => (
                          <div key={item.candidate_id}>
                            <div>
                              <code>{item.candidate_id}</code>
                              <strong>{item.title_zh ?? item.title}</strong>
                            </div>
                            {renderEvidenceButtons(item.evidence_ids)}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </Section>
              </div>

              {/* Column 3: Agent decisions + Recommended Actions / Work Order / Estimates / Review */}
              <div className="dashboard-column">
                <Section icon={<CheckCircle2 size={16} />} title="Agent \u51b3\u7b56\u8f68\u8ff9" scrollable className="agent-terminal-card">
                  <div className="terminal-header">
                    <span className="terminal-dot red"></span>
                    <span className="terminal-dot yellow"></span>
                    <span className="terminal-dot green"></span>
                    <span className="terminal-title">agent_decision_trace.log</span>
                    <span className="terminal-status"><span className="pulse-dot"></span>ACTIVE</span>
                  </div>
                  <ol className="decision-list terminal-style">
                    {diagnosis.agent_decisions.map((item, index) => (
                      <li key={`${item.state}-${index}`}>
                        <span className="terminal-prompt">&gt;</span>
                        <code>{item.state}</code>
                        <strong className={`decision-${item.decision}`}>{DECISION_LABEL[item.decision] ?? item.decision}</strong>
                        <span className="terminal-reason">{item.reason}</span>
                      </li>
                    ))}
                  </ol>
                </Section>

                <Section icon={<ShieldCheck size={16} />} title="\u5904\u7f6e\u65b9\u6848\u4e0e\u5de5\u5355" scrollable className="actions-workorder-card">
                  <div className="actions-work-order-scroll-container">
                    <div className="action-list">
                      {diagnosis.recommended_actions.map((item) => (
                        <article key={item.action_id} style={{ margin: 0 }}>
                          <div>
                            <span>{ACTION_LABEL[item.type] ?? item.type}</span>
                            <code>{item.action_id}</code>
                            <strong>{OWNER_LABEL[item.role ?? ""] ?? item.role ?? "\u5f85\u5206\u914d"}</strong>
                          </div>
                          <h4>{item.title}</h4>
                          <p>{item.detail}</p>
                        </article>
                      ))}
                    </div>

                    <div className="work-order" style={{ margin: 0 }}>
                      <div><strong>{diagnosis.work_order_draft.title}</strong><span>{diagnosis.work_order_draft.priority}</span></div>
                      <p>\u8d23\u4efb\u89d2\u8272\uff1a{OWNER_LABEL[diagnosis.work_order_draft.assignee_role] ?? diagnosis.work_order_draft.assignee_role}</p>
                      <ol>{diagnosis.work_order_draft.tasks.map((item, index) => <li key={index}>{item}</li>)}</ol>
                      <ul className="safety-list">{diagnosis.work_order_draft.safety_notes.map((item) => <li key={item}>{item}</li>)}</ul>
                    </div>

                    {diagnosis.value_estimates.length > 0 && (
                      <div className="value-section" style={{ borderTop: "1px dashed #cbd5e1", paddingTop: "12px" }}>
                        <h4 style={{ fontSize: "12px", margin: "0 0 8px", color: "#475569" }}>\u8bd5\u70b9\u4ef7\u5024\u6d4b\u7b97</h4>
                        <div className="value-grid">
                          {diagnosis.value_estimates.map((item) => (
                            <article key={item.metric} style={{ margin: 0 }}>
                              <h4>{item.metric}</h4>
                              <dl>
                                <dt>\u57fa\u7ebf</dt><dd>{item.baseline}</dd>
                                <dt>\u6d4b\u7b97</dt><dd>{item.projected}</dd>
                                <dt>\u5047\u8bbe</dt><dd>{item.assumption}</dd>
                              </dl>
                            </article>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="review-band" style={{ margin: 0, gridTemplateColumns: "1fr", gap: "12px", background: "#263d3d", padding: "12px", borderRadius: "8px" }}>
                      <div><h3 style={{ fontSize: "12px", color: "#ffffff", margin: "0 0 4px" }}>\u590d\u76d8\u6458\u8981</h3><p style={{ margin: 0, fontSize: "11px", color: "#c0d0cd" }}>{diagnosis.postmortem_summary}</p></div>
                      <div><h3 style={{ fontSize: "12px", color: "#ffffff", margin: "0 0 4px" }}>\u4f7f\u7528\u8fb9\u754c</h3><ul style={{ margin: 0, paddingLeft: "14px", fontSize: "11px", color: "#c0d0cd" }}>{diagnosis.limitations.map((item) => <li key={item}>{item}</li>)}</ul></div>
                    </div>
                  </div>
                </Section>
              </div>
            </div>
          </div>
        )}
      </section>
    </main>
  );
}
