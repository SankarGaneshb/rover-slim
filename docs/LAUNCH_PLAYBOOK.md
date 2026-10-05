# Rover-Slim Community Launch & Distribution Playbook

This playbook provides battle-tested, pre-written launch posts and outreach messages to take **Rover-Slim** from 0 to 1,000+ installs on the Docker Desktop Extension Marketplace.

Marketplace Listing: [Rover-Slim on Docker Extensions](https://open.docker.com/extensions/marketplace?extensionId=bsankarganesh/rover-slim-extension&tag=latest)  
Repository: [https://github.com/SankarGaneshb/rover-slim](https://github.com/SankarGaneshb/rover-slim)

---

## 1. Reddit Launch: r/Python
- **Target Subreddit:** `r/Python`
- **Flair:** `Project` or `Showcase`
- **Best Time:** Tuesday / Wednesday / Thursday between 7:00 AM – 10:00 AM EST (4:30 PM – 7:30 PM IST)

### Title:
`I built an open-source Docker extension that uses Python AST to shrink images from 1.2 GB to ~200 MB (with zero-breakage health checks)`

### Body:
```markdown
Hey r/Python,

A common issue when containerizing Python web services (FastAPI, Flask, Django) is that images quickly balloon to 1+ GB because development dependencies (`pytest`, `black`, `ruff`, `jupyter`, `locust`), build toolchains (`gcc`), and cache files accidentally end up in the final runtime image.

Most guides tell you to manually write multi-stage Dockerfiles and `.dockerignore` files, but developers often worry: *"If I strip this library, will my container crash in production?"*

To solve this, I built **Rover-Slim**, an open-source Docker Desktop extension and CLI tool:

### 🔍 How it Works:
1. **AST-Driven Dependency Segregation:** It parses Python Abstract Syntax Trees across your codebase to detect genuine runtime `import` statements vs dev bloat, automatically separating them into clean production requirements.
2. **Deterministic Multi-Stage Synthesis:** Generates a production-ready, non-root (`appuser`, UID 10001) multi-stage Dockerfile with optimal layer caching.
3. **Context Shielding:** Automatically configures `.dockerignore` to prevent build context leakage from local caches and test folders.
4. **Green-on-Arrival (GoA) Sentinel:** Ephemerally boots a test container sandbox inside Docker Desktop to verify startup integrity and test HTTP health probes (`/health`) before letting you apply changes. If anything fails, it safely rolls back with zero disruption.

### 📊 Real-World Benchmark on a Python Service:
- **Image Size:** 1,232.7 MB ➔ **214.6 MB (-82.6%)**
- **Compressed Registry Transfer:** 443.8 MB ➔ **68.7 MB (-84.5%)**
- **OCI Layers:** 18 layers ➔ **8 layers**

### 📦 Try it out:
- **One-click Install in Docker Desktop:** [Open in Docker Extensions Marketplace](https://open.docker.com/extensions/marketplace?extensionId=bsankarganesh/rover-slim-extension&tag=latest)
- **CLI Install:** `docker extension install bsankarganesh/rover-slim-extension:latest`
- **GitHub:** [https://github.com/SankarGaneshb/rover-slim](https://github.com/SankarGaneshb/rover-slim)

The project is completely free and MIT-licensed. I’d love to hear your thoughts, feedback, and any edge-case Python dependencies you run into!
```

---

## 2. Reddit Launch: r/docker & r/devops
- **Target Subreddits:** `r/docker`, `r/devops`
- **Flair:** `Tool / Project`

### Title:
`Rover-Slim: Open-source Docker Desktop extension to automate multi-stage builds & shrink Python images by 80%`

### Body:
```markdown
Hey everyone,

Whenever teams containerize Python apps, images almost always suffer from layer bloat, dev tools packaged into production, and unoptimized multi-stage caching.

I built **Rover-Slim**, an open-source Docker Desktop extension that automates the entire optimization workflow without breaking your app:

- **AST Inspection:** Analyzes Python ASTs to segregate runtime imports from test/lint bloat (`pytest`, `black`, `ruff`, etc.).
- **Multi-Stage Synthesis:** Emits hardened multi-stage Dockerfiles running as unprivileged non-root users (`appuser`, UID 10001).
- **Green-on-Arrival Sentinel:** Runs ephemeral container health checks (`/health`) before applying changes so you never push a broken container.
- **Supply Chain Hub:** 1-click generation of SPDX 2.3 & CycloneDX 1.5 SBOMs.

It's now officially published on the Docker Extensions Marketplace:
👉 [Install in Docker Desktop](https://open.docker.com/extensions/marketplace?extensionId=bsankarganesh/rover-slim-extension&tag=latest)  
👉 GitHub: [https://github.com/SankarGaneshb/rover-slim](https://github.com/SankarGaneshb/rover-slim)

Feedback and PRs are very welcome!
```

---

## 3. Hacker News: Show HN
- **Platform:** news.ycombinator.com
- **Submission Title:** `Show HN: Rover-Slim – Docker Desktop extension to slim Python containers via AST`
- **URL:** `https://github.com/SankarGaneshb/rover-slim`

### First Comment (Post immediately after submitting):
```text
Hi HN,

I built Rover-Slim to solve a frustrating problem with Python containers: images blowing up past 1 GB due to development tools (pytest, ruff, compilers) inadvertently ending up in the final build.

Writing multi-stage Dockerfiles manually works, but developers usually don't know which transitive dependencies are strictly required at runtime, or they're afraid of stripping something that causes a silent runtime crash.

Rover-Slim analyzes the Python AST to separate runtime imports from dev packages, synthesizes hardened 2/3-stage non-root Dockerfiles, and runs an ephemeral "Green-on-Arrival" health probe in a test container before allowing changes to be applied.

It's available as an open-source Docker Desktop Extension (https://open.docker.com/extensions/marketplace?extensionId=bsankarganesh/rover-slim-extension&tag=latest) and as a CLI.

Architecture and source: https://github.com/SankarGaneshb/rover-slim

Looking forward to your comments and feedback!
```

---

## 4. Docker Community Slack Outreach
- **Slack Workspace:** [Docker Community Slack](https://dockr.ly/slack)
- **Channels:** `#extensions`, `#show-and-tell`, `#python`

### Message:
```text
Hey everyone! 👋 
I'm excited to share that **Rover-Slim** is now live on the Docker Extensions Marketplace! 

It's an open-source extension designed to optimize Python containers:
• Analyzes Python AST code trees to isolate runtime vs dev dependencies.
• Generates minimal, non-root multi-stage Dockerfiles.
• Runs an ephemeral Green-on-Arrival (GoA) container sandbox to test startup integrity and HTTP health probes before applying changes.

In our real-world tests, it cut container sizes from 1.2 GB down to 214 MB (-82%).

You can try it directly inside Docker Desktop here:
👉 https://open.docker.com/extensions/marketplace?extensionId=bsankarganesh/rover-slim-extension&tag=latest

GitHub repo: https://github.com/SankarGaneshb/rover-slim

Feedback is warmly welcomed!
```

---

## 5. X (Twitter) & LinkedIn Launch Post
- **Hashtags:** `#Docker` `#Python` `#DevOps` `#DockerDesktop` `#OpenSource` `#CloudNative`

### Text:
```text
Tired of 1.2 GB Python Docker containers? 🐍🐳

I built and launched Rover-Slim — an open-source Docker Desktop Extension that uses Python AST analysis to strip dev bloat, synthesize hardened multi-stage Dockerfiles, and verify container health before deployment.

✨ Features:
• AST-driven runtime vs dev dependency isolation
• Non-root hardened multi-stage Dockerfile generation
• Green-on-Arrival (GoA) ephemeral health probes
• SPDX / CycloneDX SBOM exports

Benchmark: 1,232 MB ➔ 214 MB (-82% image size, -84% compressed registry transfer)

Now live on the official Docker Extensions Marketplace:
https://open.docker.com/extensions/marketplace?extensionId=bsankarganesh/rover-slim-extension&tag=latest

GitHub: https://github.com/SankarGaneshb/rover-slim
```
