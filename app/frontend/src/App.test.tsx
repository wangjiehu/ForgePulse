import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import App from "./App";
import { makeCase, makeDiagnosis } from "./__fixtures__/diagnosis";

function jsonOk(body: unknown): Response {
  return new Response(JSON.stringify(body), { status: 200, headers: { "Content-Type": "application/json" } });
}

describe("App", () => {
  beforeEach(() => {
    // Dev mode (non-prod) without VITE_STATIC_API → calls localhost:8000.
    vi.stubEnv("VITE_STATIC_API", "");
  });
  afterEach(() => {
    vi.unstubAllEnvs();
    vi.restoreAllMocks();
  });

  it("shows a retryable error banner when case loading fails", async () => {
    const fetchMock = vi
      .spyOn(globalThis, "fetch")
      .mockRejectedValueOnce(new Error("network down"))
      .mockResolvedValueOnce(jsonOk([makeCase()]));

    render(<App />);
    expect(await screen.findByText(/案例列表加载失败|network down/)).toBeInTheDocument();

    // Retry triggers the second fetch (success).
    fireEvent.click(screen.getByText("重试"));
    await waitFor(() => {
      expect(fetchMock).toHaveBeenCalledTimes(2);
    });
  });

  it("renders the dashboard after a successful load", async () => {
    const diag = makeDiagnosis();
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.endsWith("/cases")) return jsonOk([makeCase()]);
      if (url.includes("/diagnosis")) return jsonOk(diag);
      return new Response("not found", { status: 404 });
    });

    render(<App />);
    await waitFor(() => {
      expect(screen.getByText(/诊断因果证据网络图/)).toBeInTheDocument();
    });
    expect(screen.getAllByText("干燥二区温控偏差").length).toBeGreaterThan(0);
  });

  it("renders the process map with a critical station driven by evidence", async () => {
    const diag = makeDiagnosis();
    vi.spyOn(globalThis, "fetch").mockImplementation(async (input) => {
      const url = typeof input === "string" ? input : input.toString();
      if (url.endsWith("/cases")) return jsonOk([makeCase()]);
      if (url.includes("/diagnosis")) return jsonOk(diag);
      return new Response("not found", { status: 404 });
    });

    render(<App />);
    await waitFor(() => {
      // EV-1 value DRY-122 → dryer2 critical label "温控偏差"
      expect(screen.getByText("温控偏差")).toBeInTheDocument();
    });
  });
});
