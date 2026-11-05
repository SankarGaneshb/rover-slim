# ADR-001: Session-to-GitHub Synchronization and Contributor Lifecycle

* **Status**: Accepted
* **Date**: 2026-11-05
* **Deciders**: Sankar Ganesh, Antigravity AI Pair-Programming Engine
* **Context / Trigger**: Review by SilentStars (`https://silentstars.dev/projects/sankarganeshb--rover-slim/`) identified Rover-Slim as a high-signal, actively developed project (`Undervalued Score: 56`, `Health Score: 77 / Stable`).

---

## Context & Problem Statement

Rover-Slim's core engine, desktop extension, and CI actions evolve rapidly through iterative agent-assisted pair programming and architectural reviews. 

However, when architectural discoveries, roadmap milestones, and external platform evaluations (e.g. SilentStars score breakdowns) are conducted only within local sessions or conversation transcripts:
1. Future human and autonomous contributors lack visibility into why decisions were made.
2. The project's public GitHub activity displays 0 open issues and 0 closed issues, which artificially depresses the `issue_health` and `pr_health` signals used by open-source health evaluators.
3. Roadmap milestones remain undocumented in the repository's native GitHub Project/Issue tracking ecosystem.

---

## Decision Drivers

* **Transparency**: Ensure that any developer or agent joining Rover-Slim in the future can trace the lineage of features, bugs, and optimizations.
* **Community Health**: Directly drive the repository's health indicators (`Healthy 80–100` band) through standard, measurable issue resolution and PR merges.
* **Standardization**: Create an automated bridge between ephemeral interactive sessions and persistent GitHub assets.

---

## Considered Options

1. **Option 1 (Status Quo)**: Retain architectural plans in `.agents/` and commit code directly to `main`.
2. **Option 2 (Manual Logging)**: Rely on maintainers to manually remember to transcribe chat conclusions into GitHub issues.
3. **Option 3 (Formalized Session-to-GitHub Protocol + Tooling)**:
   - Establish an ADR framework in `docs/decisions/`.
   - Maintain a standardized Issue Backlog in `docs/roadmap/`.
   - Provide a CLI synchronization utility (`scripts/sync_session_issues.py`) to batch-publish structured issues with correct labels and milestones.
   - Enforce PR-first branch merges linking to tracked issues (`Closes #issue`).

---

## Decision Outcome

Chosen: **Option 3 (Formalized Session-to-GitHub Protocol + Tooling)**.

### Operational Process

```
[Agent/Maintainer Session] 
       │ 
       ▼
[Conclude Feature/Review] ──► Write/Update docs/roadmap/ & docs/decisions/
       │
       ▼
[Publish to GitHub] ────────► python scripts/sync_session_issues.py (or gh CLI)
       │
       ▼
[Branch & PR] ──────────────► feat/issue-<id> ──► PR linking "Closes #<id>"
       │
       ▼
[GoA CI Verification] ──────► Pytest + Vitest + GoA Sentinel
       │
       ▼
[Merge & Close Issue] ──────► Automated issue closure & public health metric gain
```

---

## Consequences

### Positive
* Complete auditability of every major initiative and design decision.
* New contributors can immediately find categorized tasks marked `good first issue` or `help wanted`.
* Open Source indexers (SilentStars, GitHub Insights) reflect continuous, healthy project management and community readiness.
* Unlocks SilentStars badges including `release_machine`, `funded`, and `needs_contributors`.

### Neutral / Operational Maintenance
* Every feature or fix must be tied to an issue and merged via a Pull Request rather than direct-to-main pushes.
