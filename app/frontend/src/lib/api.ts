import type { CaseMeta, Diagnosis } from "../types";

const isProd = import.meta.env.PROD;
const LIVE = import.meta.env.VITE_LIVE_API === "true";

/**
 * API base URL.
 * - Live same-origin mode (VITE_LIVE_API=true, e.g. HuggingFace Space): empty,
 *   requests go to the same origin that serves the frontend (FastAPI serves both).
 * - Explicit override via VITE_API_BASE_URL (dev with a remote backend).
 * - Default prod (GitHub Pages static): same-origin /api (pre-generated JSON).
 * - Default dev: http://localhost:8000.
 */
const API_BASE = LIVE
  ? ""
  : (import.meta.env.VITE_API_BASE_URL ?? (isProd
      ? `${window.location.origin}${window.location.pathname.replace(/\/$/, "")}/api`
      : "http://localhost:8000")).replace(/\/$/, "");

export const USE_STATIC_API = !LIVE && (isProd || import.meta.env.VITE_STATIC_API === "true");

export interface ApiConfig {
  apiKey?: string;
  reasoning?: "auto" | "off" | "llm";
}

function headers(config?: ApiConfig): Record<string, string> {
  const h: Record<string, string> = { Accept: "application/json" };
  if (config?.apiKey) h["X-API-Key"] = config.apiKey;
  return h;
}

export async function fetchCases(config?: ApiConfig): Promise<CaseMeta[]> {
  const url = USE_STATIC_API ? `${API_BASE}/cases.json` : `${API_BASE}/cases`;
  const response = await fetch(url, { headers: headers(config) });
  if (!response.ok) throw new Error(`案例列表加载失败 (${response.status})`);
  return response.json();
}

export async function fetchDiagnosis(
  caseId: string,
  config?: ApiConfig,
): Promise<Diagnosis> {
  const reasoning = config?.reasoning ?? "auto";
  const url = USE_STATIC_API
    ? `${API_BASE}/cases/${caseId}/diagnosis.json`
    : `${API_BASE}/cases/${caseId}/diagnosis?reasoning=${reasoning}`;
  const response = await fetch(url, { headers: headers(config) });
  if (!response.ok) {
    const payload = await response.json().catch(() => null);
    const detail =
      payload?.detail?.issues?.join("; ") ?? payload?.detail ?? response.status;
    throw new Error(`诊断失败：${detail}`);
  }
  return response.json();
}

export function reportUrl(caseId: string, config?: ApiConfig): string {
  const base = USE_STATIC_API
    ? `${API_BASE}/cases/${caseId}/report.md`
    : `${API_BASE}/cases/${caseId}/report`;
  if (config?.apiKey && !USE_STATIC_API) {
    return `${base}?key=${encodeURIComponent(config.apiKey)}`;
  }
  return base;
}

export function formatTime(value: string) {
  const date = new Date(value);
  return Number.isNaN(date.getTime())
    ? value
    : date.toLocaleTimeString("zh-CN", {
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
      });
}

export function percentage(value: number) {
  return `${Math.round(value * 100)}%`;
}
