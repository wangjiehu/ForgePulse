import { FileSearch, FileText } from "lucide-react";
import type { Diagnosis } from "../types";

export function EvidenceMap({
  diagnosis,
  onFocus,
}: {
  diagnosis: Diagnosis;
  onFocus: (id: string) => void;
}) {
  const sources = Array.from(new Set(diagnosis.evidence.map((e) => e.source))).slice(0, 3);
  return (
    <section className="evidence-map-card section-block">
      <header className="section-header">
        <FileSearch size={16} />
        <h3>诊断因果证据网络图 (Causal Evidence Map)</h3>
      </header>
      <div className="evidence-map-body">
        <div className="evidence-map-workspace">
          <div className="map-column">
            <span className="column-title">根因 (Candidates)</span>
            <div className="map-nodes">
              {diagnosis.root_cause_candidates.slice(0, 2).map((rc) => (
                <div key={rc.candidate_id} className={`map-node candidate-node priority-${rc.priority}`}>
                  <div className="node-header">
                    <code>{rc.candidate_id}</code>
                    <strong>{rc.title_zh || rc.title}</strong>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="map-connector-column"><div className="connector-path" /></div>

          <div className="map-column">
            <span className="column-title">关联证据 (Evidence)</span>
            <div className="map-nodes">
              {diagnosis.evidence.slice(0, 4).map((ev) => {
                const isAlarm = ev.source.includes("alarm");
                const isSensor = ev.source.includes("sensor");
                const typeClass = isAlarm ? "alarm" : isSensor ? "sensor" : "record";
                return (
                  <button
                    key={ev.id}
                    className={`map-node evidence-node type-${typeClass}`}
                    onClick={() => onFocus(ev.id)}
                    title="点击定位到下方原始数据"
                  >
                    <code>{ev.id}</code>
                    <span>{ev.summary}</span>
                  </button>
                );
              })}
              {diagnosis.evidence.length > 4 && (
                <div className="map-nodes-more">+ 还有 {diagnosis.evidence.length - 4} 项关联</div>
              )}
            </div>
          </div>

          <div className="map-connector-column"><div className="connector-path" /></div>

          <div className="map-column">
            <span className="column-title">数据源 (Sources)</span>
            <div className="map-nodes">
              {sources.map((source) => (
                <div key={source} className="map-node source-node">
                  <FileText size={12} />
                  <span>{source}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
