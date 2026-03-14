"""GitHub PR/branch operations via gh CLI for dedup-check and PR creation."""

from __future__ import annotations

import asyncio
import json
import subprocess

from vuln_remediation.models import DedupCheckResult


async def check_existing_remediation(repo: str, advisory_id: str) -> DedupCheckResult:
    """Search for existing PRs/branches matching the remediation naming convention.

    Uses ``gh`` CLI to query GitHub for PRs and branches whose names start with
    ``vuln-remediation/{advisory_id}``.  Returns a :class:`DedupCheckResult`
    indicating whether existing work already covers this advisory.

    Args:
        repo: GitHub repository in ``owner/repo`` format.
        advisory_id: Advisory identifier (e.g. ``GHSA-xxxx-yyyy-zzzz`` or ``CVE-2025-12345``).

    Returns:
        DedupCheckResult with existing_pr and/or existing_branch populated if found.
    """
    branch_prefix = f"vuln-remediation/{advisory_id}"

    # Search for existing PRs (open or merged) with matching head branch
    pr_result = await asyncio.to_thread(
        subprocess.run,
        [
            "gh", "pr", "list",
            "--repo", repo,
            "--head", branch_prefix,
            "--state", "all",
            "--json", "url,state,headRefName",
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    prs: list[dict] = []
    if pr_result.returncode == 0 and pr_result.stdout.strip():
        prs = json.loads(pr_result.stdout)

    # Search for existing branches matching the prefix
    branch_result = await asyncio.to_thread(
        subprocess.run,
        [
            "gh", "api",
            f"repos/{repo}/branches",
            "--jq",
            f'.[].name | select(startswith("{branch_prefix}"))',
        ],
        capture_output=True,
        text=True,
        timeout=15,
    )
    existing_branch = (
        branch_result.stdout.strip().split("\n")[0]
        if branch_result.returncode == 0 and branch_result.stdout.strip()
        else None
    )

    return DedupCheckResult(
        existing_pr=prs[0] if prs else None,
        existing_branch=existing_branch,
    )
