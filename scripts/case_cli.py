"""Validate, import, or diagnose ForgePulse case directories."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
BACKEND_ROOT = PROJECT_ROOT / "app" / "backend"
sys.path.insert(0, str(BACKEND_ROOT))

from forgepulse_api.services.case_loader import import_case_directory, validate_case_directory
from forgepulse_api.services.diagnosis import build_diagnosis
from forgepulse_api.services.report_writer import render_markdown_report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_parser = subparsers.add_parser("validate", help="Validate a case directory")
    validate_parser.add_argument("path", type=Path)

    import_parser = subparsers.add_parser("import", help="Validate and import a case directory")
    import_parser.add_argument("path", type=Path)
    import_parser.add_argument("--replace", action="store_true")

    diagnose_parser = subparsers.add_parser("diagnose", help="Diagnose an imported case")
    diagnose_parser.add_argument("case_id")
    diagnose_parser.add_argument("--report", type=Path)

    args = parser.parse_args()

    if args.command == "validate":
        result = validate_case_directory(args.path)
        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        return 0 if result["valid"] else 1

    if args.command == "import":
        case_id = import_case_directory(args.path, replace=args.replace)
        print(f"Imported case: {case_id}")
        return 0

    diagnosis = build_diagnosis(args.case_id)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(render_markdown_report(diagnosis), encoding="utf-8")
        print(f"Report written: {args.report}")
    else:
        print(diagnosis.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
