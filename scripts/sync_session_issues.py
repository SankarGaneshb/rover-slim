#!/usr/bin/env python3
"""
Rover-Slim Session Issues Synchronizer
Parses structured issue blueprints from docs/roadmap/ and creates them on GitHub.
Supports both the GitHub CLI (gh) and the GitHub REST API (via GITHUB_TOKEN).
"""

import argparse
import json
import os
import re
import subprocess
import sys
import urllib.request
import urllib.error

DEFAULT_SPEC_FILE = os.path.join(os.path.dirname(__file__), "..", "docs", "roadmap", "SILENTSTARS_ACTION_ISSUES.md")
REPO = "SankarGaneshb/rover-slim"


def parse_issues(file_path: str):
    """Parses issue markdown files with structured headers."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by ## ISSUE <num>
    sections = re.split(r"\n## ISSUE \d+\n", content)
    issues = []

    for sec in sections[1:]:  # skip preamble
        title_match = re.search(r"\* \*\*Title\*\*:\s*`([^`]+)`", sec)
        labels_match = re.search(r"\* \*\*Labels\*\*:\s*([^\n]+)", sec)
        body_match = re.search(r"\* \*\*Description\*\*:\s*\n```markdown\n(.*?)\n```", sec, re.DOTALL)

        if title_match and body_match:
            title = title_match.group(1).strip()
            labels_raw = labels_match.group(1).strip() if labels_match else ""
            labels = [lbl.strip(" `\",") for lbl in labels_raw.split(",") if lbl.strip(" `\",")]
            body = body_match.group(1).strip()

            issues.append({
                "title": title,
                "labels": labels,
                "body": body,
            })

    return issues


def check_gh_cli():
    """Checks if gh CLI is available and logged in."""
    try:
        res = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True)
        return res.returncode == 0
    except FileNotFoundError:
        return False


def create_issue_via_gh(issue: dict):
    """Creates a GitHub issue using `gh issue create`."""
    cmd = ["gh", "issue", "create", "--repo", REPO, "--title", issue["title"], "--body", issue["body"]]
    for label in issue["labels"]:
        cmd.extend(["--label", label])

    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode == 0:
        print(f"  [OK] Created: {res.stdout.strip()}")
        return True
    else:
        print(f"  [ERR] Failed via gh: {res.stderr.strip()}")
        return False


def create_issue_via_api(issue: dict, token: str):
    """Creates a GitHub issue using the GitHub REST API."""
    url = f"https://api.github.com/repos/{REPO}/issues"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "Rover-Slim-Sync-Bot",
        "Content-Type": "application/json",
    }
    payload = {
        "title": issue["title"],
        "body": issue["body"],
        "labels": issue["labels"],
    }

    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"  [OK] Created: {data.get('html_url')}")
            return True
    except urllib.error.HTTPError as e:
        err_msg = e.read().decode("utf-8")
        print(f"  [ERR] API Error {e.code}: {err_msg}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Sync concluded roadmap issues to GitHub.")
    parser.add_argument("--spec", default=DEFAULT_SPEC_FILE, help="Path to markdown issue backlog spec")
    parser.add_argument("--dry-run", action="store_true", help="Parse and validate issues without creating them")
    parser.add_argument("--token", default=os.environ.get("GITHUB_TOKEN"), help="GitHub Personal Access Token")
    args = parser.parse_args()

    spec_path = os.path.abspath(args.spec)
    if not os.path.exists(spec_path):
        print(f"Error: Specification file not found at {spec_path}", file=sys.stderr)
        sys.exit(1)

    issues = parse_issues(spec_path)
    print(f"Parsed {len(issues)} structured issues from {os.path.basename(spec_path)}.\n")

    if args.dry_run:
        print("=== DRY RUN MODE ===")
        for i, issue in enumerate(issues, start=1):
            print(f"Issue {i}: {issue['title']}")
            print(f"  Labels: {', '.join(issue['labels'])}")
            print(f"  Body length: {len(issue['body'])} chars\n")
        print("All issues validated successfully.")
        return

    # Check authentication methods
    token = args.token
    has_gh = check_gh_cli()

    if not has_gh and not token:
        print("Error: No valid GitHub authentication found.", file=sys.stderr)
        print("Please authenticate using either:", file=sys.stderr)
        print("  1. 'gh auth login' (GitHub CLI)", file=sys.stderr)
        print("  2. Setting the GITHUB_TOKEN environment variable or passing --token <token>", file=sys.stderr)
        sys.exit(1)

    print(f"Publishing {len(issues)} issues to {REPO}...")
    for i, issue in enumerate(issues, start=1):
        print(f"\nProcessing Issue {i}/{len(issues)}: {issue['title']}")
        if has_gh:
            create_issue_via_gh(issue)
        else:
            create_issue_via_api(issue, token)


if __name__ == "__main__":
    main()
