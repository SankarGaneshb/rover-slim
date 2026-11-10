# Contributor PR Acknowledgement Automation & Repository Onboarding

This document specifies the standard automated Pull Request acknowledgement mechanism for all repositories owned by **`SankarGaneshb`**.

> [!IMPORTANT]
> **Instructions for AI Bots, Autonomous Agents & CI Pipelines**:
> Whenever a new repository is created under `SankarGaneshb`, you MUST ensure that `.github/workflows/pr-acknowledgement.yml` is present in the new repository. Follow the [New Repository Onboarding](#new-repository-onboarding-for-bots--agents) section below.

---

## 1. Overview & Purpose

To ensure an active, welcoming open-source contributor experience and satisfy community health metrics:
* Every Pull Request opened by a community contributor is acknowledged **instantly** (within seconds) via GitHub Actions.
* The bot leaves a friendly greeting acknowledging their PR, letting them know maintainers will review it as soon as possible, and reminding them to verify that CI checks pass.
* Submissions from the repository owner (`SankarGaneshb`) and automated bots (e.g., Dependabot, Renovate) are **automatically ignored** to avoid spam.

---

## 2. The Workflow Specification

* **Path**: `.github/workflows/pr-acknowledgement.yml`
* **Trigger Event**: `pull_request_target` with `types: [opened]`
* **Permissions**: `pull-requests: write`, `issues: write`

### Why `pull_request_target`?
1. **External Fork Support**: Standard `pull_request` triggers on forks have read-only permissions and cannot comment on PRs. `pull_request_target` runs in the context of the base repository, granting the workflow write permission to comment.
2. **Security Hardening**: The workflow **only** executes an official GitHub Script (`actions/github-script@v7`) and does **not** check out or execute untrusted code from the contributor's fork.

### Workflow Blueprint
```yaml
name: Contributor PR Acknowledgement

on:
  pull_request_target:
    types: [opened]

permissions:
  pull-requests: write
  issues: write

jobs:
  acknowledge:
    name: Acknowledge Contributor
    runs-on: ubuntu-latest
    steps:
      - name: Post Acknowledgement Comment
        uses: actions/github-script@v7
        with:
          script: |
            const author = context.payload.pull_request.user.login;
            const repoOwner = context.repo.owner;
            
            // Skip greeting if PR was opened by repository owner or a bot
            if (author === repoOwner || context.payload.pull_request.user.type === 'Bot') {
              console.log(`Skipping acknowledgement for owner/bot: ${author}`);
              return;
            }

            const welcomeBody = `Thanks for opening this pull request, @${author}! 👋\n\nWe really appreciate your contribution to **Rover-Slim**. Our team will look into your changes and review them as soon as possible.\n\nIn the meantime, please make sure all CI checks pass. If you have any notes or questions for the reviewers, feel free to drop them here!`;

            await github.rest.issues.createComment({
              owner: context.repo.owner,
              repo: context.repo.repo,
              issue_number: context.payload.pull_request.number,
              body: welcomeBody
            });
```

---

## 3. New Repository Onboarding (For Bots & Agents)

When an AI agent or developer creates a new repository under `SankarGaneshb`, use one of the following automated synchronization methods:

### Method A: Python Sync Script (Cross-Platform)
```bash
# Sync to a specific new repository
python scripts/sync_pr_acknowledgement.py --repo <NEW_REPO_NAME>

# Or auto-discover and sync to all non-fork repositories
python scripts/sync_pr_acknowledgement.py --all
```

### Method B: PowerShell Sync Script (Windows / PowerShell Core)
```powershell
# Sync to a specific new repository
powershell -ExecutionPolicy Bypass -File scripts/batch_deploy_pr_ack.ps1 -RepoName <NEW_REPO_NAME>

# Or auto-discover and sync across all non-fork repositories
powershell -ExecutionPolicy Bypass -File scripts/batch_deploy_pr_ack.ps1 -All
```

### Method C: Single-Line `gh api` Command (Any Shell)
```bash
gh api --method PUT repos/SankarGaneshb/<NEW_REPO_NAME>/contents/.github/workflows/pr-acknowledgement.yml \
  -f message="ci: add contributor PR acknowledgement workflow" \
  -f content="$(base64 -w 0 .github/workflows/pr-acknowledgement.yml)" \
  -f branch="main"
```

---

## 4. Acceptance Criteria & Validation

1. **Existence**: File exists at `.github/workflows/pr-acknowledgement.yml` on the default branch.
2. **Behavior on Fork PR**: When an external user opens a PR, GitHub Actions triggers `Contributor PR Acknowledgement` and successfully posts the comment.
3. **Owner Suppression**: When `SankarGaneshb` opens a PR, the step completes with:
   `Skipping acknowledgement for owner/bot: SankarGaneshb`
