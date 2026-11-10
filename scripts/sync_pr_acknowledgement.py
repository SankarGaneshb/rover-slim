#!/usr/bin/env python3
"""
Sync Contributor PR Acknowledgement Workflow to GitHub Repositories.
Usage:
    python scripts/sync_pr_acknowledgement.py --repo <REPO_NAME> [--branch main]
    python scripts/sync_pr_acknowledgement.py --all
"""

import argparse
import base64
import json
import os
import subprocess
import sys

OWNER = "SankarGaneshb"
WORKFLOW_RELATIVE_PATH = ".github/workflows/pr-acknowledgement.yml"


def get_workflow_base64(root_dir: str) -> str:
    wf_path = os.path.join(root_dir, WORKFLOW_RELATIVE_PATH)
    if not os.path.exists(wf_path):
        raise FileNotFoundError(f"Workflow file not found at {wf_path}")
    with open(wf_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def run_gh_json(args):
    cmd = ["gh"] + args
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if result.returncode != 0:
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return None


def get_existing_sha(repo: str, branch: str) -> str:
    path = f"repos/{OWNER}/{repo}/contents/{WORKFLOW_RELATIVE_PATH}?ref={branch}"
    data = run_gh_json(["api", path])
    if data and "sha" in data:
        return data["sha"]
    return None


def deploy_to_repo(repo: str, branch: str, b64_content: str) -> bool:
    sha = get_existing_sha(repo, branch)
    body = {
        "message": "ci: add contributor PR acknowledgement workflow",
        "content": b64_content,
        "branch": branch
    }
    if sha:
        body["sha"] = sha

    payload = json.dumps(body)
    path = f"repos/{OWNER}/{repo}/contents/{WORKFLOW_RELATIVE_PATH}"

    process = subprocess.run(
        ["gh", "api", "--method", "PUT", path, "--input", "-"],
        input=payload,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if process.returncode == 0:
        print(f"  [SUCCESS] Deployed to {repo} ({branch})")
        return True
    else:
        print(f"  [FAILED] {repo}: {process.stderr.strip() or process.stdout.strip()}")
        return False


def list_candidate_repos():
    repos = run_gh_json(["repo", "list", OWNER, "--limit", "100", "--source", "--no-archived", "--json", "name,defaultBranchRef"])
    if not repos:
        return []
    candidates = []
    for r in repos:
        name = r["name"]
        if name in (OWNER, "Hello-World"):
            continue
        branch = r.get("defaultBranchRef", {}).get("name", "main") if r.get("defaultBranchRef") else "main"
        candidates.append({"name": name, "branch": branch})
    return candidates


def main():
    parser = argparse.ArgumentParser(description="Deploy PR acknowledgement workflow to GitHub repositories.")
    parser.add_argument("--repo", help="Target a specific repository name (e.g. My-New-Repo)")
    parser.add_argument("--branch", default="main", help="Target branch name (default: main)")
    parser.add_argument("--all", action="store_true", help="Sync across all non-fork active repositories")
    args = parser.parse_args()

    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    b64_content = get_workflow_base64(root_dir)

    if args.repo:
        print(f"--> Deploying PR acknowledgement workflow to {args.repo} ({args.branch})...")
        deploy_to_repo(args.repo, args.branch, b64_content)
    elif args.all:
        candidates = list_candidate_repos()
        print(f"--> Found {len(candidates)} non-fork repositories. Deploying...")
        success = sum(1 for c in candidates if deploy_to_repo(c["name"], c["branch"], b64_content))
        print(f"\nDone: {success}/{len(candidates)} succeeded.")
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
