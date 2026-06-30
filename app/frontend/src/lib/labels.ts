import type { DiagnosisStatus, DiagnosticRole } from "../types";

export const STATUS_LABEL: Record<DiagnosisStatus, string> = {
  confirmed: "证据充分",
  provisional: "暂定诊断",
  insufficient_evidence: "证据不足",
  conflicting_evidence: "证据冲突",
};

export const ROLE_LABEL: Record<DiagnosticRole, string> = {
  equipment_cause: "设备根因",
  coupled_secondary_factor: "伴随因素",
  quality_effect: "下游影响",
};

export const ACTION_LABEL: Record<string, string> = {
  collect_data: "补采数据",
  inspect: "现场检查",
  verify: "核验",
  quality: "质量处置",
  escalate: "升级通知",
  safety: "安全确认",
};

export const OWNER_LABEL: Record<string, string> = {
  equipment_engineer: "设备工程师",
  quality_engineer: "质量工程师",
  production_supervisor: "生产主管",
  safety_reviewer: "安全复核",
};

export const DECISION_LABEL: Record<string, string> = {
  continue: "继续",
  continue_with_caution: "谨慎继续",
  confirmed: "证据充分",
  provisional: "暂定诊断",
  insufficient_evidence: "停止确认，补充证据",
  conflicting_evidence: "停止处置，先核验冲突",
};

export function translateEvidenceIssue(value: string) {
  return value
    .replace("critical sensor field:", "关键传感器字段：")
    .replace("primary sensor anomaly:", "主传感器异常证据：")
    .replace("primary alarm:", "主报警证据：")
    .replace(
      /^alarms favor (.+), while sensor anomalies favor (.+)$/,
      "报警证据支持 $1，但传感器异常支持 $2",
    );
}
