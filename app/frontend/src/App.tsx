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

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

const STATUS_LABEL: Record<DiagnosisStatus, string> = {
  confirmed: "证据充分",
  provisional: "暂定诊断",
  insufficient_evidence: "证据不足",
  conflicting_evidence: "证据冲突",
};

const ROLE_LABEL: Record<DiagnosticRole, string> = {
  equipment_cause: "设备根因",
  coupled_secondary_factor: "伴随因素",
  quality_effect: "下游影响",
};

const ACTION_LABEL: Record<string, string> = {
  collect_data: "补采数据",
  inspect: "现场检查",
  verify: "核验",
  quality: "质量处置",
  escalate: "升级通知",
  safety: "安全确认",
};

const OWNER_LABEL: Record<string, string> = {
  equipment_engineer: "设备工程师",
  quality_engineer: "质量工程师",
  production_supervisor: "生产主管",
  safety_reviewer: "安全复核",
};

const DECISION_LABEL: Record<string, string> = {
  continue: "继续",
  continue_with_caution: "谨慎继续",
  confirmed: "证据充分",
  provisional: "暂定诊断",
  insufficient_evidence: "停止确认，补充证据",
  conflicting_evidence: "停止处置，先核验冲突",
};

function translateEvidenceIssue(value: string) {
  return value
    .replace("critical sensor field:", "关键传感器字段：")
    .replace("primary sensor anomaly:", "主传感器异常证据：")
    .replace("primary alarm:", "主报警证据：")
    .replace(
      /^alarms favor (.+), while sensor anomalies favor (.+)$/,
      "报警证据支持 $1，但传感器异常支持 $2",
    );
}

async function fetchCases(): Promise<CaseMeta[]> {
  const response = await fetch(`${API_BASE}/cases`);
  if (!response.ok) throw new Error(`案例列表加载失败 (${response.status})`);
  return response.json();
}

async function fetchDiagnosis(caseId: string): Promise<Diagnosis> {
  const response = await fetch(`${API_BASE}/cases/${caseId}/diagnosis`);
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail = payload?.detail?.issues?.join("; ") ?? payload?.detail ?? response.status;
    throw new Error(`诊断失败：${detail}`);
  }
  return response.json();
}

function reportUrl(caseId: string) {
  return `${API_BASE}/cases/${caseId}/report`;
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
}: {
  icon: ReactNode;
  title: string;
  children: ReactNode;
  wide?: boolean;
}) {
  return (
    <section className={`section-block${wide ? " wide" : ""}`}>
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
              <dt>时间</dt>
              <dd>{evidence.timestamp}</dd>
            </>
          )}
          {evidence.field && (
            <>
              <dt>字段</dt>
              <dd><code>{evidence.field}</code></dd>
            </>
          )}
          {evidence.value && (
            <>
              <dt>值</dt>
              <dd>{evidence.value}</dd>
            </>
          )}
          <dt>摘要</dt>
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
      setError(reason instanceof Error ? reason.message : "未知错误");
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
      return `${title}。现有证据不足以确认根因，需先补采关键数据。`;
    }
    if (diagnosis.diagnosis_status === "conflicting_evidence") {
      return `${title}。报警与传感器证据不一致，维修前必须先核验仪表与时间对齐。`;
    }
    const primary = diagnosis.primary_root_cause?.title_zh ?? diagnosis.primary_root_cause?.title;
    return `${title}。当前主根因：${primary ?? "尚未确定"}。`;
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

  const renderEvidenceButtons = (ids: string[]) => (
    <span className="evidence-tags">
      {ids.map((id) => (
        <button key={id} className="evidence-tag" onClick={() => focusEvidence(id)} title="定位原始证据">
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
          <ScoreBar label="报警" value={candidate.score_breakdown.alarm_match} />
          <ScoreBar label="传感器" value={candidate.score_breakdown.sensor_correlation} />
          <ScoreBar label="SOP" value={candidate.score_breakdown.sop_match} />
          <ScoreBar label="维修记录" value={candidate.score_breakdown.maintenance_similarity} />
          <ScoreBar label="现场描述" value={candidate.score_breakdown.operator_note_match} />
        </div>
      )}
      <div className="candidate-evidence">
        <span>证据</span>
        {renderEvidenceButtons(candidate.evidence_ids)}
      </div>
      {candidate.missing_evidence.length > 0 && (
        <div className="candidate-missing">尚缺：{candidate.missing_evidence.map(translateEvidenceIssue).join("；")}</div>
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
            <p>涂布产线证据诊断工作台</p>
          </div>
        </div>

        <nav aria-label="诊断案例">
          <h2>诊断案例</h2>
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
            <h2>当前诊断</h2>
            <div><span>状态</span><strong>{STATUS_LABEL[diagnosis.diagnosis_status]}</strong></div>
            <div><span>根因候选</span><strong>{diagnosis.root_cause_candidates.length}</strong></div>
            <div><span>证据</span><strong>{diagnosis.evidence.length}</strong></div>
            <div><span>动作</span><strong>{diagnosis.recommended_actions.length}</strong></div>
            <div><span>证据完整度</span><strong>{percentage(diagnosis.data_quality?.completeness_score ?? 0)}</strong></div>
          </section>
        )}
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <span className="eyebrow">{selectedMeta?.line ?? "未选择产线"} / {selectedMeta?.station ?? ""}</span>
            <h2>{selectedMeta?.title_zh || selectedMeta?.title || "请选择诊断案例"}</h2>
          </div>
          <div className="toolbar">
            <button className="icon-command" onClick={() => void loadDiagnosis(selectedCase)} disabled={loading || !selectedCase} title="重新诊断">
              <RefreshCw size={17} className={loading ? "spin" : ""} />
              <span>{loading ? "分析中" : "重新诊断"}</span>
            </button>
            <button className="icon-command" onClick={() => window.open(reportUrl(selectedCase), "_blank")} disabled={!selectedCase} title="导出 Markdown 报告">
              <Download size={17} />
              <span>导出报告</span>
            </button>
          </div>
        </header>

        {error && <div className="error-banner"><AlertTriangle size={18} />{error}</div>}
        {loading && !diagnosis && <div className="loading"><Activity className="spin" /><span>正在核验数据、报警和维修证据</span></div>}

        {diagnosis && (
          <>
            <section className={`decision-banner status-${diagnosis.diagnosis_status}`}>
              <div>
                <span>诊断状态</span>
                <strong>{STATUS_LABEL[diagnosis.diagnosis_status]}</strong>
              </div>
              <p>{localizedSummary}</p>
            </section>

            {(diagnosis.missing_evidence.length > 0 || diagnosis.conflicting_evidence.length > 0) && (
              <section className="evidence-alerts">
                {diagnosis.missing_evidence.length > 0 && (
                  <div>
                    <FileSearch size={18} />
                    <span><strong>缺失证据</strong>{diagnosis.missing_evidence.map(translateEvidenceIssue).join("；")}</span>
                  </div>
                )}
                {diagnosis.conflicting_evidence.length > 0 && (
                  <div>
                    <AlertTriangle size={18} />
                    <span><strong>冲突证据</strong>{diagnosis.conflicting_evidence.map(translateEvidenceIssue).join("；")}</span>
                  </div>
                )}
              </section>
            )}

            {diagnosis.primary_root_cause && (
              <section className="primary-finding">
                <div>
                  <span>主根因</span>
                  <h3>{diagnosis.primary_root_cause.title_zh ?? diagnosis.primary_root_cause.title}</h3>
                  {diagnosis.primary_root_cause.title_zh && <small>{diagnosis.primary_root_cause.title}</small>}
                  <p>{diagnosis.primary_root_cause.why_ranked}</p>
                </div>
                <strong>{percentage(diagnosis.primary_root_cause.confidence)}</strong>
              </section>
            )}

            <div className="section-grid">
              <Section icon={<CheckCircle2 size={19} />} title="Agent 决策轨迹">
                <ol className="decision-list">
                  {diagnosis.agent_decisions.map((item, index) => (
                    <li key={`${item.state}-${index}`}>
                      <code>{item.state}</code>
                      <strong>{DECISION_LABEL[item.decision] ?? item.decision}</strong>
                      <span>{item.reason}</span>
                    </li>
                  ))}
                </ol>
              </Section>

              <Section icon={<BarChart3 size={19} />} title="数据质量">
                <div className="quality-metrics">
                  <div><span>传感器行</span><strong>{diagnosis.data_quality?.sensor_rows ?? 0}</strong></div>
                  <div><span>报警事件</span><strong>{diagnosis.data_quality?.alarm_events ?? 0}</strong></div>
                  <div><span>SOP 章节</span><strong>{diagnosis.data_quality?.sop_sections ?? 0}</strong></div>
                  <div><span>维修记录</span><strong>{diagnosis.data_quality?.maintenance_records ?? 0}</strong></div>
                </div>
                {(diagnosis.data_quality?.warnings.length ?? 0) > 0 && (
                  <ul className="warning-list">
                    {diagnosis.data_quality?.warnings.map((item) => <li key={item}>{item}</li>)}
                  </ul>
                )}
              </Section>

              <Section icon={<Activity size={19} />} title="事件时间线">
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

              <Section icon={<Wrench size={19} />} title="根因与伴随因素">
                <div className="candidate-list">
                  {diagnosis.root_cause_candidates.map(renderCandidate)}
                </div>
              </Section>

              {diagnosis.downstream_effects.length > 0 && (
                <Section icon={<AlertTriangle size={19} />} title="下游影响与质量风险" wide>
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
                </Section>
              )}

              <Section icon={<FileText size={19} />} title="原始证据" wide>
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

              <Section icon={<ShieldCheck size={19} />} title="角色化处置动作">
                <div className="action-list">
                  {diagnosis.recommended_actions.map((item) => (
                    <article key={item.action_id}>
                      <div>
                        <span>{ACTION_LABEL[item.type] ?? item.type}</span>
                        <code>{item.action_id}</code>
                        <strong>{OWNER_LABEL[item.role ?? ""] ?? item.role ?? "待分配"}</strong>
                      </div>
                      <h4>{item.title}</h4>
                      <p>{item.detail}</p>
                    </article>
                  ))}
                </div>
              </Section>

              <Section icon={<FileText size={19} />} title="维修工单草案">
                <div className="work-order">
                  <div><strong>{diagnosis.work_order_draft.title}</strong><span>{diagnosis.work_order_draft.priority}</span></div>
                  <p>责任角色：{OWNER_LABEL[diagnosis.work_order_draft.assignee_role] ?? diagnosis.work_order_draft.assignee_role}</p>
                  <ol>{diagnosis.work_order_draft.tasks.map((item, index) => <li key={index}>{item}</li>)}</ol>
                  <ul className="safety-list">{diagnosis.work_order_draft.safety_notes.map((item) => <li key={item}>{item}</li>)}</ul>
                </div>
              </Section>

              {diagnosis.value_estimates.length > 0 && (
                <Section icon={<BarChart3 size={19} />} title="试点价值测算" wide>
                  <div className="value-grid">
                    {diagnosis.value_estimates.map((item) => (
                      <article key={item.metric}>
                        <h4>{item.metric}</h4>
                        <dl>
                          <dt>基线</dt><dd>{item.baseline}</dd>
                          <dt>测算</dt><dd>{item.projected}</dd>
                          <dt>假设</dt><dd>{item.assumption}</dd>
                        </dl>
                      </article>
                    ))}
                  </div>
                </Section>
              )}
            </div>

            <section className="review-band">
              <div><h3>复盘摘要</h3><p>{diagnosis.postmortem_summary}</p></div>
              <div><h3>使用边界</h3><ul>{diagnosis.limitations.map((item) => <li key={item}>{item}</li>)}</ul></div>
            </section>
          </>
        )}
      </section>
    </main>
  );
}
