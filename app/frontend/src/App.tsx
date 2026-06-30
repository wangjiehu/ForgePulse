import { useCallback, useEffect, useMemo, useState } from "react";
import type { CaseMeta, Diagnosis } from "./types";
import { fetchCases, fetchDiagnosis, reportUrl } from "./lib/api";
import { computeLineStatus } from "./lib/lineStatus";
import { Sidebar } from "./components/Sidebar";
import { Topbar } from "./components/Topbar";
import { DecisionBanner } from "./components/DecisionBanner";
import { ProcessMap } from "./components/ProcessMap";
import { EvidenceMap } from "./components/EvidenceMap";
import { Candidates } from "./components/Candidates";
import { Timeline } from "./components/Timeline";
import { EvidenceList } from "./components/EvidenceList";
import { PrimaryFinding } from "./components/PrimaryFinding";
import { DataQuality } from "./components/DataQuality";
import { DecisionLog } from "./components/DecisionLog";
import { ActionsPanel } from "./components/ActionsPanel";
import { ErrorBanner, DashboardSkeleton, EmptyState } from "./components/Feedback";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { FileSearch } from "lucide-react";

const API_KEY = import.meta.env.VITE_API_KEY as string | undefined;

export default function App() {
  const [cases, setCases] = useState<CaseMeta[]>([]);
  const [selectedCase, setSelectedCase] = useState("");
  const [diagnosis, setDiagnosis] = useState<Diagnosis | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [casesError, setCasesError] = useState<string | null>(null);
  const [openEvidence, setOpenEvidence] = useState<Set<string>>(new Set());
  const [focusedEvidence, setFocusedEvidence] = useState<string | null>(null);

  const loadCases = useCallback(async () => {
    setCasesError(null);
    try {
      const data = await fetchCases({ apiKey: API_KEY });
      setCases(data);
      if (data.length > 0) {
        const requestedCase = new URLSearchParams(window.location.search).get("case");
        const initialCase = data.some((item) => item.case_id === requestedCase)
          ? requestedCase!
          : data[0].case_id;
        setSelectedCase((current) => current || initialCase);
      }
    } catch (reason) {
      setCasesError(reason instanceof Error ? reason.message : "案例列表加载失败");
    }
  }, []);

  useEffect(() => {
    void loadCases();
  }, [loadCases]);

  const loadDiagnosis = useCallback(async (caseId: string) => {
    if (!caseId) return;
    setLoading(true);
    setError(null);
    setFocusedEvidence(null);
    setOpenEvidence(new Set());
    try {
      setDiagnosis(await fetchDiagnosis(caseId, { apiKey: API_KEY, reasoning: "auto" }));
    } catch (reason) {
      setDiagnosis(null);
      setError(reason instanceof Error ? reason.message : "未知错误");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void loadDiagnosis(selectedCase);
  }, [selectedCase, loadDiagnosis]);

  const selectedMeta = useMemo(
    () => cases.find((item) => item.case_id === selectedCase),
    [cases, selectedCase],
  );

  const localizedSummary = useMemo(() => {
    if (!diagnosis) return "";
    const title = selectedMeta?.title_zh || selectedMeta?.title || diagnosis.case_id;
    if (diagnosis.diagnosis_status === "insufficient_evidence") {
      return `${title}。现有证据不足以确认根因，需先补采关键数据。`;
    }
    if (diagnosis.diagnosis_status === "conflicting_evidence") {
      return `${title}。报警与传感器证据不一致，维修前必须先核验仪表与时间对齐。`;
    }
    const primary = diagnosis.primary_root_cause?.title_zh ?? diagnosis.primary_root_cause?.title;
    return `${title}。当前主根因：${primary ?? "尚未确定"}。`;
  }, [diagnosis, selectedMeta]);

  const selectCase = useCallback((caseId: string) => {
    setSelectedCase(caseId);
    const url = new URL(window.location.href);
    url.searchParams.set("case", caseId);
    window.history.replaceState({}, "", url);
  }, []);

  const focusEvidence = useCallback((evidenceId: string) => {
    setFocusedEvidence(evidenceId);
    setOpenEvidence((current) => new Set(current).add(evidenceId));
    window.setTimeout(() => {
      document.getElementById(`evidence-${evidenceId}`)?.scrollIntoView({
        behavior: "smooth",
        block: "center",
      });
    }, 20);
  }, []);

  const toggleEvidence = useCallback((id: string) => {
    setOpenEvidence((current) => {
      const next = new Set(current);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  const stations = useMemo(() => computeLineStatus(diagnosis), [diagnosis]);

  return (
    <main className="workspace">
      <Sidebar
        cases={cases}
        selectedCase={selectedCase}
        onSelectCase={selectCase}
        diagnosis={diagnosis}
      />

      <section className="content">
        <Topbar
          meta={selectedMeta}
          loading={loading}
          canRefresh={!!selectedCase}
          onRefresh={() => void loadDiagnosis(selectedCase)}
          onExport={() => window.open(reportUrl(selectedCase, { apiKey: API_KEY }), "_blank")}
        />

        {casesError && (
          <ErrorBanner message={casesError} onRetry={() => void loadCases()} />
        )}

        {error && (
          <ErrorBanner message={error} onRetry={() => void loadDiagnosis(selectedCase)} />
        )}

        {loading && !diagnosis && <DashboardSkeleton />}

        {!loading && !diagnosis && !error && !casesError && (
          <EmptyState
            icon={<FileSearch size={28} />}
            title="请选择诊断案例"
            hint="在左侧选择一个案例以开始证据诊断"
          />
        )}

        {diagnosis && (
          <ErrorBoundary>
            <div className="dashboard-body">
              <div className="dashboard-row-top">
                <DecisionBanner
                  diagnosis={diagnosis}
                  meta={selectedMeta}
                  summary={localizedSummary}
                />
                <ProcessMap stations={stations} />
              </div>

              <div className="dashboard-grid-columns">
                <div className="dashboard-column">
                  <EvidenceMap diagnosis={diagnosis} onFocus={focusEvidence} />
                  <Candidates diagnosis={diagnosis} onFocus={focusEvidence} />
                  <Timeline diagnosis={diagnosis} onFocus={focusEvidence} />
                  <EvidenceList
                    diagnosis={diagnosis}
                    openSet={openEvidence}
                    focused={focusedEvidence}
                    onToggle={toggleEvidence}
                  />
                </div>

                <div className="dashboard-column">
                  <PrimaryFinding diagnosis={diagnosis} />
                  <DataQuality diagnosis={diagnosis} />
                  <DecisionLog diagnosis={diagnosis} />
                  <ActionsPanel diagnosis={diagnosis} />
                </div>
              </div>
            </div>
          </ErrorBoundary>
        )}
      </section>
    </main>
  );
}
