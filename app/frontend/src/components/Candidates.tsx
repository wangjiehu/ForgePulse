import { AlertTriangle, CircleHelp, Wrench } from "lucide-react";
import type { RootCauseCandidate } from "../types";
import { ROLE_LABEL, translateEvidenceIssue } from "../lib/labels";
import { Section, ScoreBar } from "./Section";
import { EvidenceTags } from "./EvidenceTags";

function CandidateCard({
  candidate,
  index,
  onFocus,
}: {
  candidate: RootCauseCandidate;
  index: number;
  onFocus: (id: string) => void;
}) {
  return (
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
        <strong className="confidence">{Math.round(candidate.confidence * 100)}%</strong>
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
        <EvidenceTags ids={candidate.evidence_ids} onFocus={onFocus} />
      </div>
      {candidate.missing_evidence.length > 0 && (
        <div className="candidate-missing">尚缺：{candidate.missing_evidence.map(translateEvidenceIssue).join("；")}</div>
      )}
    </article>
  );
}

export function Candidates({
  diagnosis,
  onFocus,
}: {
  diagnosis: import("../types").Diagnosis;
  onFocus: (id: string) => void;
}) {
  return (
    <Section icon={<Wrench size={16} />} title="根因与伴随因素">
      <div className="candidate-list">
        {diagnosis.root_cause_candidates.map((c, i) => (
          <CandidateCard key={c.candidate_id} candidate={c} index={i} onFocus={onFocus} />
        ))}
      </div>
      {diagnosis.downstream_effects.length > 0 && (
        <div className="downstream-block">
          <h4 className="downstream-title">
            <AlertTriangle size={14} />下游影响与质量风险
          </h4>
          <div className="effect-list">
            {diagnosis.downstream_effects.map((item) => (
              <div key={item.candidate_id}>
                <div>
                  <code>{item.candidate_id}</code>
                  <strong>{item.title_zh ?? item.title}</strong>
                </div>
                <EvidenceTags ids={item.evidence_ids} onFocus={onFocus} />
              </div>
            ))}
          </div>
        </div>
      )}
    </Section>
  );
}
