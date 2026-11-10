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

---

## 🔄 Session & Feature Formalization Workflow

To maintain full transparency and ensure future contributors (both human developers and AI coding assistants) understand the rationale behind changes, **Rover-Slim** follows a structured **Session-to-GitHub Lifecycle**:

1. **Discussion & Conclusion**:
   - Ideas, architectural improvements, and review findings discussed in pair-programming or AI sessions are synthesized into clear problem statements and proposed solutions.
2. **Formalization to GitHub Issues**:
   - Rather than remaining in local transcripts or ephemeral chats, concluded items are converted into tracked [GitHub Issues](https://github.com/SankarGaneshb/rover-slim/issues) using the appropriate issue template (`bug_report.yml`, `feature_request.yml`, or `rfc_proposal.yml`).
   - For architectural shifts, an Architecture Decision Record (ADR) is added to `docs/decisions/`.
3. **PR-First Branching Model**:
   - Never push directly to `main`. Always branch off `main` using standard naming conventions:
     - `feat/<issue-number>-<short-description>`
     - `fix/<issue-number>-<short-description>`
     - `docs/<issue-number>-<short-description>`
   - Link the PR to the issue in the description using GitHub keywords (e.g., `Closes #12`).
4. **Green-on-Arrival (GoA) CI Verification**:
   - All PRs must pass the CI pipeline (`ci.yml`): Python tests across matrix 3.10–3.13, Vitest UI suite, and self-optimization dogfooding before merging.
5. **Issue Resolution & Metric Health**:
   - Merging the PR automatically closes the issue, elevating the project's health and maintenance score across community indices (such as SilentStars).
6. **Automated Contributor Acknowledgement**:
   - Every incoming PR is greeted in real-time by the workflow in `.github/workflows/pr-acknowledgement.yml`. For onboarding new repositories, see [docs/governance/CONTRIBUTOR_PR_ACKNOWLEDGEMENT.md](docs/governance/CONTRIBUTOR_PR_ACKNOWLEDGEMENT.md).

---

## 🌟 Good First Issues & Contributor Areas

New contributors are strongly encouraged to explore issues labeled [`good first issue`](https://github.com/SankarGaneshb/rover-slim/labels/good%20first%20issue) or [`help wanted`](https://github.com/SankarGaneshb/rover-slim/labels/help%20wanted).

Popular areas to contribute:
* **AST Language Parsers**: Extending detection rules for emerging frameworks in Python, Node.js, Java, and .NET.
* **Extension UI (React/TypeScript)**: Enhancing Docker/Rancher Desktop dashboards, chart visualizations, and theme support.
* **Documentation & Samples**: Adding sample projects, benchmarks, and multi-cloud CI/CD recipes.
* **GoA Sentinel Verifiers**: Adding new health check strategies for complex microservice topologies.

