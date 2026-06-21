"""ForgePulse API – FastAPI application."""

from __future__ import annotations

import logging
import os

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse

from forgepulse_api.services.case_loader import (
    CaseValidationError,
    get_case_dir,
    load_case_manifest,
    list_available_cases,
    validate_case_directory,
)
from forgepulse_api.services.diagnosis import build_diagnosis
from forgepulse_api.services.model_provider import get_model_provider
from forgepulse_api.services.report_writer import render_markdown_report

APP_VERSION = "0.2.0"
logger = logging.getLogger(__name__)

app = FastAPI(title="ForgePulse API", version=APP_VERSION)

allowed_origins = [
    origin.strip()
    for origin in os.getenv(
        "FORGEPULSE_CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["Accept", "Content-Type"],
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": APP_VERSION}


@app.get("/cases")
def list_cases():
    """List available cases with metadata."""
    cases = []
    for case_id in list_available_cases():
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
        except (CaseValidationError, OSError, ValueError):
            cases.append({"case_id": case_id, "title": "", "title_zh": "", "industry": "", "line": "", "station": ""})
    return cases


@app.get("/cases/{case_id}/diagnosis")
def diagnose_case(case_id: str):
    """Return structured diagnosis for the given case."""
    try:
        return build_diagnosis(case_id).model_dump()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CaseValidationError as e:
        raise HTTPException(status_code=422, detail={"code": "invalid_case", "issues": e.issues})
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"code": "diagnosis_error", "issues": [str(e)]})
    except Exception:
        logger.exception("Unexpected diagnosis failure for case %s", case_id)
        raise HTTPException(status_code=500, detail="Internal diagnosis error")


@app.get("/cases/{case_id}/report", response_class=PlainTextResponse)
def export_report(case_id: str):
    """Export diagnosis as Markdown report."""
    try:
        diagnosis = build_diagnosis(case_id)
        report = render_markdown_report(diagnosis)
        return PlainTextResponse(content=report, media_type="text/markdown")
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CaseValidationError as e:
        raise HTTPException(status_code=422, detail={"code": "invalid_case", "issues": e.issues})
    except ValueError as e:
        raise HTTPException(status_code=422, detail={"code": "diagnosis_error", "issues": [str(e)]})
    except Exception:
        logger.exception("Unexpected report failure for case %s", case_id)
        raise HTTPException(status_code=500, detail="Internal report error")


@app.get("/fault-modes")
def list_fault_modes():
    """List available fault mode definitions."""
    import json
    from pathlib import Path
    fault_modes_path = Path(__file__).resolve().parents[3] / "data" / "fault_modes.json"
    if fault_modes_path.exists():
        with open(fault_modes_path, encoding="utf-8") as f:
            return json.load(f)
    return {"fault_modes": []}


@app.get("/cases/{case_id}/validation")
def validate_case(case_id: str):
    """Return validation errors and warnings for a registered case."""
    try:
        return validate_case_directory(get_case_dir(case_id))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/cases/{case_id}/narrative")
def enhance_narrative(case_id: str):
    """Optionally improve summary wording without changing diagnosis facts."""
    try:
        diagnosis = build_diagnosis(case_id)
        return get_model_provider().enhance(diagnosis).model_dump()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except CaseValidationError as e:
        raise HTTPException(status_code=422, detail={"code": "invalid_case", "issues": e.issues})
    except Exception:
        logger.exception("Unexpected narrative failure for case %s", case_id)
        raise HTTPException(status_code=500, detail="Internal narrative error")
