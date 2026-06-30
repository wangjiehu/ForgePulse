import type { Diagnosis } from "../types";

export type StationStatus = "normal" | "warning" | "critical";

export interface LineStation {
  id: string;
  name: string;
  status: StationStatus;
  /** Status text shown when the station is not normal. */
  abnormalLabel?: string;
}

interface StationRule {
  id: string;
  name: string;
  /** Sensor fields that indicate an anomaly at this station. */
  fields?: string[];
  /** Alarm codes raised at this station. */
  alarms?: string[];
  /** Severity when any trigger matches. */
  severity: "warning" | "critical" | "critical-unless-conflict";
  abnormalLabel: string;
}

/**
 * Rule table for mapping evidence (sensor fields + alarm codes) to coating-line
 * station status. Adding a new case/station only requires editing this table,
 * not the component. Derived from the original ForgePulse coating-line model.
 */
const STATION_RULES: StationRule[] = [
  { id: "unwind", name: "放卷 (Unwind)", severity: "warning", abnormalLabel: "正常" },
  {
    id: "coater",
    name: "涂布/QCS",
    fields: ["thickness_um"],
    alarms: ["QCS-318"],
    severity: "warning",
    abnormalLabel: "厚度漂移",
  },
  {
    id: "dryer1",
    name: "干燥一区 (Z1)",
    fields: ["dryer_zone_1_temp_c"],
    alarms: ["DRY-110"],
    severity: "warning",
    abnormalLabel: "温升异常",
  },
  {
    id: "dryer2",
    name: "干燥二区 (Z2)",
    fields: ["dryer_zone_2_temp_c", "fan_frequency_hz"],
    alarms: ["DRY-122", "AIR-305"],
    severity: "critical-unless-conflict",
    abnormalLabel: "温控偏差",
  },
  {
    id: "tension",
    name: "张力驱动 (Tension)",
    fields: ["web_tension_n", "drive_current_a"],
    alarms: ["TEN-204", "DRV-410"],
    severity: "critical",
    abnormalLabel: "阻力偏大",
  },
  { id: "wind", name: "收卷 (Wind)", severity: "warning", abnormalLabel: "正常" },
];

/** Compute per-station status from a diagnosis's evidence (rule-table driven). */
export function computeLineStatus(diagnosis: Diagnosis | null): Record<string, LineStation> {
  const result: Record<string, LineStation> = {};
  if (!diagnosis) {
    for (const rule of STATION_RULES) {
      result[rule.id] = { id: rule.id, name: rule.name, status: "normal" };
    }
    return result;
  }

  const alarmCodes = new Set(
    diagnosis.evidence.map((e) => e.value).filter(Boolean) as string[],
  );
  const anomalyFields = new Set(
    diagnosis.evidence.map((e) => e.field).filter(Boolean) as string[],
  );

  for (const rule of STATION_RULES) {
    const fieldHit = (rule.fields ?? []).some((f) => anomalyFields.has(f));
    const alarmHit = (rule.alarms ?? []).some((a) => alarmCodes.has(a));
    const triggered = fieldHit || alarmHit;
    let status: StationStatus = "normal";
    if (triggered) {
      if (rule.severity === "critical-unless-conflict") {
        status = diagnosis.diagnosis_status === "conflicting_evidence" ? "warning" : "critical";
      } else {
        status = rule.severity;
      }
    }
    result[rule.id] = {
      id: rule.id,
      name: rule.name,
      status,
      abnormalLabel: rule.abnormalLabel,
    };
  }
  return result;
}
