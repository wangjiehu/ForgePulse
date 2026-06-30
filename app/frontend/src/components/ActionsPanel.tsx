import { ShieldCheck } from "lucide-react";
import type { Diagnosis } from "../types";
import { ACTION_LABEL, OWNER_LABEL } from "../lib/labels";
import { Section } from "./Section";

export function ActionsPanel({ diagnosis }: { diagnosis: Diagnosis }) {
  return (
    <Section icon={<ShieldCheck size={16} />} title="处置方案与工单" className="actions-workorder-card">
      <div className="actions-work-order-scroll-container">
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

        <div className="work-order">
          <div>
            <strong>{diagnosis.work_order_draft.title}</strong>
            <span>{diagnosis.work_order_draft.priority}</span>
          </div>
          <p>责任角色：{OWNER_LABEL[diagnosis.work_order_draft.assignee_role] ?? diagnosis.work_order_draft.assignee_role}</p>
          <ol>{diagnosis.work_order_draft.tasks.map((item, index) => <li key={index}>{item}</li>)}</ol>
          <ul className="safety-list">
            {diagnosis.work_order_draft.safety_notes.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </div>

        {diagnosis.value_estimates.length > 0 && (
          <div className="value-section">
            <h4>试点价值测算</h4>
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
          </div>
        )}

        <div className="review-band">
          <div><h3>复盘摘要</h3><p>{diagnosis.postmortem_summary}</p></div>
          <div>
            <h3>使用边界</h3>
            <ul>{diagnosis.limitations.map((item) => <li key={item}>{item}</li>)}</ul>
          </div>
        </div>
      </div>
    </Section>
  );
}
