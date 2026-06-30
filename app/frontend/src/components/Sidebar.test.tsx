import { describe, it, expect, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { Sidebar } from "./Sidebar";
import { makeCase, makeDiagnosis } from "../__fixtures__/diagnosis";

describe("Sidebar", () => {
  it("renders the case list and selects on click", () => {
    const onSelect = vi.fn();
    const cases = [makeCase({ case_id: "C1", title_zh: "案例一" }), makeCase({ case_id: "C2", title_zh: "案例二" })];
    render(
      <Sidebar cases={cases} selectedCase="C1" onSelectCase={onSelect} diagnosis={null} />,
    );
    expect(screen.getByText("案例一")).toBeInTheDocument();
    expect(screen.getByText("案例二")).toBeInTheDocument();
    fireEvent.click(screen.getByText("案例二"));
    expect(onSelect).toHaveBeenCalledWith("C2");
  });

  it("shows an empty state when there are no cases", () => {
    render(<Sidebar cases={[]} selectedCase="" onSelectCase={() => {}} diagnosis={null} />);
    expect(screen.getByText("暂无可用案例")).toBeInTheDocument();
  });

  it("renders current diagnosis metrics when a diagnosis is present", () => {
    render(
      <Sidebar
        cases={[makeCase()]}
        selectedCase="CASE-001"
        onSelectCase={() => {}}
        diagnosis={makeDiagnosis()}
      />,
    );
    expect(screen.getByText("当前诊断")).toBeInTheDocument();
    expect(screen.getByText("证据充分")).toBeInTheDocument();
  });
});
