# VulnRemediation Skill Test — erev0s/VAmPI

**Date:** 2026-03-14
**Target:** https://github.com/erev0s/VAmPI (master, depth=1 clone)
**Ecosystem:** Python/pip (scanned via OSV API)

## Findings Summary

- **Total findings:** 4
- **High:** 2 (flask, PyJWT)
- **Medium:** 1 (flask — separate advisory)
- **Low:** 1 (flask — separate advisory)
- **Selected for remediation:** 2

## Skip Summary (new feature)

```
── Skip Summary (2 of 4 findings not remediated) ──
  below_severity       (2) — Below severity threshold: flask (medium/low advisories)
```

Additionally, Flask's HIGH finding (GHSA-m2qf-hxjv-5gpq) was selected but its candidate fix version 2.3.2 was flagged as unsafe by osv-check — it introduces a new advisory (GHSA-68rp-wp8r-4726). This would result in a `low_confidence` skip in a full run.

## Files

| # | File | CLI Command / Step | Description |
|---|------|-------------------|-------------|
| 01 | `01-osv-scan-raw.json` | OSV API batch query | Raw findings for all 7 pinned deps |
| 02 | `02-generic-adapter-all.json` | `GenericAdapter.fetch_findings()` | All 4 findings through adapter |
| 03 | `03-generic-adapter-high-crit.json` | `GenericAdapter.fetch_findings(severity=['critical','high'])` | 2 high findings after filtering |
| 04 | `04-triage-summary.json` | `TriageSummary` model | Full triage with selected + skipped (new SkipReason model) |
| 05 | `05-osv-check-flask.json` | `vuln-remediation osv-check pkg:pypi/flask 2.3.2` | **NOT safe** — new advisory GHSA-68rp-wp8r-4726 |
| 06 | `06-osv-check-pyjwt.json` | `vuln-remediation osv-check pkg:pypi/PyJWT 2.12.0` | Safe |
| 07 | `07-changelog-flask.json` | `vuln-remediation changelog flask 2.2.2 2.3.2` | Minor delta, no breaking changes |
| 08 | `08-changelog-pyjwt.json` | `vuln-remediation changelog PyJWT 2.6.0 2.12.0` | Minor delta, no breaking changes |
| 09 | `09-dedup-check.json` | `vuln-remediation dedup-check erev0s/VAmPI GHSA-m2qf-hxjv-5gpq` | No existing PRs |
| 10 | `10-pr-template-data.json` | Assembled from findings | Input data for templates (PyJWT fix) |
| 11 | `11-remediation-record.json` | Assembled from findings | Full RemediationRecord |
| 12 | `12-rendered-pr-body.md` | `vuln-remediation render-pr` | PR body for PyJWT 2.6.0→2.12.0 |
| 13 | `13-rendered-checklist.md` | `vuln-remediation render-checklist` | Reviewer checklist (no major-version flag) |
| 14 | `14-rendered-decision-log.md` | `vuln-remediation render-decision-log` | Decision log with Flask deferral rationale |

## Notable Observations

- **OSV catch:** Flask 2.3.2 (the "fix" version) itself has a known advisory — the skill correctly flags this
- **Skip reasons work:** TriageSummary model correctly categorizes medium/low findings as `below_severity`
- **Smaller attack surface:** Only 7 direct deps means fewer findings, but the quality of each finding matters more
