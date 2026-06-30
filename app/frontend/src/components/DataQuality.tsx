import { BarChart3 } from "lucide-react";
import type { Diagnosis } from "../types";

export function DataQuality({ diagnosis }: { diagnosis: Diagnosis }) {
  const dq = diagnosis.data_quality;
  return (
    <section className="data-quality-card section-block">
      <header className="section-header">
        <BarChart3 size={16} />
        <h3>数据监测质量 (Data Quality)</h3>
      </header>
      <div className="section-body">
        <div className="quality-metrics">
          <div><span>传感器行</span><strong>{dq?.sensor_rows ?? 0}</strong></div>
          <div><span>报警事件</span><strong>{dq?.alarm_events ?? 0}</strong></div>
          <div><span>SOP 章节</span><strong>{dq?.sop_sections ?? 0}</strong></div>
          <div><span>维修记录</span><strong>{dq?.maintenance_records ?? 0}</strong></div>
        </div>
      </div>
    </section>
  );
}
