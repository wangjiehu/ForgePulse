"""Generate checked-in sample diagnosis reports for public review."""

from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "app" / "backend"
OUTPUT_DIR = PROJECT_ROOT / "reports" / "generated_samples"

CASES = [
    "coating_line_dryer_tension_001",
    "coating_line_airflow_002",
    "coating_line_drive_resistance_003",
    "coating_line_incomplete_evidence_004",
    "coating_line_conflicting_evidence_005",
]


def main() -> int:
    sys.path.insert(0, str(BACKEND_ROOT))

    from forgepulse_api.services.diagnosis import build_diagnosis
    from forgepulse_api.services.report_writer import render_markdown_report

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for case_id in CASES:
        diagnosis = build_diagnosis(case_id)
        report = render_markdown_report(diagnosis)
        output_path = OUTPUT_DIR / f"{case_id}.md"
        output_path.write_text(report, encoding="utf-8")
        print(f"generated {output_path.relative_to(PROJECT_ROOT)}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
