# HuggingFace Spaces Deployment

ForgePulse can run as a **full live stack** (real backend + real LLM advisory
agent + auth) on a free HuggingFace Space using the Docker SDK. This is the
recommended path for a public, fully-functional demo — GitHub Pages only serves
the static/offline build (no live backend, no LLM).

## What runs

A single Docker container (repo-root `Dockerfile`) runs one FastAPI process that:
- serves the built React frontend at `/` (and `/assets/*`), and
- serves the API at `/health`, `/cases`, `/cases/{id}/diagnosis`, etc.

The frontend is built with `VITE_LIVE_API=true`, so it calls the API on the same
origin — no CORS, no separate backend host.

The container listens on port **7860** (HuggingFace default) and runs as a
non-root user, per HuggingFace policy.

## Cost

- HuggingFace CPU Space: **free** (2 vCPU / 16 GB). No GPU needed — the LLM call
  is forwarded to an external OpenAI-compatible endpoint.
- The Space sleeps after inactivity (cold start ~tens of seconds on next visit).
- The LLM provider you configure charges separately (or use a free-tier/local model for zero cost).

## Step-by-step

### 1. Create the Space

1. Go to <https://huggingface.co/new-space>.
2. Name it (e.g. `forgepulse`), license, visibility (public is fine for a demo).
3. **SDK: Docker**, **Space hardware: CPU basic (free)**.
4. Create.

### 2. Set the Space's README frontmatter

The Space's root `README.md` must contain this YAML frontmatter (HF reads it to
configure the Space). When you push the repo, ensure the `README.md` starts with:

```yaml
---
title: ForgePulse
emoji: 🏭
colorFrom: indigo
colorTo: green
sdk: docker
app_port: 7860
pinned: false
---
```

You can keep the rest of the project README below it, or replace it.

### 3. Push the code

Clone the Space repo and push this project (the `Dockerfile` at repo root is
what HF builds):

```bash
git clone https://huggingface.co/spaces/<your-user>/forgepulse
# copy all project files into the clone, then:
cd forgepulse
git add .
git commit -m "Deploy ForgePulse to HuggingFace Space"
git push
```

HuggingFace builds the Docker image automatically and starts the Space. Watch
the "Logs" tab for build/runtime errors.

### 4. Configure Secrets (required for the real agent + auth)

In the Space → **Settings → Repository secrets**, add:

| Secret | Value | Purpose |
|---|---|---|
| `FORGEPULSE_MODEL_PROVIDER` | `openai_compatible` | Enable the LLM advisory layer |
| `FORGEPULSE_MODEL_BASE_URL` | `https://<your-endpoint>/v1` | OpenAI-compatible endpoint |
| `FORGEPULSE_MODEL_API_KEY` | `<your key>` | LLM credential (not visible in UI) |
| `FORGEPULSE_MODEL_NAME` | `<model name>` | Model to call |
| `FORGEPULSE_API_KEYS` | `alice-key:admin,bob-key:viewer` | API auth (omit only for public open demo) |
| `FORGEPULSE_RATE_LIMIT` | `60` | Per-key requests/minute |

Secrets are injected as environment variables at runtime — never written to the
repo. Restart the Space after adding/changing secrets.

> If you leave `FORGEPULSE_API_KEYS` unset, the API runs in **open mode** (no
> auth) — acceptable for a public read-only demo, but the backend will log a
> warning. Set a key for any production use.

### 5. Verify

- Visit the Space URL → you should see the ForgePulse workbench with 5 cases.
- The "AI 复核" block appears in the Agent decision panel when the LLM is
  configured and `?reasoning=auto` (default) returns a review.
- `/health` shows `provider_mode: openai_compatible` when the LLM is wired up.

## Local test of the Docker image (optional)

```bash
docker build -t forgepulse .
docker run --rm -p 7860:7860 \
  -e FORGEPULSE_MODEL_PROVIDER=openai_compatible \
  -e FORGEPULSE_MODEL_BASE_URL=... \
  -e FORGEPULSE_MODEL_API_KEY=... \
  -e FORGEPULSE_MODEL_NAME=... \
  forgepulse
# open http://localhost:7860
```

## Notes / limits

- The 5 cases are synthetic demo data (same as local). Real factory SCADA
  integration is out of scope here (see `docs/SECURITY_AND_SAFETY_BOUNDARIES.md`).
- Free Spaces sleep when idle; the first request after sleep takes a few seconds.
- The deterministic engine runs live on every request; the LLM review is the
  only optional, advisory layer and falls back gracefully if the endpoint fails.
