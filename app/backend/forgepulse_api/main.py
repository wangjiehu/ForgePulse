"""ForgePulse API – FastAPI application."""

from __future__ import annotations

import logging
import os
import uuid
from typing import Literal

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.base import BaseHTTPMiddleware

from forgepulse_api.security import (
    Principal,
    audit_dispatch,
    is_open_mode,
    verify_api_key,
)
from forgepulse_api.services.case_loader import (
    CaseValidationError,
    list_available_cases,
    load_case_manifest,
    validate_case_directory,
    get_case_dir,
)
from forgepulse_api.services.diagnosis import build_diagnosis
from forgepulse_api.services.model_provider import get_model_provider
from forgepulse_api.services.report_writer import render_markdown_report

APP_VERSION = "0.3.0"
logger = logging.getLogger(__name__)

logging.basicConfig(
    level=os.getenv("FORGEPULSE_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)

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
    allow_headers=["Accept", "Content-Type", "X-API-Key", "Authorization"],
)


async def request_id_dispatch(request: Request, call_next):
    """Attach a request id to every request for tracing and audit correlation."""
    request_id = request.headers.get("X-Request-ID") or uuid.uuid4().hex[:12]
    request.state.request_id = request_id
    response = await call_next(request)
    response.headers["X-Request-ID"] = request_id
    return response


app.add_middleware(BaseHTTPMiddleware, dispatch=request_id_dispatch)
app.add_middleware(BaseHTTPMiddleware, dispatch=audit_dispatch)

if is_open_mode():
    logger.warning(
        "FORGEPULSE_API_KEYS is not set — API is running in OPEN MODE (no auth). "
        "This must not be used in production."
    )

provider = get_model_provider()
if os.getenv("FORGEPULSE_MODEL_PROVIDER", "offline").strip().lower() == "openai_compatible" and provider.name == "offline":
    logger.warning(
        "FORGEPULSE_MODEL_PROVIDER=openai_compatible but base_url/api_key/model is incomplete; "
        "falling back to offline (no LLM reasoning)."
    )


@app.get("/health")
def health():
    """Return service health, provider mode, case count, and rate-limit config (no secrets)."""
    return {
        "status": "ok",
        "version": APP_VERSION,
        "provider_mode": provider.name,
        "open_mode": is_open_mode(),
        "case_count": len(list_available_cases()),
        "rate_limit_per_minute": os.getenv("FORGEPULSE_RATE_LIMIT", "60"),
    }


@app.get("/cases")
def list_cases(_: Principal = Depends(verify_api_key)):
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
def diagnose_case(
    case_id: str,
    reasoning: Literal["auto", "off", "llm"] = "auto",
    _: Principal = Depends(verify_api_key),
):
    """Return structured diagnosis for the given case.

    ``reasoning``:
    - ``auto``: attach LLM advisory review when a provider is configured (default).
    - ``llm``: same as auto (explicit); offline provider yields no review.
    - ``off``: never call the LLM; pure deterministic output.
    """
    try:
        return build_diagnosis(case_id, reasoning=reasoning).model_dump()
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
def export_report(case_id: str, _: Principal = Depends(verify_api_key)):
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
def list_fault_modes(_: Principal = Depends(verify_api_key)):
    """List available fault mode definitions."""
    import json
    from pathlib import Path
    fault_modes_path = Path(__file__).resolve().parents[3] / "data" / "fault_modes.json"
    if fault_modes_path.exists():
        with open(fault_modes_path, encoding="utf-8") as f:
            return json.load(f)
    return {"fault_modes": []}


@app.get("/cases/{case_id}/validation")
def validate_case(case_id: str, _: Principal = Depends(verify_api_key)):
    """Return validation errors and warnings for a registered case."""
    try:
        return validate_case_directory(get_case_dir(case_id))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/cases/{case_id}/narrative")
def enhance_narrative(case_id: str, _: Principal = Depends(verify_api_key)):
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


# ---------------------------------------------------------------------------
# Static frontend serving (single-process deploy, e.g. HuggingFace Spaces).
# Enabled when FORGEPULSE_STATIC_DIR points to a built Vite `dist` directory.
# Mounted AFTER all API routes so API endpoints take precedence. The built
# frontend uses same-origin live mode (VITE_LIVE_API=true) and calls the API
# routes above directly.
# ---------------------------------------------------------------------------
_static_dir = os.getenv("FORGEPULSE_STATIC_DIR", "").strip()
if _static_dir:
    from pathlib import Path

    _static_path = Path(_static_dir)
    if _static_path.is_dir():
        app.mount("/", StaticFiles(directory=str(_static_path), html=True), name="frontend")
        logger.info("Serving static frontend from %s", _static_path)
    else:
        logger.warning("FORGEPULSE_STATIC_DIR=%s does not exist; not serving frontend", _static_dir)
