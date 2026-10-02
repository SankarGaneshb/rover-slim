# syntax=docker/dockerfile:1

# ==============================================================================
# STAGE 1: Frontend UI Production Compilation (Cross-Architecture Host Accelerated)
# ==============================================================================
FROM --platform=$BUILDPLATFORM node:20-alpine AS ui-builder
WORKDIR /ui
COPY extension/ui/package*.json ./
RUN npm install --frozen-lockfile || npm install
COPY extension/ui/ ./
RUN npm run build

# ==============================================================================
# STAGE 2: Ephemeral Python Dependency & Wheel Builder
# ==============================================================================
FROM python:3.13-slim AS python-builder
WORKDIR /build

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*

COPY requirements-prod.txt .
RUN pip install --no-cache-dir --user -r requirements-prod.txt

COPY pyproject.toml .
COPY rover_slim/ rover_slim/
RUN pip install --no-cache-dir --user --no-deps -e .

# ==============================================================================
# STAGE 3: Minimal Multi-Arch Production Extension Runtime
# ==============================================================================
FROM python:3.13-slim AS runtime
WORKDIR /backend

# Clean runtime environment with zero build tools or package manager caches
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Copy pre-compiled Python packages from python-builder stage
COPY --from=python-builder /root/.local /root/.local

# Copy Rover-Slim core source and project metadata
COPY pyproject.toml .
COPY rover_slim/ rover_slim/

# Copy Extension manifests and UI distribution bundle
COPY extension/metadata.json /metadata.json
COPY extension/docker-compose.yaml /docker-compose.yaml
COPY extension/icon.svg /icon.svg
COPY --from=ui-builder /ui/dist /ui

# Configure runtime execution environment
ENV PATH="/root/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/backend:$PYTHONPATH"

EXPOSE 8000

# Official Docker Desktop Extension & OCI Labels
LABEL org.opencontainers.image.title="Rover-Slim" \
      org.opencontainers.image.description="Autonomous Container Optimization, AST Dependency Segregation, and GoA Sentinel Verification" \
      org.opencontainers.image.vendor="Rover-Slim Team" \
      com.docker.desktop.extension.api.version=">= 0.3.4" \
      com.docker.extension.icon="icon.svg" \
      com.docker.desktop.extension.icon="icon.svg" \
      com.docker.extension.categories="utility-tools,developer-tools" \
      com.docker.extension.screenshots='[{"url": "https://raw.githubusercontent.com/SankarGaneshb/rover-slim/main/docs/dashboard.png", "alt": "Rover-Slim Extension Dashboard"}]' \
      com.docker.extension.detailed-description="Rover-Slim analyzes Python AST code trees, segregates dev dependencies, synthesizes lean multi-stage Dockerfiles, and guarantees Green-on-Arrival container health." \
      com.docker.extension.publisher-url="https://github.com/SankarGaneshb/rover-slim" \
      com.docker.extension.additional-urls='[{"title":"Documentation","url":"https://github.com/SankarGaneshb/rover-slim"}]' \
      com.docker.extension.changelog="v1.0.0 Self-Optimized Multi-Stage Release."

CMD ["uvicorn", "rover_slim.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
