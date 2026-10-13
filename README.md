# 🚀 Rover-Slim: Autonomous Container Optimization Engine & Docker & Rancher Desktop Extension

[![Install in Docker Desktop](https://img.shields.io/badge/Docker%20Desktop-Install%20Extension-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://open.docker.com/extensions/marketplace?extensionId=bsankarganesh/rover-slim-extension&tag=latest)
[![GitHub Action](https://img.shields.io/badge/GitHub%20Action-v1-2088FF?style=flat&logo=githubactions&logoColor=white)](https://github.com/SankarGaneshb/rover-slim/releases/tag/v1.1.1)
[![CI Test Suite](https://github.com/SankarGaneshb/rover-slim/actions/workflows/ci.yml/badge.svg)](https://github.com/SankarGaneshb/rover-slim/actions)
[![Coverage](https://img.shields.io/badge/coverage-90%25-brightgreen.svg)](https://github.com/SankarGaneshb/rover-slim)
[![Extension Release](https://img.shields.io/badge/Extension-v1.1.2-blue.svg)](https://github.com/SankarGaneshb/rover-slim/releases/tag/v1.1.2)
[![Install in Rancher Desktop](https://img.shields.io/badge/Rancher%20Desktop-Install%20Extension-0075A8?style=for-the-badge&logo=suse&logoColor=white)](https://github.com/rancher-sandbox/rancher-desktop/pull/11115)
[![Python Version](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12%20%7C%203.13-blue.svg)](https://python.org)
[![M8ven Trust](https://m8ven.ai/badge/mcp/sankarganeshb/rover-slim?variant=verified)](https://m8ven.ai/mcp/sankarganeshb/rover-slim?s=readme)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Rover-Slim** is an intelligent, source-first container optimization engine and official **Docker & Rancher Desktop Extension** that analyzes application Abstract Syntax Trees (AST), automatically segregates development bloat from minimal production dependencies, synthesizes hardened multi-stage Dockerfiles, and guarantees zero runtime breakage via **Green-on-Arrival (GoA)** Sentinel health checks.

---

## 📸 Docker & Rancher Desktop Extension Dashboard

![Rover-Slim Dashboard](docs/dashboard.png)

---

## 🎯 Key Capabilities

- **🧬 AST-Driven Dependency Segregation**: Parses Python source syntax trees to detect genuine runtime `import` statements, generating lean `requirements-prod.txt` while quarantining dev tools (`pytest`, `black`, `ruff`, `locust`).
- **🏗️ Deterministic Multi-Stage Synthesis**: Synthesizes 2-stage and 3-stage minimal multi-arch Dockerfiles running under unprivileged non-root users (`appuser`, UID `10001`).
- **🛡️ Context Shielding (`.dockerignore`)**: Automatically detects and shields build contexts from heavy test caches, `.git`, `node_modules`, and local state.
- **⚡ Green-on-Arrival (GoA) Sentinel**: Boots ephemeral container sandboxes to verify startup integrity, validate active HTTP health probes (`/health`), and verify static asset graphs before final deployment.
- **🐳 Docker & Rancher Desktop Extension Workbench**: Interactive visual studio featuring live KPI gauges, 2-column drag-and-drop dependency classifier, side-by-side Monaco diff inspector, 1-click **Apply** with safety checkpoint rollback, and export hub.
- **🤖 Model Context Protocol (MCP) Server**: Built-in stdio MCP server for agentic IDEs (Antigravity, Cursor, Claude Desktop), officially listed on [M8ven MCP Registry & Trust Index](https://m8ven.ai/mcp/sankarganeshb/rover-slim) as a **Verified Publisher** with full safety tool annotations.

---

## 📊 Performance Benchmarks (Real-World Service)

| Metric | Fat / Baseline Container | Rover-Slim Optimized | Total Savings / Delta |
|---|---|---|---|
| **Uncompressed Image Size** | 1,232.7 MB | **214.6 MB** | **-1,018.1 MB (-82.6%)** |
| **Registry Transfer (Compressed)** | 443.8 MB | **68.7 MB** | **-375.1 MB (-84.5%)** |
| **Build Context Size** | 10.2 MB | **2.4 MB** | **-7.8 MB (-76.5%)** |
| **OCI Image Layers** | 18 layers | **8 layers** | **-10 layers** |
| **Installed Packages** | 40 packages | **12 packages** | **-28 packages** |
| **Runtime GoA Sentinel** | Untested / Breakage Risk | **100% Verified Green** | **Zero Breaking Changes** |

---

## 🐳 Docker & Rancher Desktop Extension

### 1. Install in Rancher Desktop
Install directly via the Rancher Desktop CLI (`rdctl`):
```bash
rdctl extension install bsankarganesh/rover-slim-extension:latest
```
*Or discover in the **Extensions → Catalog** tab once the [official catalog PR #11115](https://github.com/rancher-sandbox/rancher-desktop/pull/11115) merges!*

### 2. Install in Docker Desktop
Click below to open Docker Desktop directly and install Rover-Slim:

[![Install in Docker Desktop](https://img.shields.io/badge/Docker%20Desktop-Install%20Extension-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://open.docker.com/extensions/marketplace?extensionId=bsankarganesh/rover-slim-extension&tag=latest)

Or install via Docker CLI:
```bash
docker extension install bsankarganesh/rover-slim-extension:latest
```

### 3. Launch the Extension
Open **Rancher Desktop** or **Docker Desktop** and click **Rover Slim** in the left navigation sidebar!

### 4. Extension Features
- **Library Discovery**: Select local Docker images or project repositories.
- **Interactive Matrix**: Review and customize package splits (Production vs. Development).
- **Diff Inspector**: Inspect generated multi-stage Dockerfiles side-by-side.
- **GoA Sentinel**: Run live HTTP health probes and ephemeral container sandboxes.
- **Export Hub**: Generate GitHub PR descriptions, CI/CD YAML workflows, and SBOMs.

---

## 💻 CLI Usage & Quickstart

### 1. Install Core CLI
```bash
pip install -e .
```

### 2. Audit Container & Bloat
```bash
# Audit current directory or existing Docker image
rover-slim audit .
rover-slim audit . --image my-app:latest
```

### 3. Run End-to-End Optimization
```bash
# Run AST segregation, Dockerfile synthesis, and GoA verification
rover-slim optimize . --verify-goa

# Interactive wizard mode
rover-slim optimize . --interactive

# Multi-Architecture build output (amd64 + arm64)
rover-slim optimize . --multi-arch
```

### 4. View Side-by-Side Structural Diff
```bash
rover-slim diff .
```

### 5. Generate Software Bill of Materials (SBOM)
```bash
# Generates SPDX 2.3 and CycloneDX 1.5 SBOMs
rover-slim sbom . --output .rover-slim
```

### 6. Continuous File Watcher Mode
```bash
# Automatically synchronizes requirements-prod.txt upon source code edits
rover-slim watch .
```

### 7. Safety Rollback Checkpoints
```bash
# Restores files from previous snapshot backup
rover-slim rollback .
```

---

## 🤖 Model Context Protocol (MCP) Server

[![M8ven Trust Index](https://m8ven.ai/badge/mcp/sankarganeshb/rover-slim?variant=verified)](https://m8ven.ai/mcp/sankarganeshb/rover-slim?s=readme)
[![M8ven Verified Publisher](https://img.shields.io/badge/M8ven-Verified%20Publisher-10B981?style=flat&logo=checkmarx&logoColor=white)](https://m8ven.ai/mcp/sankarganeshb/rover-slim)

Rover-Slim is an officially listed and verified server on the **[M8ven MCP Registry & Trust Index](https://m8ven.ai/mcp/sankarganeshb/rover-slim)** under **Verified Publisher** status (`@SankarGaneshb`), continuously monitored for security, stability, and MCP schema compliance.

It includes a native Model Context Protocol (MCP) server for seamless integration with agentic coding environments (Antigravity, Cursor, Claude Desktop, Windsurf):

```json
{
  "mcpServers": {
    "rover-slim": {
      "command": "rover-slim",
      "args": ["mcp"]
    }
  }
}
```

### 🛡️ Exposed Tools & Safety Annotations
Rover-Slim adheres to the official MCP specification risk vocabulary and OpenAI MCP directory standards. Every exposed tool declares explicit boolean hints (`readOnlyHint`, `destructiveHint`, `idempotentHint`, and `openWorldHint`):

| Tool | Description | `readOnlyHint` | `destructiveHint` | `idempotentHint` | `openWorldHint` |
|---|---|:---:|:---:|:---:|:---:|
| `audit_container` | Audits directory or image for bloat, wasted layers, context leaks, and CVEs | `true` | `false` | `true` | `false` |
| `get_markdown_report` | Generates GitHub PR markdown diff summary report | `true` | `false` | `true` | `false` |
| `verify_goa` | Runs Green-on-Arrival Sentinel runtime boot integrity & health probes | `true` | `false` | `true` | `false` |
| `optimize_project` | Runs end-to-end container optimization & writes multi-stage Dockerfile | `false` | `true` | `true` | `false` |

> 🛡️ **Autonomous Safety**: Read-only inspection tools execute frictionlessly in agentic IDEs without confirmation prompts, while `optimize_project` signals `destructiveHint: true` so hosts warn users before modifying files.

---

## ⚙️ Configuration (`.rover-slim.yaml`)

```yaml
version: "1.0"
project_name: "my-service"

thresholds:
  max_image_size_mb: 350.0
  max_wasted_percent: 10.0
  max_cold_start_seconds: 2.5
  fail_on_cve_severity: ["CRITICAL"]

build:
  target_base_image: "python:3.13-slim"
  enable_multistage: true
  strip_node_runtime: true
  frontend_dist_path: "static/"

verification:
  auto_discover: true
  startup_command: "python -c 'import server; print(\"[OK] Startup Integrity verified\")'"
  probes:
    - name: "HTTP Root Health"
      type: "http"
      path: "/health"
      port: 8080
      expected_status: 200
      timeout_seconds: 10
```

---

## 🧪 Testing & Verification

```bash
# Run full Python test suite (81 tests, 90% coverage)
pytest -v --cov=rover_slim --cov-report=term-missing

# Run Extension React UI component test suite (6 suites, 100% green)
cd extension/ui && npm test
```

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

### 2. Install in Rancher Desktop
Rover-Slim natively supports Rancher Desktop (via its Docker-compatible extension architecture).

1. Start Rancher Desktop (with the **dockerd (Moby)** container engine enabled in Preferences).
2. Install via the CLI:
   ``bash
   rdctl extension install bsankarganesh/rover-slim-extension:latest
   ``
3. Open the **Rancher Desktop UI**, navigate to the **Extensions** tab, and click **Rover Slim**!

> *Note: We are actively submitting Rover Slim to the official Rancher Desktop Extension Catalog for 1-click UI installations.*
