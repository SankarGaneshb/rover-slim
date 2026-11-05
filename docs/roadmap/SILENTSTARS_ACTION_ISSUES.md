# Formalized GitHub Issues: SilentStars Evaluation & Community Health

This document contains structured GitHub issue definitions derived from the SilentStars review of **Rover-Slim** ([review URL](https://silentstars.dev/projects/sankarganeshb--rover-slim/)).

These issues are designed to be published to [GitHub Issues](https://github.com/SankarGaneshb/rover-slim/issues) using `python scripts/sync_session_issues.py` (or manually via `gh issue create`).

---

## ISSUE 1

* **Title**: `[Release]: Publish Release v0.5.1 / v1.0.0 to unlock 'release_machine' cadence`
* **Labels**: `release`, `governance`
* **Description**:
```markdown
### 🎯 Objective
SilentStars currently records Rover-Slim with 4 releases in the last 90 days. The `// release_machine` behavioral tag is awarded to repositories with 5 or more releases in a 90-day window.

### 📋 Scope of Work
- [ ] Collate changelog for recent enhancements (AST dependency segregation improvements, Docker extension UI updates, GitHub Action v1 refinements).
- [ ] Tag git commit as `v0.5.1` (or `v1.0.0`).
- [ ] Publish official GitHub Release with release notes and build assets.
- [ ] Verify Docker Hub extension container image tag synchronization (`bsankarganesh/rover-slim-extension`).

### ✅ Acceptance Criteria
- GitHub repository has 5 recorded releases in the last 90 days.
- SilentStars refreshes nightly and assigns the `// release_machine` badge.
```

---

## ISSUE 2

* **Title**: `[Community / Good First Issue]: Add .github/FUNDING.yml and document sponsorship channels`
* **Labels**: `good first issue`, `documentation`, `community`
* **Description**:
```markdown
### 🎯 Objective
Enable project sponsorship transparency and unlock the SilentStars `// funded` behavioral tag by providing official funding configurations.

### 📋 Scope of Work
- [ ] Verify `.github/FUNDING.yml` is present in the repository root.
- [ ] Configure maintainer sponsor platform handles (GitHub Sponsors: `SankarGaneshb`, optional BuyMeACoffee/Patreon).
- [ ] Add a `## 💖 Sponsor & Support` badge and section to `README.md`.

### ✅ Acceptance Criteria
- GitHub renders the "Sponsor this project" heart icon in the repository sidebar.
- SilentStars nightly indexer identifies active funding and attaches the `// funded` tag.
```

---

## ISSUE 3

* **Title**: `[Community]: Enable GitHub Discussions and seed knowledge base categories`
* **Labels**: `community`, `enhancement`
* **Description**:
```markdown
### 🎯 Objective
Transform Rover-Slim from a solo builder project into a welcoming open-source community hub (`// community_hub` tag requires GitHub Discussions with community interaction).

### 📋 Scope of Work
- [ ] Enable GitHub Discussions in Repository Settings -> Features -> Discussions.
- [ ] Seed standard categories:
  - 💬 **General**: Community introductions and open-source Docker optimization ideas.
  - 💡 **Ideas & RFCs**: Proposed language parsers and feature requests.
  - 🙋 **Q&A / Help**: Troubleshooting container optimization and GoA Sentinel verification.
  - 🙌 **Show & Tell**: Share container size reductions achieved using Rover-Slim.
- [ ] Post a welcome pinned announcement with links to the Quickstart and Docker Extension.

### ✅ Acceptance Criteria
- Discussions tab is visible publicly on GitHub.
- Initial welcome post and categories are configured.
```

---

## ISSUE 4

* **Title**: `[Onboarding / Good First Issue]: Curate beginner-friendly AST parser stubs`
* **Labels**: `good first issue`, `help wanted`, `core`
* **Description**:
```markdown
### 🎯 Objective
Attract new contributors to Rover-Slim's polyglot container optimization engine by curating well-isolated beginner issues and unlocking the `// needs_contributors` SilentStars signal.

### 📋 Scope of Work
- [ ] Create stub / specification for a new AST parser (e.g. Go module analyzer `go.mod` / Rust Cargo `Cargo.toml`).
- [ ] Add clear contribution instructions, sample fixture files in `tests/fixtures/`, and expected JSON schema outputs.
- [ ] Ensure issues are tagged with both `good first issue` and `help wanted`.

### ✅ Acceptance Criteria
- At least 2 active issues carry the `good first issue` and `help wanted` labels.
- Documentation points prospective contributors to `CONTRIBUTING.md#good-first-issues`.
```

---

## ISSUE 5

* **Title**: `[Governance / CI]: Formalize branch protection and PR-only merges to main`
* **Labels**: `ci/cd`, `governance`
* **Description**:
```markdown
### 🎯 Objective
Elevate the project's **Health Score** from `77 / Stable` to `85–100 / Healthy` by ensuring all code changes flow through Pull Requests with automated Green-on-Arrival (GoA) Sentinel verification.

### 📋 Scope of Work
- [ ] Configure GitHub Branch Protection on `main` / `master`:
  - Require a pull request before merging.
  - Require status checks to pass before merging:
    - `python-tests` (matrix 3.10–3.13)
    - `ui-tests` (Vitest & production build)
    - `dogfood-self-optimization` (GoA Sentinel check)
- [ ] Ensure every new feature branch links to an issue using `Closes #<issue_number>`.

### ✅ Acceptance Criteria
- Direct pushes to `main` are prevented.
- All merged PRs automatically resolve their corresponding issues, driving `pr_health` and `issue_health` to 100%.
```
