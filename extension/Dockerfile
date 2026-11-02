# syntax=docker/dockerfile:1

# ==============================================================================
# Docker Desktop Extension: Rover-Slim
#
# Packages both the FastAPI backend service and the compiled React UI into a
# multi-architecture Docker Desktop Extension image (`rover-slim:extension`).
#
# Canonical Local Build & Installation Commands:
#   1. Compile React UI production bundle (optional if already built):
#      cd extension/ui && npm run build && cd ../..
#
#   2. Build Extension image from repository root (canonical context):
#      docker build -t rover-slim:extension -f extension/Dockerfile .
#
#   3. Install Extension into Docker Desktop:
#      docker extension install rover-slim:extension
#
#   4. Verify Extension deployment & health:
#      docker extension ls
#      docker ps --filter "name=rover-slim"
#      curl http://localhost:40040/api/health
# ==============================================================================

# ==============================================================================
# STAGE 1: Frontend UI Production Compilation / Static Asset Packaging
# ==============================================================================
FROM --platform=$BUILDPLATFORM node:20-alpine AS ui-builder
WORKDIR /ui

# Cache dependency layer
COPY extension/ui/package*.json ./
RUN npm install --frozen-lockfile || npm install

# Copy source tree and compile production bundle into /ui/dist
COPY extension/ui/ ./
RUN if [ -f dist/index.html ]; then \
        echo "Using pre-compiled React UI distribution bundle from extension/ui/dist"; \
    else \
        npm run build; \
    fi

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

COPY README.md pyproject.toml ./
COPY rover_slim/ rover_slim/
RUN pip install --no-cache-dir --user --no-deps .

# ==============================================================================
# STAGE 3: Minimal Multi-Arch Production Extension Runtime
# ==============================================================================
FROM python:3.13-slim AS runtime
WORKDIR /backend

# Clean runtime environment with curl, ca-certificates, and static Docker CLI binary
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
 && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/* \
 && ARCH=$(uname -m) && \
    case "$ARCH" in \
      x86_64) DOCKER_ARCH="x86_64" ;; \
      aarch64) DOCKER_ARCH="aarch64" ;; \
      *) DOCKER_ARCH="x86_64" ;; \
    esac && \
    curl -fsSL "https://download.docker.com/linux/static/stable/${DOCKER_ARCH}/docker-27.3.1.tgz" | tar -xz -C /tmp && \
    mv /tmp/docker/docker /usr/local/bin/docker && \
    chmod 755 /usr/local/bin/docker && \
    rm -rf /tmp/docker

# Copy pre-compiled Python packages from python-builder stage
COPY --from=python-builder /root/.local /root/.local

# Copy Rover-Slim core source and project metadata
COPY README.md pyproject.toml ./
COPY rover_slim/ rover_slim/

# Copy Extension manifests, icon, and React UI distribution bundle
COPY extension/metadata.json /metadata.json
COPY extension/docker-compose.yaml /docker-compose.yaml
COPY extension/icon.svg /icon.svg
COPY --from=ui-builder /ui/dist /ui

# Configure runtime execution environment & security hardening
ENV PATH="/root/.local/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH="/backend:$PYTHONPATH"

# Ensure runtime directories and static assets have safe read permissions
RUN chmod -R 755 /backend /ui

EXPOSE 8000

# Docker Desktop Extension & OCI Labels
LABEL org.opencontainers.image.title="Rover-Slim" \
      org.opencontainers.image.description="Autonomous Container Optimization, Polyglot Dependency Segregation, and GoA Sentinel Verification" \
      org.opencontainers.image.vendor="Rover-Slim Team" \
      com.docker.desktop.extension.api.version=">= 0.3.4" \
      com.docker.extension.icon="https://raw.githubusercontent.com/SankarGaneshb/rover-slim/main/extension/icon.svg" \
      com.docker.desktop.extension.icon="https://raw.githubusercontent.com/SankarGaneshb/rover-slim/main/extension/icon.svg" \
      com.docker.extension.categories="utility-tools,developer-tools" \
      com.docker.extension.screenshots='[{"url": "https://raw.githubusercontent.com/SankarGaneshb/rover-slim/main/docs/dashboard.png", "alt": "Rover-Slim Extension Dashboard"}]' \
      com.docker.extension.detailed-description="Rover-Slim analyzes AST and manifest dependency trees across Python, Node.js, Java Spring Boot Layertools, and .NET Core 8/9, synthesizes lean multi-stage Dockerfiles, and guarantees Green-on-Arrival container health. Compatible with Docker Desktop and container runtimes." \
      com.docker.extension.publisher-url="https://github.com/SankarGaneshb/rover-slim" \
      com.docker.extension.additional-urls='[{"title":"Documentation","url":"https://github.com/SankarGaneshb/rover-slim"}]' \
      com.docker.extension.changelog="v1.1.2 Polyglot AST Architecture, Bloat Diagnoser, FinOps ROI & CIS Security Release."

CMD ["uvicorn", "rover_slim.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
