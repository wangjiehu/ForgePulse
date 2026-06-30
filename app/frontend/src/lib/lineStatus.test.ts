import { describe, it, expect } from "vitest";
import { computeLineStatus } from "./lineStatus";
import type { Diagnosis } from "../types";

function diagWith(evidence: { id: string; source: string; field?: string; value?: string }[], status: Diagnosis["diagnosis_status"] = "confirmed"): Diagnosis {
  return {
    case_id: "t",
    diagnosis_status: status,
    incident_summary: "",
    timeline: [],
    evidence: evidence as Diagnosis["evidence"],
    root_cause_candidates: [],
    contributing_factors: [],
    downstream_effects: [],
    business_risks: [],
    missing_evidence: [],
    conflicting_evidence: [],
    recommended_actions: [],
    work_order_draft: { title: "", priority: "", assignee_role: "", tasks: [], safety_notes: [] },
    postmortem_summary: "",
    limitations: [],
    diagnostic_process: [],
    agent_decisions: [],
    evidence_links: [],
    value_estimates: [],
  };
}

describe("computeLineStatus", () => {
  it("returns all-normal when diagnosis is null", () => {
    const stations = computeLineStatus(null);
    expect(stations.dryer2.status).toBe("normal");
    expect(stations.tension.status).toBe("normal");
    expect(Object.keys(stations)).toHaveLength(6);
  });

  it("marks coater warning on thickness field", () => {
    const stations = computeLineStatus(diagWith([{ id: "EV1", source: "sensor", field: "thickness_um" }]));
    expect(stations.coater.status).toBe("warning");
    expect(stations.dryer2.status).toBe("normal");
  });

  it("marks tension critical on drive current field", () => {
    const stations = computeLineStatus(diagWith([{ id: "EV1", source: "sensor", field: "drive_current_a" }]));
    expect(stations.tension.status).toBe("critical");
  });

  it("marks dryer2 critical on alarm DRY-122", () => {
    const stations = computeLineStatus(diagWith([{ id: "EV1", source: "alarm", value: "DRY-122" }]));
    expect(stations.dryer2.status).toBe("critical");
  });

  it("downgrades dryer2 to warning when evidence is conflicting", () => {
    const stations = computeLineStatus(
      diagWith([{ id: "EV1", source: "alarm", value: "DRY-122" }], "conflicting_evidence"),
    );
    expect(stations.dryer2.status).toBe("warning");
  });

  it("is rule-driven: alarm TEN-204 hits tension, not coater", () => {
    const stations = computeLineStatus(diagWith([{ id: "EV1", source: "alarm", value: "TEN-204" }]));
    expect(stations.tension.status).toBe("critical");
    expect(stations.coater.status).toBe("normal");
  });
});
