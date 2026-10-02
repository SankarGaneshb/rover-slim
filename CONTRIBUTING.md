# Contributing to Rover-Slim

Thank you for your interest in contributing to **Rover-Slim**! We welcome bug reports, feature requests, and pull requests.

---

## 🛠️ Development Setup

### 1. Prerequisites
- Python 3.10+ (Python 3.13 recommended)
- Node.js 20+ and npm
- Docker Desktop with Buildx enabled

### 2. Install Development Dependencies
```bash
git clone https://github.com/SankarGaneshb/rover-slim.git
cd rover-slim

# Install Python backend in editable mode with dev tools
pip install -e ".[dev]"
```

### 3. Running Backend Tests & Coverage
```bash
# Run pytest with code coverage
pytest -v --cov=rover_slim --cov-report=term-missing
```

### 4. Running Extension UI Tests
```bash
cd extension/ui
npm install
npm test
npm run build
```

---

## 🐳 Building the Docker Desktop Extension Locally

```bash
# Multi-arch local build
docker build -t bsankarganesh/rover-slim-extension:latest -f extension/Dockerfile .

# Install / update in Docker Desktop
docker extension install bsankarganesh/rover-slim-extension:latest
# Or update if already installed
docker extension update bsankarganesh/rover-slim-extension:latest
```

---

## 📜 Pull Request Guidelines
1. Ensure all 81+ Python tests and 6+ React Vitest component tests pass cleanly (`100% green`).
2. Maintain minimum 90% test coverage on new Python code.
3. Keep Dockerfiles minimal, non-root (`appuser`), and multi-arch compliant (`linux/amd64` and `linux/arm64`).
