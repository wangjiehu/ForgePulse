import { AlertTriangle, FileSearch } from "lucide-react";
import type { Diagnosis } from "../types";
import { translateEvidenceIssue } from "../lib/labels";

export function PrimaryFinding({ diagnosis }: { diagnosis: Diagnosis }) {
  const primary = diagnosis.primary_root_cause;
  const hasAlerts =
    diagnosis.missing_evidence.length > 0 || diagnosis.conflicting_evidence.length > 0;
  return (
    <>
      {primary && (
        <div className="primary-finding-compact">
          <div>
            <span>主根因</span>
            <h4>{primary.title_zh ?? primary.title}</h4>
            <p>{primary.why_ranked}</p>
          </div>
          <strong>{Math.round(primary.confidence * 100)}%</strong>
        </div>
      )}

      {hasAlerts && (
        <section className="evidence-alerts">
          {diagnosis.missing_evidence.length > 0 && (
            <div className="alert-missing">
              <FileSearch size={14} />
              <span>
                <strong>缺失：</strong>
                {diagnosis.missing_evidence.map(translateEvidenceIssue).join("；")}
              </span>
            </div>
          )}
          {diagnosis.conflicting_evidence.length > 0 && (
            <div className="alert-conflicting">
              <AlertTriangle size={14} />
              <span>
                <strong>冲突：</strong>
                {diagnosis.conflicting_evidence.map(translateEvidenceIssue).join("；")}
              </span>
            </div>
          )}
        </section>
      )}
    </>
  );
}
