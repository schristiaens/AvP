# VulnRemediation Skill Test — OWASP/NodeGoat

**Date:** 2026-03-14
**Target:** https://github.com/OWASP/NodeGoat (master, depth=1 clone)
**Ecosystem:** npm

## Findings Summary

- **Total findings:** 157
- **Critical:** 17
- **High:** 82
- **Moderate:** 44
- **Low:** 14
- **High/Critical loaded via GenericAdapter:** 99

## Files

| # | File | CLI Command / Step | Description |
|---|------|-------------------|-------------|
| 01 | `01-npm-audit-raw.json` | `npm audit --json` | Raw npm audit output (134 KB) |
| 02 | `02-findings-normalized.json` | Python transform | All 157 findings in Finding model format |
| 03 | `03-generic-adapter-output.json` | `GenericAdapter.fetch_findings(severity=['critical','high'])` | 99 high/critical findings after adapter filtering |
| 04 | `04-osv-check-express.json` | `vuln-remediation osv-check pkg:npm/express 4.21.0` | Express 4.21.0 confirmed safe |
| 05 | `05-osv-check-marked.json` | `vuln-remediation osv-check pkg:npm/marked 4.3.0` | Marked 4.3.0 confirmed safe |
| 06 | `06-changelog-express.json` | `vuln-remediation changelog express 4.13.4 4.21.0` | Minor delta, no breaking changes |
| 07 | `07-pr-template-data.json` | Assembled from findings | Input data for PR/checklist/decision-log templates |
| 08 | `08-remediation-record.json` | Assembled from findings | Full RemediationRecord for decision log |
| 09 | `09-rendered-pr-body.md` | `vuln-remediation render-pr` | Rendered PR body with findings, strategy, validation |
| 10 | `10-rendered-checklist.md` | `vuln-remediation render-checklist` | Reviewer checklist (includes major-version approval) |
| 11 | `11-rendered-decision-log.md` | `vuln-remediation render-decision-log` | Full decision log entry |
| 12 | `12-changelog-marked.json` | `vuln-remediation changelog marked 0.3.5 4.3.0` | Major delta, no breaking changes detected |
| 13 | `13-dedup-check.json` | `vuln-remediation dedup-check OWASP/NodeGoat GHSA-67hx-6x53-jw92` | No existing PRs/branches found |

## CLI Commands Tested

All 7 subcommands exercised:
- `fetch` — skipped (requires SNYK_TOKEN), replaced by GenericAdapter + npm audit
- `osv-check` — 2 runs (express, marked)
- `changelog` — 2 runs (express 4.13.4→4.21.0, marked 0.3.5→4.3.0)
- `dedup-check` — 1 run (GHSA-67hx-6x53-jw92)
- `render-pr` — 1 run
- `render-checklist` — 1 run
- `render-decision-log` — 1 run
