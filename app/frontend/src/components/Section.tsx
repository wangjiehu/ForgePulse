import { ChevronDown, ChevronRight } from "lucide-react";
import type { ReactNode } from "react";
import type { Evidence } from "../types";
import { percentage } from "../lib/api";

export function Section({
  icon,
  title,
  children,
  className = "",
}: {
  icon: ReactNode;
  title: string;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section className={`section-block ${className}`.trim()}>
      <header className="section-header">
        {icon}
        <h3>{title}</h3>
      </header>
      <div className="section-body">{children}</div>
    </section>
  );
}

export function ScoreBar({ label, value }: { label: string; value: number }) {
  return (
    <div className="score-row">
      <span>{label}</span>
      <div className="score-track">
        <div className="score-fill" style={{ width: percentage(value) }} />
      </div>
      <strong>{percentage(value)}</strong>
    </div>
  );
}

export function EvidenceItem({
  evidence,
  open,
  focused,
  onToggle,
}: {
  evidence: Evidence;
  open: boolean;
  focused: boolean;
  onToggle: () => void;
}) {
  return (
    <article id={`evidence-${evidence.id}`} className={`evidence-item${focused ? " focused" : ""}`}>
      <button className="evidence-toggle" onClick={onToggle} aria-expanded={open}>
        {open ? <ChevronDown size={16} /> : <ChevronRight size={16} />}
        <code>{evidence.id}</code>
        <span>{evidence.source}</span>
      </button>
      {open && (
        <dl className="evidence-detail">
          {evidence.timestamp && (
            <>
              <dt>时间</dt>
              <dd>{evidence.timestamp}</dd>
            </>
          )}
          {evidence.field && (
            <>
              <dt>字段</dt>
              <dd><code>{evidence.field}</code></dd>
            </>
          )}
          {evidence.value && (
            <>
              <dt>值</dt>
              <dd>{evidence.value}</dd>
            </>
          )}
          <dt>摘要</dt>
          <dd>{evidence.summary}</dd>
        </dl>
      )}
    </article>
  );
}
