# syntax=docker/dockerfile:1
#
# HuggingFace Spaces (Docker SDK) deployment for ForgePulse.
# Serves the FastAPI backend AND the built frontend from one process on port 7860
# (HuggingFace Spaces default). Runs as non-root user (HF requirement).
#
# Build context = repository root.

# ---------- Stage 1: build the frontend ----------
FROM node:20-bookworm AS frontend-build
WORKDIR /build

# Install deps first for better layer caching
COPY app/frontend/package.json app/frontend/package-lock.json ./
RUN npm ci

# Copy frontend sources
COPY app/frontend/ ./

# Build in live same-origin mode: the frontend calls the API on the same origin
# (FastAPI serves both). Vite reads .env.production for the build.
RUN echo "VITE_LIVE_API=true" > .env.production && npm run build

# ---------- Stage 2: runtime ----------
FROM python:3.11-slim AS runtime

# HuggingFace Spaces require a non-root user
RUN useradd -m -u 1000 user

WORKDIR /home/user/app

# Install backend runtime dependencies directly (no editable install needed)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir "fastapi>=0.115" "uvicorn[standard]>=0.30" "pydantic>=2.7"

# Copy backend source (case_loader resolves repo root via parents[4] = /home/user/app)
COPY app/backend/forgepulse_api ./app/backend/forgepulse_api

# Copy data (cases + fault modes) and scripts
COPY data ./data
COPY scripts ./scripts

# Copy built frontend
COPY --from=frontend-build /build/dist ./app/frontend/dist

# Ensure non-root ownership
RUN chown -R user:user /home/user/app

USER user

# Backend imports `forgepulse_api.*`; static dir enables single-process frontend serving.
ENV PYTHONPATH=/home/user/app/app/backend \
    FORGEPULSE_STATIC_DIR=/home/user/app/app/frontend/dist \
    PYTHONUNBUFFERED=1 \
    FORGEPULSE_LOG_LEVEL=INFO

EXPOSE 7860
WORKDIR /home/user/app/app/backend

# Bind to 0.0.0.0 so HuggingFace's reverse proxy can reach the container.
CMD ["python", "-m", "uvicorn", "forgepulse_api.main:app", "--host", "0.0.0.0", "--port", "7860"]
