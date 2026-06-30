import { CircleDot, Factory, Flame, Layers, MoveHorizontal, RotateCw } from "lucide-react";
import type { LineStation } from "../lib/lineStatus";

const ICONS: Record<string, typeof Flame> = {
  unwind: CircleDot,
  coater: Layers,
  dryer1: Flame,
  dryer2: Flame,
  tension: MoveHorizontal,
  wind: RotateCw,
};

const ORDER = ["unwind", "coater", "dryer1", "dryer2", "tension", "wind"];

export function ProcessMap({ stations }: { stations: Record<string, LineStation> }) {
  return (
    <section className="process-map-card section-block">
      <header className="section-header">
        <Factory size={16} />
        <h3>极片涂布产线物理监测图 (Coating Line Process Map)</h3>
      </header>
      <div className="process-map-body">
        <div className="process-flow">
          {ORDER.map((id, index) => {
            const station = stations[id];
            if (!station) return null;
            const Icon = ICONS[id] ?? CircleDot;
            return (
              <span key={id} style={{ display: "contents" }}>
                <div className={`process-node status-${station.status}`}>
                  <Icon size={18} />
                  <span className="node-name">{station.name}</span>
                  <span className="node-status">
                    {station.status === "normal" ? "正常" : station.abnormalLabel}
                  </span>
                </div>
                {index < ORDER.length - 1 && <div className="flow-arrow">→</div>}
              </span>
            );
          })}
        </div>
      </div>
    </section>
  );
}
