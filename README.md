---
title: ForgePulse
emoji: 🏭
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---

# ForgePulse

> 面向新能源电池产线的设备故障诊断 Agent —— 把传感器时序、报警日志、SOP、维修记录整合成可追溯的诊断、处置建议与复盘报告。

An industry agent for battery manufacturing equipment diagnosis. Every root cause, action, and work-order suggestion links back to the alarm, sensor anomaly, SOP section, or maintenance record it came from — so an engineer can audit it rather than trust it.

**Live demo** — [jiehu-claire-forgepulse.hf.space](https://jiehu-claire-forgepulse.hf.space/) (full stack, real LLM advisory layer) · [Static demo](https://wangjiehu.github.io/ForgePulse/) (offline build)

## What it does

ForgePulse turns scattered shop-floor signals into a read-only diagnosis workflow. It reads evidence, ranks likely root causes with confidence scores, recommends actions and work orders, and produces a reviewable report. It is engineer-facing and **never writes back to equipment**.

## Architecture — two layers

- **Deterministic engine (source of truth).** Produces the structured diagnosis: status, root-cause candidates, confidence, scores, recommended actions. Evidence-validated and deterministic — identical output across runs.
- **LLM advisory layer.** Reviews the deterministic output and adds natural-language rationale, uncertainty flags, and a safety reaffirmation. Validated against an evidence-ID whitelist, **never overrides structured fields**, and falls back gracefully when no model is configured.

Diagnosis stays auditable and reproducible; the LLM only adds a reviewable reasoning trace.

## Features

- 5 golden industrial cases, including insufficient and conflicting evidence
- Evidence-linked root-cause ranking with confidence and scoring
- AI review block (renders as `offline` when no LLM is wired up)
- API-key auth, RBAC (viewer / engineer / admin), rate limiting, JSONL audit log
- Single-container deploy — one FastAPI process serves the API and the built frontend

## Tech stack

| Layer | Stack |
|---|---|
| Backend | Python · FastAPI · Pydantic v2 · OpenAI-compatible LLM |
| Frontend | React 19 · TypeScript · Vite |
| Evaluation | golden cases · counterfactual sensitivity · determinism checks |

## Quick start

### Local development

```bash
# Backend (API on :8000)
cd app/backend
python -m uvicorn forgepulse_api.main:app --reload --port 8000

# Frontend (dev server on :5173)
cd app/frontend
npm install
npm run dev
```

The frontend dev server expects the API at `http://127.0.0.1:8000` (set via `app/frontend/.env`, see `.env.example`). With no LLM configured it runs in offline mode — fully functional, no API key required.

### Docker

```bash
docker build -t forgepulse .
docker run --rm -p 7860:7860 \
  -e FORGEPULSE_MODEL_PROVIDER=openai_compatible \
  -e FORGEPULSE_MODEL_BASE_URL=https://your-endpoint/v1 \
  -e FORGEPULSE_MODEL_API_KEY=your-key \
  -e FORGEPULSE_MODEL_NAME=your-model \
  -e FORGEPULSE_API_KEYS=demo-key:viewer \
  forgepulse
# open http://localhost:7860
```

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `FORGEPULSE_MODEL_PROVIDER` | `offline` | `offline` or `openai_compatible` |
| `FORGEPULSE_MODEL_BASE_URL` | — | OpenAI-compatible endpoint |
| `FORGEPULSE_MODEL_API_KEY` | — | LLM credential |
| `FORGEPULSE_MODEL_NAME` | — | Model to call |
| `FORGEPULSE_API_KEYS` | — | `key:role` entries; unset = open mode (dev only) |
| `FORGEPULSE_RATE_LIMIT` | `60` | Per-key requests / minute |
| `FORGEPULSE_AUDIT_LOG` | `logs/audit.jsonl` | Structured audit log path |

See `.env.example` for the full list. **Open mode (no `FORGEPULSE_API_KEYS`) must not be used in production.**

## Verification

- `92` backend tests · `21` frontend tests
- `76 / 76` evaluation checks pass (behavioral, integrity, counterfactual, determinism)

```bash
cd app/backend && python -m pytest              # backend
cd app/frontend && npm test                     # frontend
cd evaluation && python evaluate_cases.py       # evaluation
```

## Project structure

```
app/backend/forgepulse_api/   FastAPI app, services, security, schemas
app/frontend/src/             React UI (components, lib, types)
agent/prompts/                LLM system + diagnosis prompts
data/samples/                 5 industrial cases
evaluation/                   golden cases + evaluation harness
scripts/                      static export, LLM verifier
docs/                         architecture, security, deployment
Dockerfile                    single-image deploy (port 7860, non-root)
```

## Deployment

ForgePulse deploys as a Docker Space on HuggingFace (free CPU tier). The repo-root `Dockerfile` builds the frontend and serves everything from one process on port 7860. Step-by-step: [`docs/HUGGINGFACE_DEPLOY.md`](docs/HUGGINGFACE_DEPLOY.md).

## Safety boundaries

- **Read-only.** ForgePulse diagnoses and recommends; it does not control equipment.
- **Deterministic first.** Structured conclusions come from the engine, not the LLM. The LLM only reviews.
- **Auth required for production.** Configure `FORGEPULSE_API_KEYS`; the backend logs a warning in open mode.
- **Synthetic data.** The 5 cases are demo data. Real plant integration is on-site work, not part of this repo.

## License

MIT
