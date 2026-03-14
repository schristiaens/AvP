"""Click CLI entry point with all subcommands for vuln-remediation."""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path

import click
from jinja2 import Environment, FileSystemLoader
from rich.console import Console
from rich.table import Table

from vuln_remediation.config import load_config
from vuln_remediation.models import (
    Finding,
    RemediationRecord,
    StrategyRecommendation,
    ValidationResult,
)

console = Console()

TEMPLATE_DIR = Path(__file__).parent / "templates"
_jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=False,
    keep_trailing_newline=True,
)


@click.group()
@click.version_option(version="0.1.0")
def main() -> None:
    """Vulnerability remediation skill CLI."""


# ── Fetch ────────────────────────────────────────────────────────────────────


@main.command()
@click.argument("org_id")
@click.argument("project_id")
@click.option("--severity", "-s", default="high,critical", help="Comma-separated severity filter")
@click.option("--ecosystem", "-e", default=None, help="Filter by ecosystem")
@click.option("--output", "-o", type=click.Choice(["json", "table"]), default="table")
def fetch(
    org_id: str,
    project_id: str,
    severity: str,
    ecosystem: str | None,
    output: str,
) -> None:
    """Fetch findings from Snyk."""
    findings = asyncio.run(_fetch(org_id, project_id, severity.split(","), ecosystem))
    if output == "json":
        click.echo(json.dumps([f.model_dump(mode="json") for f in findings], indent=2))
    else:
        _render_table(findings)


async def _fetch(
    org_id: str,
    project_id: str,
    severity: list[str],
    ecosystem: str | None,
) -> list[Finding]:
    """Fetch findings via the Snyk adapter."""
    from vuln_remediation.scanners.snyk import SnykAdapter
    import os

    token = os.environ.get("SNYK_TOKEN", "")
    if not token:
        console.print("[red]Error:[/red] SNYK_TOKEN environment variable is not set.")
        sys.exit(1)

    adapter = SnykAdapter(token=token, org_id=org_id, project_id=project_id)
    return await adapter.fetch_findings(severity=severity, ecosystem=ecosystem)


# ── OSV Check ────────────────────────────────────────────────────────────────


@main.command("osv-check")
@click.argument("purl")
@click.argument("version")
def osv_check(purl: str, version: str) -> None:
    """Check a candidate version against OSV and GHSA."""
    from vuln_remediation.safety.osv import OSVClient

    result = asyncio.run(OSVClient().check_version(purl, version))
    click.echo(result.model_dump_json(indent=2))


# ── Changelog ────────────────────────────────────────────────────────────────


@main.command()
@click.argument("package_name")
@click.argument("from_version")
@click.argument("to_version")
@click.option("--ecosystem", "-e", default="npm")
def changelog(package_name: str, from_version: str, to_version: str, ecosystem: str) -> None:
    """Fetch changelog and breaking change signals between versions."""
    from vuln_remediation.safety.changelog import ChangelogFetcher

    result = asyncio.run(
        ChangelogFetcher().fetch(package_name, from_version, to_version, ecosystem)
    )
    click.echo(result.model_dump_json(indent=2))


# ── Dedup Check ──────────────────────────────────────────────────────────────


@main.command("dedup-check")
@click.argument("repo")
@click.argument("advisory_id")
def dedup_check(repo: str, advisory_id: str) -> None:
    """Search for existing remediation PRs/branches."""
    from vuln_remediation.github import check_existing_remediation

    result = asyncio.run(check_existing_remediation(repo, advisory_id))
    click.echo(result.model_dump_json(indent=2))


# ── Template Rendering ───────────────────────────────────────────────────────


@main.command("render-pr")
@click.argument("data_json", type=click.Path(exists=True))
def render_pr(data_json: str) -> None:
    """Render PR body from remediation data JSON file.

    DATA_JSON must contain: findings (list), strategy, validation (optional),
    consumers (optional list), commit_sha (optional).
    """
    data = json.loads(Path(data_json).read_text())
    template = _jinja_env.get_template("pr_body.jinja2")
    output = template.render(
        findings=[Finding.model_validate(f) for f in data["findings"]],
        strategy=StrategyRecommendation.model_validate(data["strategy"]),
        validation=(
            ValidationResult.model_validate(data["validation"])
            if data.get("validation")
            else None
        ),
        consumers=data.get("consumers", []),
        commit_sha=data.get("commit_sha", "HEAD"),
    )
    click.echo(output)


@main.command("render-checklist")
@click.argument("data_json", type=click.Path(exists=True))
def render_checklist(data_json: str) -> None:
    """Render reviewer checklist from remediation data JSON file.

    DATA_JSON must contain: has_generated_tests (bool), is_major_update (bool).
    """
    data = json.loads(Path(data_json).read_text())
    template = _jinja_env.get_template("reviewer_checklist.jinja2")
    output = template.render(
        has_generated_tests=data.get("has_generated_tests", False),
        is_major_update=data.get("is_major_update", False),
    )
    click.echo(output)


@main.command("render-decision-log")
@click.argument("data_json", type=click.Path(exists=True))
def render_decision_log(data_json: str) -> None:
    """Render decision log entry from remediation record JSON file.

    DATA_JSON must contain a full RemediationRecord.
    """
    data = json.loads(Path(data_json).read_text())
    record = RemediationRecord.model_validate(data)
    template = _jinja_env.get_template("decision_log.jinja2")
    output = template.render(record=record)
    click.echo(output)


# ── Helpers ──────────────────────────────────────────────────────────────────


def _render_table(findings: list[Finding]) -> None:
    """Render findings as a Rich terminal table."""
    table = Table(title="Vulnerability Findings")
    table.add_column("Severity", style="bold")
    table.add_column("Package")
    table.add_column("Version")
    table.add_column("Advisory")
    table.add_column("Fix Available")
    for f in findings:
        style = {
            "critical": "red bold",
            "high": "red",
            "medium": "yellow",
            "low": "dim",
        }.get(f.severity, "")
        table.add_row(
            f.severity.upper(),
            f.package_name,
            f.current_version,
            ", ".join(f.advisory_ids[:2]),
            "Yes" if f.candidate_fixed_versions else "No",
            style=style,
        )
    console.print(table)
