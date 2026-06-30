import { Download, RefreshCw } from "lucide-react";
import type { CaseMeta } from "../types";

export function Topbar({
  meta,
  loading,
  canRefresh,
  onRefresh,
  onExport,
}: {
  meta?: CaseMeta;
  loading: boolean;
  canRefresh: boolean;
  onRefresh: () => void;
  onExport: () => void;
}) {
  return (
    <header className="topbar">
      <div>
        <span className="eyebrow">{meta?.line ?? "未选择产线"} / {meta?.station ?? ""}</span>
        <h2>{meta?.title_zh || meta?.title || "请选择诊断案例"}</h2>
      </div>
      <div className="toolbar">
        <button className="icon-command" onClick={onRefresh} disabled={loading || !canRefresh} title="重新诊断">
          <RefreshCw size={16} className={loading ? "spin" : ""} />
          <span>{loading ? "分析中" : "重新诊断"}</span>
        </button>
        <button className="icon-command" onClick={onExport} disabled={!canRefresh} title="导出 Markdown 报告">
          <Download size={16} />
          <span>导出报告</span>
        </button>
      </div>
    </header>
  );
}
