import { Activity } from "lucide-react";
import type { Diagnosis } from "../types";
import { formatTime } from "../lib/api";
import { Section } from "./Section";
import { EvidenceTags } from "./EvidenceTags";

export function Timeline({
  diagnosis,
  onFocus,
}: {
  diagnosis: Diagnosis;
  onFocus: (id: string) => void;
}) {
  return (
    <Section icon={<Activity size={16} />} title="事件时间线">
      <div className="timeline">
        {diagnosis.timeline.map((item, index) => (
          <div className="timeline-row" key={`${item.timestamp}-${index}`}>
            <time>{formatTime(item.timestamp)}</time>
            <span className={`severity severity-${item.severity}`}>{item.severity}</span>
            <div>
              <strong>{item.title}</strong>
              <p>{item.detail}</p>
              <EvidenceTags ids={item.evidence_ids} onFocus={onFocus} />
            </div>
          </div>
        ))}
      </div>
    </Section>
  );
}
