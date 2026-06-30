import { AlertTriangle, CheckCircle2, Sparkles } from "lucide-react";
import type { Diagnosis } from "../types";
import { DECISION_LABEL } from "../lib/labels";
import { Section } from "./Section";

function AgentReview({ diagnosis }: { diagnosis: Diagnosis }) {
  const review = diagnosis.agent_reasoning;
  if (!review) return null;
  const isLLM = review.mode !== "offline";
  return (
    <section className={`agent-review-card ${isLLM ? "llm" : "offline"}`}>
      <header className="agent-review-header">
        <Sparkles size={15} />
        <h3>AI 复核</h3>
        <span className="agent-review-mode">{isLLM ? "LLM 推理" : "离线"}</span>
      </header>
      <div className="agent-review-body">
        {review.warning && (
          <p className="agent-review-warning"><AlertTriangle size={13} />{review.warning}</p>
        )}
        {review.review_summary && <p className="agent-review-summary">{review.review_summary}</p>}
        {review.uncertainties.length > 0 && (
          <div className="agent-review-uncertainties">
            <span className="agent-review-label">不确定性</span>
            <ul>{review.uncertainties.map((u, i) => <li key={i}>{u}</li>)}</ul>
          </div>
        )}
        {review.safety_reaffirmation && (
          <p className="agent-review-safety"><CheckCircle2 size={13} />{review.safety_reaffirmation}</p>
        )}
      </div>
    </section>
  );
}

export function DecisionLog({ diagnosis }: { diagnosis: Diagnosis }) {
  return (
    <>
      <AgentReview diagnosis={diagnosis} />
      <Section icon={<CheckCircle2 size={16} />} title="Agent 决策轨迹" className="agent-terminal-card">
        <div className="terminal-header">
          <span className="terminal-dot red" />
          <span className="terminal-dot yellow" />
          <span className="terminal-dot green" />
          <span className="terminal-title">agent_decision_trace.log</span>
          <span className="terminal-status"><span className="pulse-dot" />ACTIVE</span>
        </div>
        <ol className="decision-list">
          {diagnosis.agent_decisions.map((item, index) => (
            <li key={`${item.state}-${index}`}>
              <span className="terminal-prompt">&gt;</span>
              <code>{item.state}</code>
              <strong className={`decision-${item.decision}`}>
                {DECISION_LABEL[item.decision] ?? item.decision}
              </strong>
              <span className="terminal-reason">{item.reason}</span>
            </li>
          ))}
        </ol>
      </Section>
    </>
  );
}
