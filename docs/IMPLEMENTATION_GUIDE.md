# Implementation Guide

## Implemented Modules

### Backend

All modules are implemented in `app/backend/forgepulse_api/services/`:

1. **case_loader.py** – Loads case manifest, sensor CSV, alarm CSV, SOP markdown, and maintenance records from `data/samples/<case_id>/`. Exposes `list_available_cases()` to discover cases dynamically.

2. **sensor_analyzer.py** – Performs threshold violation detection and sustained drift detection on sensor data. Uses configurable threshold bands (`THRESHOLDS` dict). Produces correlated findings across fields (e.g., temperature ↔ thickness).

3. **alarm_parser.py** – Parses alarm CSV into structured events with alarm_code, severity, message, status, and timestamp. Sorts by timestamp.

4. **retriever.py** – Keyword-based retrieval from SOP and maintenance records. Splits documents by section headers and matches keywords from alarm codes and anomaly fields. Returns section content with matched keywords.

5. **diagnosis.py** – Core diagnosis engine that composes a full `Diagnosis` from data analysis results instead of hard-coded values. Builds evidence, timeline, root causes, recommended actions, and work order from real data.

6. **report_writer.py** – Renders a `Diagnosis` as a Markdown report.

### API Endpoints

| Endpoint | Description |
|---|---|
| `GET /health` | Health check |
| `GET /cases` | List available cases with metadata |
| `GET /cases/{case_id}/diagnosis` | Full structured diagnosis |

### Frontend

The React + Vite frontend (`app/frontend/`) implements an engineer workbench with:

- **Sidebar**: Case selection and status overview
- **Incident Summary**: High-level description
- **Event Timeline**: Chronological events with severity badges and evidence links
- **Root Cause Ranking**: Cards with confidence, priority, rationale, and evidence tags
- **Evidence Chain**: Collapsible evidence details from sensors, alarms, SOP, and maintenance records
- **Recommended Actions**: Actionable steps with type badges and linked root causes
- **Work Order Draft**: Pre-filled maintenance work order with tasks and safety notes
- **Postmortem Summary & Limitations**: Post-incident analysis and disclaimers

The frontend fetches data from the backend API (`http://localhost:8000`) and renders it dynamically. No static hard-coded content.

## Running the System

### Backend

```bash
cd app/backend
pip install -e ".[dev]"
uvicorn forgepulse_api.main:app --reload --port 8000
```

### Frontend

```bash
cd app/frontend
npm install
npm run dev
# Open http://localhost:5173
```

### Tests

```bash
cd app/backend
pytest -v
```

## Differences from Original Plan

1. **No alarm_parser.py as a separate file in the plan** – Added as a distinct module per the AGENT_WORKFLOW "Normalize" and "Correlate" steps.
2. **Retriever uses keyword matching instead of vector search** – Appropriate for offline deterministic demo. Can be upgraded to embedding-based retrieval later.
3. **Root cause confidence scores are rule-derived** – Not from LLM reasoning. Scores reflect the number and strength of supporting evidence items.
4. **Frontend uses a single-page workbench layout** – Not a multi-page app. All diagnosis panels are visible on one screen, consistent with the "engineer workbench" requirement.
