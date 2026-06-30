import type { Diagnosis, CaseMeta } from "../types";
import { STATUS_LABEL } from "../lib/labels";

export function DecisionBanner({
  diagnosis,
  meta,
  summary,
}: {
  diagnosis: Diagnosis;
  meta?: CaseMeta;
  summary: string;
}) {
  return (
    <section className={`decision-banner status-${diagnosis.diagnosis_status}`}>
      <div>
        <span>诊断状态</span>
        <strong>{STATUS_LABEL[diagnosis.diagnosis_status]}</strong>
      </div>
      <p>{summary}</p>
    </section>
  );
}
