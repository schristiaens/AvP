---
name: VulnRemediation
description: >-
  Vulnerability remediation for dependencies — fetch scanner findings,
  select fix strategy, validate in sandbox, open PR with evidence.
  USE WHEN vuln remediation, fix vulnerability, remediate CVE,
  dependency update, security fix, snyk fix, wiz remediation,
  patch vulnerability, upgrade dependency.
---

# VulnRemediation Skill

Human-directed, single-repo vulnerability remediation assistant. Point the agent at a repo and a set of findings — it selects the safest fix, validates it, and opens a PR with evidence.

## Prerequisites

- Python 3.12+
- `uv` installed (`curl -LsSf https://astral.sh/uv/install.sh | sh`)
- GitHub CLI authenticated (`gh auth status`)
- Scanner API token in environment (`SNYK_TOKEN` for Snyk)

## Installation

```bash
# From this skill directory:
uv sync
```

## CLI

All subcommands available via:

```bash
uv run vuln-remediation <subcommand> [args]
```

| Command | Purpose |
|---|---|
| `fetch <org_id> <project_id>` | Fetch findings from Snyk |
| `osv-check <purl> <version>` | Check candidate version against OSV/GHSA |
| `changelog <pkg> <from> <to>` | Fetch changelog and breaking change signals |
| `dedup-check <repo> <advisory_id>` | Search for existing remediation PRs/branches |
| `render-pr <data_json>` | Render PR body from remediation data |
| `render-checklist <data_json>` | Render reviewer checklist |
| `render-decision-log <data_json>` | Render decision log entry |

## Workflow Routing

| Trigger | Workflow | Description |
|---|---|---|
| "remediate", "fix vuln", "fix CVE" (DEFAULT) | `Workflows/Remediate.md` | Full end-to-end remediation |
| "fetch findings", "scan", "what's vulnerable" | `Workflows/FetchFindings.md` | Pull and display findings only |
| "triage", "prioritize", "which vulns matter" | `Workflows/TriageFindings.md` | Apply policy, rank findings |
| "what strategy", "how to fix", "analyze fix" | `Workflows/SelectStrategy.md` | Strategy selection for specific finding |
| "validate fix", "test fix", "verify update" | `Workflows/ValidateFix.md` | Build/test a proposed fix |
| "open PR", "ship fix", "create PR" | `Workflows/ShipPR.md` | Generate PR from validated fix |

## Repo-Level Config

Place `.vuln-remediation.yml` in any target repo to customize behavior. See `docs/superpowers/specs/vuln-remediation-skill-plan.md` for schema.
