export function EvidenceTags({
  ids,
  onFocus,
}: {
  ids: string[];
  onFocus: (id: string) => void;
}) {
  return (
    <span className="evidence-tags">
      {ids.map((id) => (
        <button key={id} className="evidence-tag" onClick={() => onFocus(id)} title="定位原始证据">
          {id}
        </button>
      ))}
    </span>
  );
}
