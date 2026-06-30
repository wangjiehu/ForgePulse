import { FileText } from "lucide-react";
import type { Diagnosis } from "../types";
import { Section, EvidenceItem } from "./Section";

export function EvidenceList({
  diagnosis,
  openSet,
  focused,
  onToggle,
}: {
  diagnosis: Diagnosis;
  openSet: Set<string>;
  focused: string | null;
  onToggle: (id: string) => void;
}) {
  return (
    <Section icon={<FileText size={16} />} title="原始证据">
      <div className="evidence-list">
        {diagnosis.evidence.map((item) => (
          <EvidenceItem
            key={item.id}
            evidence={item}
            open={openSet.has(item.id)}
            focused={focused === item.id}
            onToggle={() => onToggle(item.id)}
          />
        ))}
      </div>
    </Section>
  );
}
