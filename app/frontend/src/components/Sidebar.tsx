import { Factory, Inbox } from "lucide-react";
import type { CaseMeta, Diagnosis } from "../types";
import { percentage } from "../lib/api";
import { STATUS_LABEL } from "../lib/labels";
import { EmptyState } from "./Feedback";

export function Sidebar({
  cases,
  selectedCase,
  onSelectCase,
  diagnosis,
}: {
  cases: CaseMeta[];
  selectedCase: string;
  onSelectCase: (id: string) => void;
  diagnosis: Diagnosis | null;
}) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <Factory size={26} />
        <div>
          <h1>ForgePulse</h1>
          <p>涂布产线证据诊断工作台</p>
        </div>
      </div>

      <nav aria-label="诊断案例">
        <h2>诊断案例</h2>
        {cases.length === 0 ? (
          <EmptyState icon={<Inbox size={20} />} title="暂无可用案例" hint="请确认数据已就绪" />
        ) : (
          <div className="case-list">
            {cases.map((item) => (
              <button
                key={item.case_id}
                className={`case-button${selectedCase === item.case_id ? " active" : ""}`}
                onClick={() => onSelectCase(item.case_id)}
              >
                <span>{item.title_zh || item.title}</span>
                <code>{item.case_id}</code>
              </button>
            ))}
          </div>
        )}
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
  );
}
