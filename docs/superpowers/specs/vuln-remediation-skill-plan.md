# Vulnerability Remediation Skill — Build Plan

Date: 2026-03-14
Status: Draft v2
Predecessor: vuln-remediation-service-plan.md
Stack: Python 3.12+, uv, Pydantic, Jinja2, httpx

## What Changed and Why

The original plan described a long-running service (Temporal + PostgreSQL + Fastify + Docker workers). This document re-targets the same domain logic as a PAI skill — an AI agent capability that any human can invoke from their own Claude Code agent session.

v2 re-platforms from TypeScript/Bun to modern Python, using uv for dependency management, Pydantic for data models and validation, httpx for async HTTP, Jinja2 for templating, and Click for CLI entry points.

### What the skill IS

A human-directed, single-repo vulnerability remediation assistant. A security engineer points the agent at a repo and a set of findings. The agent selects the safest fix, validates it, and opens a PR with evidence.

### What the skill IS NOT

- A portfolio-wide automation engine (that's a future service that could orchestrate skill invocations)
- A scanner (still delegates to Snyk/Wiz)
- An auto-merge bot
- A replacement for human judgment on what to fix

### Why this shape

First principles analysis shows 5 of the original 14 service components are irreducible (fetch findings, triage, strategize, validate, ship PR). The other 9 existed because the service ran unattended at scale. An attended agent needs none of them. This eliminates PostgreSQL, Temporal, Fastify, queue workers, observability stack, priority queue, persistent dedup, artifact storage, and concurrency management.

### Why Python

- Richest ecosystem for security tooling (Snyk SDK, OSV client libraries, packaging/semver parsing)
- Pydantic gives typed, validated data models with JSON serialization for free — replaces ad-hoc TypeScript interfaces
- httpx provides async HTTP with connection pooling, retries, and timeouts out of the box
- uv makes dependency management fast and reproducible (lockfile, venv isolation, script execution)
- Click gives clean CLI composition with subcommands, help text, and argument validation
- Jinja2 is the standard for templating with inheritance and filters — replaces Handlebars
- Python 3.12+ provides modern features: `type` aliases, `match` statements, `tomllib`, `ExceptionGroup`

## Architecture: Service vs Skill

| Service Component | Skill Equivalent | Rationale |
|---|---|---|
| Scanner ingestion adapters | **Workflow: FetchFindings** | Agent calls scanner API via CLI or HTTP |
| Normalization/dedup store | **In-session normalization** | Agent normalizes in memory; dedup via GitHub PR search |
| Risk/policy engine | **Workflow: TriageFindings** | Policy from `.vuln-remediation.yml`, applied by agent |
| Fix strategy engine | **Workflow: SelectStrategy** | Decision tree preserved as workflow instructions |
| Execution orchestrator (Temporal) | **Agent session** | Agent IS the orchestrator |
| Docker workers | **Workflow: ValidateFix** | Agent runs build/test via Bash (Docker optional but recommended) |
| Breaking change analyzer | **Workflow step in SelectStrategy** | Agent fetches changelogs, diffs APIs, assesses risk |
| Candidate version safety | **Workflow step in SelectStrategy** | Agent queries OSV/GHSA before selecting version |
| PR composer | **Workflow: ShipPR** | Agent generates PR via `gh` CLI |
| Consumer impact discoverer | **Workflow step in ShipPR** | Agent reads repo config for consumer metadata |
| Priority queue | **Eliminated** | Human selects what to remediate |
| PostgreSQL database | **Eliminated** | Session memory + git + PR history |
| Temporal workflow engine | **Eliminated** | Agent session handles orchestration |
| Observability stack | **Eliminated** | Agent output is the observability |
| Config management | **`.vuln-remediation.yml` + skill customizations** | Preserved, simplified |

## Skill Directory Structure

```
~/.claude/skills/VulnRemediation/
├── SKILL.md                              # Routing, triggers, voice notification
├── Workflows/
│   ├── Remediate.md                      # Full workflow: fetch → triage → fix → validate → PR
│   ├── FetchFindings.md                  # Standalone: pull findings from scanner
│   ├── TriageFindings.md                 # Standalone: apply policy, rank by risk
│   ├── SelectStrategy.md                # Standalone: choose fix approach for a finding
│   ├── ValidateFix.md                   # Standalone: apply fix, build, test, re-scan
│   └── ShipPR.md                        # Standalone: generate PR with evidence
├── src/
│   └── vuln_remediation/
│       ├── __init__.py
│       ├── cli.py                        # Click CLI entry point with subcommands
│       ├── models.py                     # Pydantic models: Finding, Strategy, Evidence, etc.
│       ├── config.py                     # Config loading (.vuln-remediation.yml + defaults)
│       ├── scanners/
│       │   ├── __init__.py
│       │   ├── base.py                   # ScannerAdapter protocol
│       │   ├── snyk.py                   # Snyk Issues API adapter
│       │   └── generic.py                # Generic normalized-report adapter
│       ├── safety/
│       │   ├── __init__.py
│       │   ├── osv.py                    # OSV API client
│       │   ├── ghsa.py                   # GitHub Advisory Database client
│       │   └── changelog.py              # Release notes fetcher (npm, Maven, GitHub)
│       ├── strategy/
│       │   ├── __init__.py
│       │   ├── engine.py                 # Strategy selection logic
│       │   └── breaking_changes.py       # Breaking change analysis
│       ├── github.py                     # GitHub PR/branch operations via gh CLI
│       └── templates/
│           ├── pr_body.jinja2            # PR body template with evidence sections
│           ├── reviewer_checklist.jinja2  # Reviewer checklist
│           └── decision_log.jinja2       # Session decision log for audit trail
├── data/
│   ├── strategy_decision_tree.yaml       # 4-strategy decision tree
│   ├── ecosystem_support.yaml            # Supported ecosystems and toolchains
│   └── curated_replacements.yaml         # Known safe package replacements
├── tests/
│   ├── __init__.py
│   ├── test_models.py                    # Pydantic model validation tests
│   ├── test_scanners.py                  # Scanner adapter tests with fixtures
│   ├── test_safety.py                    # OSV/GHSA query tests
│   ├── test_strategy.py                  # Strategy engine decision tests
│   └── fixtures/                         # Sample scanner responses, findings
│       ├── snyk_response.json
│       ├── osv_response.json
│       └── npm_changelog.json
├── pyproject.toml                        # Project metadata, dependencies, tool config
└── uv.lock                              # Pinned dependency lockfile
```

## Python Stack Details

### pyproject.toml

```toml
[project]
name = "vuln-remediation"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "click>=8.1",
    "httpx>=0.27",
    "pydantic>=2.9",
    "pyyaml>=6.0",
    "jinja2>=3.1",
    "packaging>=24.0",     # semver parsing and version comparison
    "rich>=13.0",          # terminal output formatting
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0",
    "pytest-asyncio>=0.24",
    "respx>=0.22",         # httpx mock/fixtures
    "ruff>=0.8",
]

[project.scripts]
vuln-remediation = "vuln_remediation.cli:main"

[tool.ruff]
target-version = "py312"
line-length = 100

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Execution model

Agent invokes tools via:
```bash
uv run vuln-remediation <subcommand> [args]
```

uv handles venv creation, dependency resolution, and script execution automatically. No manual `pip install` or `venv activate` needed.

## SKILL.md Definition

```yaml
---
name: VulnRemediation
description: >-
  Vulnerability remediation for dependencies — fetch scanner findings,
  select fix strategy, validate in sandbox, open PR with evidence.
  USE WHEN vuln remediation, fix vulnerability, remediate CVE,
  dependency update, security fix, snyk fix, wiz remediation,
  patch vulnerability, upgrade dependency.
---
```

### Workflow Routing Table

| Trigger | Workflow | Description |
|---|---|---|
| "remediate", "fix vuln", "fix CVE" (DEFAULT) | `Workflows/Remediate.md` | Full end-to-end remediation |
| "fetch findings", "scan", "what's vulnerable" | `Workflows/FetchFindings.md` | Pull and display findings only |
| "triage", "prioritize", "which vulns matter" | `Workflows/TriageFindings.md` | Apply policy, rank findings |
| "what strategy", "how to fix", "analyze fix" | `Workflows/SelectStrategy.md` | Strategy selection for specific finding |
| "validate fix", "test fix", "verify update" | `Workflows/ValidateFix.md` | Build/test a proposed fix |
| "open PR", "ship fix", "create PR" | `Workflows/ShipPR.md` | Generate PR from validated fix |

## Data Models (models.py)

```python
from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from pydantic import BaseModel, Field


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DependencyType(StrEnum):
    DIRECT = "direct"
    TRANSITIVE = "transitive"
    BASE_IMAGE = "base_image"


class Ecosystem(StrEnum):
    NPM = "npm"
    MAVEN = "maven"
    DOCKER = "docker"
    PNPM = "pnpm"
    YARN = "yarn"
    GRADLE = "gradle"


class StrategyType(StrEnum):
    UPDATE = "update"
    PATCH = "patch"
    REPLACE = "replace"
    MITIGATE = "mitigate"


class RemediationStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PR_OPENED = "pr_opened"
    REPORT_ONLY = "report_only"
    SKIPPED = "skipped"
    FAILED = "failed"


class Finding(BaseModel):
    """Normalized vulnerability finding from any scanner."""
    finding_id: str
    source_system: str
    repository: str
    branch: str
    manifest_path: str
    ecosystem: Ecosystem
    package_name: str
    purl: str
    current_version: str
    candidate_fixed_versions: list[str] = Field(default_factory=list)
    dependency_type: DependencyType
    dependency_path: list[str] = Field(default_factory=list)
    severity: Severity
    cvss: float | None = None
    epss: float | None = None
    exploit_maturity: str | None = None
    reachable: bool | None = None
    runtime_exposure: str | None = None
    advisory_ids: list[str] = Field(default_factory=list)
    scanner_evidence_urls: list[str] = Field(default_factory=list)
    introduced_via: str | None = None
    fix_types_available: list[StrategyType] = Field(default_factory=list)


class CandidateCheck(BaseModel):
    """Result of checking a candidate version against advisory databases."""
    version: str
    safe: bool
    advisories: list[str] = Field(default_factory=list)
    severity_introduced: Severity | None = None


class BreakingChangeSignal(BaseModel):
    """Structured breaking change evidence."""
    semver_delta: str  # major | minor | patch
    changelog_url: str | None = None
    breaking_changes: list[str] = Field(default_factory=list)
    deprecations: list[str] = Field(default_factory=list)
    api_changes: list[str] = Field(default_factory=list)


class StrategyRecommendation(BaseModel):
    """Output of the strategy engine."""
    finding: Finding
    recommended_strategy: StrategyType
    target_version: str | None = None
    confidence: float
    rationale: str
    breaking_change_signals: BreakingChangeSignal | None = None
    candidate_checks: list[CandidateCheck] = Field(default_factory=list)
    alternatives_considered: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Output of the validate step."""
    success: bool
    test_passed: bool
    build_passed: bool
    rescan_clean: bool
    confidence: float
    test_output_summary: str
    scan_output_summary: str
    lockfile_diff_summary: str
    execution_mode: str  # direct | docker | docker-restricted


class DedupCheckResult(BaseModel):
    """Result of checking for existing remediation work."""
    existing_pr: dict | None = None  # {url, status, branch}
    existing_branch: str | None = None


class RemediationRecord(BaseModel):
    """Full remediation lifecycle record — written to decision log."""
    finding: Finding
    strategy: StrategyRecommendation
    validation: ValidationResult | None = None
    pr_url: str | None = None
    status: RemediationStatus = RemediationStatus.PENDING
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None
    decision_rationale: str = ""
    downstream_consumers: list[str] = Field(default_factory=list)
```

## Scanner Adapters (scanners/)

### base.py — Protocol

```python
from typing import Protocol

from vuln_remediation.models import Finding


class ScannerAdapter(Protocol):
    """All scanner adapters implement this interface."""

    async def fetch_findings(
        self,
        *,
        severity: list[str] | None = None,
        ecosystem: str | None = None,
    ) -> list[Finding]: ...
```

### snyk.py — Snyk adapter

```python
import httpx
from vuln_remediation.models import Finding, Severity, DependencyType, Ecosystem


class SnykAdapter:
    """Fetch and normalize findings from Snyk Issues API."""

    BASE_URL = "https://api.snyk.io/rest"

    def __init__(self, token: str, org_id: str, project_id: str) -> None:
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={"Authorization": f"token {token}"},
            timeout=30.0,
        )
        self.org_id = org_id
        self.project_id = project_id

    async def fetch_findings(
        self,
        *,
        severity: list[str] | None = None,
        ecosystem: str | None = None,
    ) -> list[Finding]:
        # Fetch from Snyk Issues API, normalize to Finding model
        ...
```

### generic.py — Normalized report import

Accepts a JSON file matching the `Finding` schema directly, or a CSV/SARIF export that gets mapped. Covers Wiz exported reports and any scanner that can produce normalized output.

## Safety Checks (safety/)

### osv.py

```python
import httpx
from vuln_remediation.models import CandidateCheck


class OSVClient:
    """Query OSV.dev for known vulnerabilities in a package version."""

    BASE_URL = "https://api.osv.dev/v1"

    async def check_version(self, purl: str, version: str) -> CandidateCheck:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{self.BASE_URL}/query",
                json={"package": {"purl": purl}, "version": version},
            )
            resp.raise_for_status()
            data = resp.json()
            advisories = [v["id"] for v in data.get("vulns", [])]
            return CandidateCheck(
                version=version,
                safe=len(advisories) == 0,
                advisories=advisories,
            )
```

### ghsa.py

Queries GitHub Advisory Database via GraphQL API. Same interface as OSV — returns `CandidateCheck` with overlapping advisory IDs.

### changelog.py

```python
import httpx
from packaging.version import Version
from vuln_remediation.models import BreakingChangeSignal


class ChangelogFetcher:
    """Fetch release notes and extract breaking change signals."""

    async def fetch(
        self,
        package_name: str,
        from_version: str,
        to_version: str,
        ecosystem: str = "npm",
    ) -> BreakingChangeSignal:
        match ecosystem:
            case "npm":
                return await self._fetch_npm(package_name, from_version, to_version)
            case "maven":
                return await self._fetch_maven(package_name, from_version, to_version)
            case _:
                return await self._fetch_github_releases(package_name, from_version, to_version)

    async def _fetch_npm(self, pkg: str, from_v: str, to_v: str) -> BreakingChangeSignal:
        """Fetch from npm registry metadata + GitHub releases."""
        from_ver, to_ver = Version(from_v), Version(to_v)
        delta = "major" if to_ver.major > from_ver.major else (
            "minor" if to_ver.minor > from_ver.minor else "patch"
        )
        # Fetch changelog from registry, extract breaking changes
        ...
```

## CLI Entry Point (cli.py)

```python
import asyncio
import json
import sys

import click
from rich.console import Console
from rich.table import Table

from vuln_remediation.config import load_config
from vuln_remediation.models import Finding

console = Console()


@click.group()
@click.version_option()
def main() -> None:
    """Vulnerability remediation skill CLI."""


@main.command()
@click.argument("org_id")
@click.argument("project_id")
@click.option("--severity", "-s", default="high,critical", help="Comma-separated severity filter")
@click.option("--ecosystem", "-e", default=None, help="Filter by ecosystem")
@click.option("--output", "-o", type=click.Choice(["json", "table"]), default="table")
def fetch(org_id: str, project_id: str, severity: str, ecosystem: str | None, output: str) -> None:
    """Fetch findings from Snyk."""
    findings = asyncio.run(_fetch(org_id, project_id, severity.split(","), ecosystem))
    if output == "json":
        click.echo(json.dumps([f.model_dump(mode="json") for f in findings], indent=2))
    else:
        _render_table(findings)


@main.command()
@click.argument("purl")
@click.argument("version")
def osv_check(purl: str, version: str) -> None:
    """Check a candidate version against OSV and GHSA."""
    from vuln_remediation.safety.osv import OSVClient

    result = asyncio.run(OSVClient().check_version(purl, version))
    click.echo(result.model_dump_json(indent=2))


@main.command()
@click.argument("package_name")
@click.argument("from_version")
@click.argument("to_version")
@click.option("--ecosystem", "-e", default="npm")
def changelog(package_name: str, from_version: str, to_version: str, ecosystem: str) -> None:
    """Fetch changelog and breaking change signals between versions."""
    from vuln_remediation.safety.changelog import ChangelogFetcher

    result = asyncio.run(ChangelogFetcher().fetch(package_name, from_version, to_version, ecosystem))
    click.echo(result.model_dump_json(indent=2))


@main.command()
@click.argument("repo")
@click.argument("advisory_id")
def dedup_check(repo: str, advisory_id: str) -> None:
    """Search for existing remediation PRs/branches."""
    from vuln_remediation.github import check_existing_remediation

    result = asyncio.run(check_existing_remediation(repo, advisory_id))
    click.echo(result.model_dump_json(indent=2))


def _render_table(findings: list[Finding]) -> None:
    table = Table(title="Vulnerability Findings")
    table.add_column("Severity", style="bold")
    table.add_column("Package")
    table.add_column("Version")
    table.add_column("Advisory")
    table.add_column("Fix Available")
    for f in findings:
        style = {"critical": "red bold", "high": "red", "medium": "yellow", "low": "dim"}.get(
            f.severity, ""
        )
        table.add_row(
            f.severity.upper(),
            f.package_name,
            f.current_version,
            ", ".join(f.advisory_ids[:2]),
            "Yes" if f.candidate_fixed_versions else "No",
            style=style,
        )
    console.print(table)
```

## GitHub Operations (github.py)

```python
import asyncio
import json
import subprocess

from vuln_remediation.models import DedupCheckResult


async def check_existing_remediation(repo: str, advisory_id: str) -> DedupCheckResult:
    """Search for existing PRs/branches matching the remediation naming convention."""
    branch_prefix = f"vuln-remediation/{advisory_id}"

    # Check for existing PRs
    pr_result = subprocess.run(
        ["gh", "pr", "list", "--repo", repo, "--head", branch_prefix, "--json", "url,state,headRefName"],
        capture_output=True, text=True, timeout=15,
    )
    prs = json.loads(pr_result.stdout) if pr_result.returncode == 0 else []

    # Check for existing branches
    branch_result = subprocess.run(
        ["gh", "api", f"repos/{repo}/branches", "--jq", f'.[].name | select(startswith("{branch_prefix}"))'],
        capture_output=True, text=True, timeout=15,
    )
    existing_branch = branch_result.stdout.strip() or None

    return DedupCheckResult(
        existing_pr=prs[0] if prs else None,
        existing_branch=existing_branch,
    )
```

## Jinja2 Templates (templates/)

### pr_body.jinja2

```jinja2
## Vulnerability Remediation

### Triggering Findings
{% for finding in findings %}
- **{{ finding.package_name }}@{{ finding.current_version }}** — {{ finding.severity | upper }}
  - Advisory: {{ finding.advisory_ids | join(", ") }}
  - Type: {{ finding.dependency_type }}
  - Path: `{{ finding.manifest_path }}`
{% endfor %}

### Chosen Strategy: {{ strategy.recommended_strategy | upper }}

**Target version:** {{ strategy.target_version }}
**Confidence:** {{ "%.0f" | format(strategy.confidence * 100) }}%

{{ strategy.rationale }}

### Alternatives Considered
{% for alt in strategy.alternatives_considered %}
- {{ alt }}
{% endfor %}

{% if strategy.breaking_change_signals %}
### Breaking Change Analysis

- **Semver delta:** {{ strategy.breaking_change_signals.semver_delta }}
{% for change in strategy.breaking_change_signals.breaking_changes %}
- ⚠️ {{ change }}
{% endfor %}
{% for dep in strategy.breaking_change_signals.deprecations %}
- 📋 Deprecated: {{ dep }}
{% endfor %}
{% endif %}

### Candidate Version Safety
{% for check in strategy.candidate_checks %}
- **{{ check.version }}**: {{ "✅ Safe" if check.safe else "❌ " + (check.advisories | join(", ")) }}
{% endfor %}

{% if validation %}
### Validation Evidence

| Check | Result |
|---|---|
| Build | {{ "✅ Passed" if validation.build_passed else "❌ Failed" }} |
| Tests | {{ "✅ Passed" if validation.test_passed else "❌ Failed" }} |
| Re-scan | {{ "✅ Clean" if validation.rescan_clean else "❌ New findings" }} |
| Execution mode | {{ validation.execution_mode }} |
| Confidence | {{ "%.0f" | format(validation.confidence * 100) }}% |

<details>
<summary>Test output</summary>

```
{{ validation.test_output_summary }}
```
</details>

<details>
<summary>Lockfile diff</summary>

```
{{ validation.lockfile_diff_summary }}
```
</details>
{% endif %}

{% if consumers %}
### Downstream Consumer Impact
{% for consumer in consumers %}
- **{{ consumer }}**
{% endfor %}
{% endif %}

### Rollback

```bash
git revert {{ commit_sha }}
```

Or manually revert `{{ strategy.finding.package_name }}` to `{{ strategy.finding.current_version }}`.
```

### reviewer_checklist.jinja2

```jinja2
### Reviewer Checklist

- [ ] Chosen strategy is the lowest-risk viable option
- [ ] Target version is not known-vulnerable in the attached evidence
- [ ] Changelog and compatibility notes reviewed
- [ ] Existing tests passed in the runner
{% if has_generated_tests %}- [ ] Generated tests are relevant and non-trivial{% endif %}
- [ ] Downstream consumer impact acknowledged
- [ ] Rollback instructions are sufficient
{% if is_major_update %}- [ ] Major-version change has explicit owner approval{% endif %}
```

## Workflow Details

### Remediate.md (Primary Workflow)

The full pipeline, invoked when a human says "remediate vulnerabilities in this repo."

**Steps:**

1. **Pre-flight checks**
   - Verify scanner CLI or API token is available (`SNYK_TOKEN` env var)
   - Verify GitHub CLI authenticated (`gh auth status`)
   - Verify repo is a git repo with clean working tree
   - Verify Python toolchain: `uv run vuln-remediation --version`
   - Read `.vuln-remediation.yml` if present, else use defaults
   - Run `uv run vuln-remediation dedup-check <repo> <advisory>` — search for existing remediation PRs/branches

2. **Fetch findings**
   - Run `uv run vuln-remediation fetch <org-id> <project-id> --output json`
   - Normalize findings into uniform records (in agent memory)
   - Display summary: total findings, by severity, by ecosystem

3. **Triage**
   - Apply policy from config (severity threshold, reachability, exposure)
   - Present ranked findings to human
   - Human selects which finding(s) to remediate (or accepts agent recommendation)

4. **Strategy selection** (per selected finding)
   - Load `strategy_decision_tree.yaml`
   - For each candidate version:
     - Run `uv run vuln-remediation osv-check <purl> <version>` to verify no new advisories
     - Run `uv run vuln-remediation changelog <pkg> <from> <to>` to assess breaking change risk
     - Score compatibility: semver delta, changelog signals, repo call-site analysis
   - Select lowest-risk viable strategy
   - Present recommendation to human with rationale
   - Human approves or overrides

5. **Validate**
   - Create feature branch: `vuln-remediation/{advisory-id}`
   - Apply the fix (version update, lockfile regeneration, etc.)
   - Run build and test suite
   - Re-scan with scanner CLI
   - Collect evidence: test output, scan results, diff
   - Compute confidence score
   - If confidence < threshold, present as report instead of PR

6. **Ship PR**
   - Render `pr_body.jinja2` with evidence
   - Render `reviewer_checklist.jinja2`
   - Open PR via `gh pr create`
   - Render `decision_log.jinja2` output to `.vuln-remediation/logs/{date}-{advisory}.md` in repo
   - Commit decision log to the PR branch

7. **Post-flight**
   - Display PR URL
   - Summarize what was done, what was skipped, and why

### FetchFindings.md (Standalone)

Fetch-only mode for reconnaissance. Agent pulls findings and presents them without taking action. Useful for a human to survey the landscape before deciding what to remediate.

**Input:** Repo path + scanner source (snyk, wiz, or generic report file)
**Output:** Rich terminal table of findings with severity, ecosystem, package, current version, fix available (y/n)

### TriageFindings.md (Standalone)

Apply policy to a set of findings and rank them. Can operate on output from FetchFindings or on a previously saved findings file.

**Input:** Findings (from fetch or file) + policy config
**Output:** Prioritized list with reasoning for each inclusion/exclusion

### SelectStrategy.md (Standalone)

Deep-dive on a single finding. Agent analyzes all remediation options, checks candidate versions, assesses breaking changes, and recommends a strategy.

**Input:** Single finding record (package, version, advisory)
**Output:** Strategy recommendation with evidence, alternatives considered, confidence score

### ValidateFix.md (Standalone)

Apply a proposed fix and run validation. Agent creates a branch, applies the change, runs build/test/re-scan.

**Input:** Repo + proposed fix (package, target version, strategy)
**Output:** Validation report (pass/fail, test output, scan results, confidence score)

### ShipPR.md (Standalone)

Generate and open a PR from a validated fix. Agent renders PR template with evidence, opens PR, writes decision log.

**Input:** Validated fix artifacts + repo
**Output:** PR URL + decision log committed

## Multi-Human Consumption Model

### What's shared (in the repo)

- `.vuln-remediation.yml` — repo-level policy config (risk thresholds, allowed strategies, consumers, notification channels)
- `.vuln-remediation/logs/` — decision logs from past remediations (committed to repo)
- PR naming convention: `vuln-remediation/{advisory-id}` — enables dedup-check across humans
- Branch naming convention: same prefix — enables branch search

### What's per-user (in their environment)

- `~/.claude/skills/VulnRemediation/` — the skill definition (same for all users)
- `~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/VulnRemediation/PREFERENCES.md` — personal overrides (e.g., preferred scanner, default severity threshold, Docker usage preference)
- Scanner API tokens — in user's environment variables (`SNYK_TOKEN`, `WIZ_TOKEN`)
- GitHub auth — in user's `gh` CLI config
- Python 3.12+ and uv — installed on user's machine

### Coordination protocol

1. **Before starting:** Agent runs `uv run vuln-remediation dedup-check` to find existing PRs/branches for the target advisory
2. **If existing PR found:** Agent reports it and asks human whether to proceed anyway, update the existing PR, or skip
3. **Branch naming convention enforced:** All branches use `vuln-remediation/{advisory-id}` so other humans' agents can discover them
4. **Decision logs committed to repo:** Each remediation writes a log file to `.vuln-remediation/logs/`, creating a persistent audit trail visible to all humans

### No runtime coordination needed

Each agent session is independent. Git and GitHub are the coordination layer. No shared database, no message queue, no locking protocol.

## Execution Isolation Options

The skill supports three execution modes for the validate step, configured in `.vuln-remediation.yml` or user preferences:

### Mode 1: Direct (fastest, least isolated)

Agent runs `npm install`, `npm test`, etc. directly in the repo working directory on a feature branch. Suitable for trusted, internal packages only.

### Mode 2: Docker container (recommended default)

Agent runs validation inside a container:
```bash
docker run --rm \
  -v $(pwd):/workspace:rw \
  -w /workspace \
  --network=host \
  node:20-slim \
  sh -c "npm ci && npm test"
```

Provides process isolation without requiring a full container orchestration system.

### Mode 3: Docker rootless + network-restricted (most isolated)

For untrusted or public-facing repos:
```bash
docker run --rm \
  --security-opt no-new-privileges \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid \
  -v $(pwd):/workspace:rw \
  -w /workspace \
  --network=none \
  node:20-slim \
  sh -c "npm ci --prefer-offline && npm test"
```

Requires pre-cached dependencies or a registry proxy.

## Preserved Domain Logic

The following elements from the original service plan are preserved exactly in the skill's workflow instructions and data files:

### Fix Strategy Decision Tree (strategy_decision_tree.yaml)

1. **Update** — lowest safe direct version first, escalate only if lowest fails
2. **Patch** — authoritative patch only, when update path is breaking/unavailable
3. **Replace** — advisory-only unless curated replacement exists
4. **Mitigate** — config/code change + follow-up ticket for permanent fix

### Confidence Scoring

- `>=0.80` for patch/minor updates → open PR
- `>=0.90` for major updates → open PR
- Below threshold → generate report, not PR

### Breaking Change Analysis Signals

- Semver delta
- Changelog/release notes
- Registry deprecation notices
- API diff tooling (where available)
- Call-site analysis in the repo
- LLM summarization (explanation layer, not decision layer)

### Candidate Version Safety

- Query OSV + GHSA for each candidate
- Reject if new critical or new high in same scope
- Reject if total unresolved > baseline
- Re-scan post-change lockfile

### Transitive Dependency Resolution

- Attempt native override/resolution mechanisms
- Diff full lockfile for unrelated churn
- Reject if graph can't be deterministically resolved
- Never PR from unresolved dependency graph

### PR Content

- Triggering findings and advisory IDs
- Chosen strategy + rejected alternatives with reasoning
- Version delta (current → target)
- Breaking change summary
- New-vulnerability check result
- Test evidence summary
- Downstream consumer impact
- Reviewer checklist
- Rollback instructions

### Reviewer Checklist

- Lowest-risk viable strategy confirmed
- Target version not known-vulnerable in evidence
- Changelog reviewed
- Tests passed in runner
- Generated tests are relevant
- Downstream impact acknowledged
- Rollback instructions sufficient
- Major-version change has owner approval

## What Was Eliminated and Why

| Eliminated Component | Why |
|---|---|
| PostgreSQL | Session memory + git history + decision logs replace persistent store |
| Temporal | Agent session IS the workflow engine; no checkpoint/resume needed for single-repo work |
| Fastify/NestJS API | No API needed; skill is invoked directly |
| Priority queue | Human selects what to fix; agent doesn't need to optimize ordering |
| Concurrency limits | One agent, one session, one repo at a time |
| Persistent dedup store | `dedup-check` subcommand searches GitHub for existing PRs/branches |
| Artifact storage (S3) | Evidence embedded in PR body + decision log committed to repo |
| Observability stack | Agent output is visible to human in real-time |
| Runner image management | User's local toolchain or standard Docker images |
| Secret rotation | User manages their own credentials |

## What Was Explicitly Deferred

| Deferred Capability | Why | Future Path |
|---|---|---|
| Portfolio-wide automation | Skill handles 1-10 findings per session | Future orchestrator service invokes skill across repos |
| Cross-repo candidate ledger | No persistent state across sessions | Could be a shared YAML in a central repo |
| Environment consistency guarantees | Users have different toolchains | Could publish recommended Docker images |
| Automated scheduling | No cron/trigger mechanism | Could wrap skill invocation in a CI pipeline |
| Multi-scanner correlation | Session handles one scanner at a time | Could add a correlation workflow later |

## Suggested Repository Config (Preserved)

```yaml
# .vuln-remediation.yml
version: 1
riskThreshold:
  minSeverity: high
  allowReachableMedium: true
supportedEcosystems:
  - npm
  - maven
  - docker
strategies:
  allow:
    - update
    - patch
    - mitigate
  replacementMode: advisory
executionMode: docker  # direct | docker | docker-restricted
consumers:
  - name: billing-api
    type: service
    contractTests: services/billing-api/contracts
notifications:
  slackChannel: "#security-remediation"
  jiraProject: SEC
confidence:
  defaultMin: 0.8
  majorMin: 0.9
```

## Build Plan

### Phase 1: Project Bootstrap + Fetch (Week 1-2)

**Deliverables:**
- `pyproject.toml` with dependencies, ruff/pytest config
- `uv.lock` pinned lockfile
- `models.py` — all Pydantic models with validation
- `config.py` — YAML config loader with defaults
- `scanners/snyk.py` — Snyk Issues API adapter
- `scanners/generic.py` — normalized report import
- `cli.py` — Click entry point with `fetch` subcommand
- `test_models.py` — model validation tests
- `test_scanners.py` — scanner adapter tests with fixtures
- SKILL.md with routing table
- `FetchFindings.md` workflow
- `TriageFindings.md` workflow
- `ecosystem_support.yaml` with npm + Maven support

**Independently testable:** Human can invoke `VulnRemediation fetch findings` on any repo and see normalized output via Rich table. `uv run vuln-remediation fetch <org> <project>` works standalone.

### Phase 2: Strategy + Safety (Week 3-4)

**Deliverables:**
- `safety/osv.py` — OSV API client
- `safety/ghsa.py` — GitHub Advisory Database client
- `safety/changelog.py` — release notes fetcher with npm + Maven + GitHub releases
- `strategy/engine.py` — strategy selection logic implementing decision tree
- `strategy/breaking_changes.py` — breaking change analysis
- `cli.py` — add `osv-check`, `changelog`, `dedup-check` subcommands
- `github.py` — PR/branch search operations
- `test_safety.py` — OSV/GHSA query tests with respx mocks
- `test_strategy.py` — strategy engine decision tests
- `strategy_decision_tree.yaml`
- `SelectStrategy.md` workflow

**Independently testable:** Human can invoke `VulnRemediation analyze fix` for a specific finding and get a strategy recommendation with evidence. `uv run vuln-remediation osv-check <purl> <version>` works standalone.

### Phase 3: Validate + Ship (Week 5-6)

**Deliverables:**
- `ValidateFix.md` workflow — branch, apply fix, build, test, re-scan
- `ShipPR.md` workflow — render PR, open via gh CLI, write decision log
- `templates/pr_body.jinja2`
- `templates/reviewer_checklist.jinja2`
- `templates/decision_log.jinja2`
- Three execution modes (direct, docker, docker-restricted)
- Template rendering integration in CLI

**Independently testable:** Human can invoke `VulnRemediation validate fix` and `VulnRemediation ship PR` as standalone steps.

### Phase 4: Full Pipeline + Multi-Human (Week 7-8)

**Deliverables:**
- `Remediate.md` workflow — full end-to-end pipeline connecting all steps
- Multi-human coordination: dedup-check integration, branch naming enforcement, decision log commits
- `curated_replacements.yaml` — initial set of known safe replacements
- User customization support at `~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/VulnRemediation/`

**Independently testable:** Human can invoke `VulnRemediation remediate` and go from findings to PR in one session. Second human can invoke on same repo without collision.

### Phase 5: Ecosystem Expansion (Week 9+)

**Deliverables:**
- Docker base image remediation support
- Generic scanner adapter (for Wiz and others)
- Additional ecosystem support (pnpm, yarn, Gradle)
- Monorepo awareness (detect packages, group by bounded context)

## Open Questions (Carried Forward)

- Which source of truth owns "external consumers": Backstage, repo config, or both?
- Is Wiz API access available, or is normalized import (exported report) the initial path?
- Should the skill support a "report-only" mode that writes findings + recommendations to a file without opening PRs?
- Is there a preferred Docker base image registry for validation containers?
- Should decision logs be committed to the target repo or to a central security-audit repo?
