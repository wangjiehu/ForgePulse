import { describe, it, expect } from "vitest";
import { translateEvidenceIssue, STATUS_LABEL, DECISION_LABEL } from "./labels";

describe("labels", () => {
  it("translates known evidence issue prefixes to Chinese", () => {
    expect(translateEvidenceIssue("primary alarm: DRY-122")).toBe("主报警证据： DRY-122");
    expect(translateEvidenceIssue("critical sensor field: fan_frequency_hz")).toBe(
      "关键传感器字段： fan_frequency_hz",
    );
  });

  it("translates the alarm-vs-sensor conflict sentence", () => {
    expect(
      translateEvidenceIssue("alarms favor dryer, while sensor anomalies favor tension"),
    ).toBe("报警证据支持 dryer，但传感器异常支持 tension");
  });

  it("maps every diagnosis status to a Chinese label", () => {
    expect(STATUS_LABEL.confirmed).toBe("证据充分");
    expect(STATUS_LABEL.conflicting_evidence).toBe("证据冲突");
  });

  it("maps decision codes", () => {
    expect(DECISION_LABEL.continue_with_caution).toBe("谨慎继续");
    expect(DECISION_LABEL.conflicting_evidence).toContain("核验冲突");
  });
});
