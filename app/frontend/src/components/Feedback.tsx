import { Activity, AlertTriangle, RefreshCw } from "lucide-react";
import type { ReactNode } from "react";

export function ErrorBanner({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <div className="error-banner" role="alert">
      <AlertTriangle size={18} />
      <span style={{ flex: 1 }}>{message}</span>
      {onRetry && (
        <button className="retry-button" onClick={onRetry}>
          <RefreshCw size={14} /> 重试
        </button>
      )}
    </div>
  );
}

export function Loading({ label }: { label?: string }) {
  return (
    <div className="loading">
      <Activity className="spin" />
      <span>{label ?? "正在核验数据、报警和维修证据"}</span>
    </div>
  );
}

/** Structured skeleton matching the dashboard layout to reduce layout shift. */
export function DashboardSkeleton() {
  return (
    <div className="dashboard-body" aria-hidden="true">
      <div className="dashboard-row-top">
        <div className="skeleton skeleton-banner" />
        <div className="skeleton skeleton-card" />
      </div>
      <div className="dashboard-grid-columns">
        <div className="dashboard-column">
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card tall" />
        </div>
        <div className="dashboard-column">
          <div className="skeleton skeleton-card" />
          <div className="skeleton skeleton-card tall" />
        </div>
      </div>
    </div>
  );
}

export function EmptyState({ icon, title, hint }: { icon?: ReactNode; title: string; hint?: string }) {
  return (
    <div className="empty-state">
      {icon}
      <strong>{title}</strong>
      {hint && <span>{hint}</span>}
    </div>
  );
}
