import os
import sys
import json
import shutil
from pathlib import Path

# Add backend directory to path
backend_dir = Path(__file__).resolve().parents[1] / "app" / "backend"
sys.path.insert(0, str(backend_dir))

from forgepulse_api.services.case_loader import (
    list_available_cases,
    load_case_manifest,
)
from forgepulse_api.services.diagnosis import build_diagnosis
from forgepulse_api.services.report_writer import render_markdown_report

def main():
    root_dir = Path(__file__).resolve().parents[1]
    output_dir = root_dir / "app" / "frontend" / "public" / "api"
    
    # Clean output dir
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Export /health.json
    health_data = {"status": "ok", "version": "0.3.0", "provider_mode": "offline", "open_mode": True}
    with open(output_dir / "health.json", "w", encoding="utf-8") as f:
        json.dump(health_data, f)
        
    # 2. Export /fault-modes.json
    fault_modes_path = root_dir / "data" / "fault_modes.json"
    if fault_modes_path.exists():
        shutil.copy(fault_modes_path, output_dir / "fault-modes.json")
    else:
        with open(output_dir / "fault-modes.json", "w", encoding="utf-8") as f:
            json.dump({"fault_modes": []}, f)
            
    # 3. Export /cases.json
    cases = []
    case_ids = list_available_cases()
    for case_id in case_ids:
        try:
            m = load_case_manifest(case_id)
            cases.append({
                "case_id": case_id,
                "title": m.get("title", ""),
                "title_zh": m.get("title_zh", ""),
                "industry": m.get("industry", ""),
                "line": m.get("line", ""),
                "station": m.get("station", ""),
            })
        except Exception as e:
            print(f"Error loading manifest for {case_id}: {e}")
            cases.append({
                "case_id": case_id,
                "title": "",
                "title_zh": "",
                "industry": "",
                "line": "",
                "station": "",
            })
            
    with open(output_dir / "cases.json", "w", encoding="utf-8") as f:
        json.dump(cases, f, ensure_ascii=False, indent=2)
        
    # 4. Export /cases/{case_id}/diagnosis.json and /cases/{case_id}/report.md
    for case_id in case_ids:
        case_api_dir = output_dir / "cases" / case_id
        case_api_dir.mkdir(parents=True, exist_ok=True)
        
        # Diagnosis
        try:
            diagnosis = build_diagnosis(case_id)
            with open(case_api_dir / "diagnosis.json", "w", encoding="utf-8") as f:
                json.dump(diagnosis.model_dump(), f, ensure_ascii=False, indent=2)
            
            # Report
            report = render_markdown_report(diagnosis)
            with open(case_api_dir / "report.md", "w", encoding="utf-8") as f:
                f.write(report)
                
            print(f"Exported static API files for case: {case_id}")
        except Exception as e:
            print(f"Error diagnosing {case_id}: {e}")

if __name__ == "__main__":
    main()
