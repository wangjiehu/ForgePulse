import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { DecisionLog } from "./DecisionLog";
import { makeDiagnosis, makeReasoning } from "../__fixtures__/diagnosis";

describe("DecisionLog", () => {
  it("renders the agent decision trace", () => {
    render(<DecisionLog diagnosis={makeDiagnosis()} />);
    expect(screen.getByText("Agent 决策轨迹")).toBeInTheDocument();
    expect(screen.getByText("agent_decision_trace.log")).toBeInTheDocument();
    expect(screen.getByText("证据充分")).toBeInTheDocument();
  });

  it("does not render the AI review block when agent_reasoning is absent", () => {
    render(<DecisionLog diagnosis={makeDiagnosis({ agent_reasoning: null })} />);
    expect(screen.queryByText("AI 复核")).not.toBeInTheDocument();
  });

  it("renders the AI review block when agent_reasoning is present", () => {
    render(<DecisionLog diagnosis={makeDiagnosis({ agent_reasoning: makeReasoning() })} />);
    expect(screen.getByText("AI 复核")).toBeInTheDocument();
    expect(screen.getByText("LLM 推理")).toBeInTheDocument();
    expect(screen.getByText("Evidence supports the primary candidate.")).toBeInTheDocument();
    expect(screen.getByText("Confirm with engineer before repair.")).toBeInTheDocument();
    expect(screen.getByText("Confirm fan inspection record.")).toBeInTheDocument();
  });

  it("shows offline badge when reasoning mode is offline", () => {
    render(
      <DecisionLog
        diagnosis={makeDiagnosis({ agent_reasoning: makeReasoning({ mode: "offline", review_summary: "" }) })}
      />,
    );
    expect(screen.getByText("离线")).toBeInTheDocument();
  });

  it("shows a warning when the review carries one", () => {
    render(
      <DecisionLog
        diagnosis={makeDiagnosis({ agent_reasoning: makeReasoning({ warning: "LLM review failed" }) })}
      />,
    );
    expect(screen.getByText("LLM review failed")).toBeInTheDocument();
  });
});
