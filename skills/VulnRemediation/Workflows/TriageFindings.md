# TriageFindings — Apply Policy and Rank Findings

Apply policy to a set of findings and rank them by remediation priority.

## Triggers

- "triage"
- "prioritize"
- "which vulns matter"

## Input

- Findings from FetchFindings workflow output, or a previously saved findings JSON file
- Policy config from `.vuln-remediation.yml` (or defaults)

## Policy Application

Apply the following filters and scoring from config:

### Severity Threshold
- Default: `high` and above
- If `allowReachableMedium: true` in config, include medium-severity findings where `reachable: true`

### Scoring Factors (weighted)
1. **Severity** (weight: 0.30) — critical > high > medium > low
2. **Exploit maturity** (weight: 0.25) — active > poc > theoretical > none
3. **Reachability** (weight: 0.20) — reachable > unknown > unreachable
4. **Dependency type** (weight: 0.15) — direct > transitive > base_image
5. **Fix availability** (weight: 0.10) — fix available > no fix

### Exclusions
- Skip findings where `fix_types_available` is empty AND severity < critical
- Skip findings already covered by existing PRs (run dedup-check)

## Steps

1. **Load findings** — from FetchFindings output or provided file
2. **Load policy** — read `.vuln-remediation.yml` from repo root, merge with defaults
3. **Apply severity filter** — tag excluded findings with `below_severity`
4. **Apply fix-availability filter** — tag findings with no fix and severity < critical as `no_fix`
5. **Run dedup-check** — tag findings with existing PRs as `already_open`; tag same-advisory duplicates as `duplicate`
6. **Score remaining findings** — apply weighted scoring
7. **Rank** — sort by composite score, descending
8. **Present to human** — display both the ranked candidates AND the skip summary (see Output below)
9. **Human selects** which finding(s) to remediate — tag unselected as `not_selected`

## Output

Always display TWO sections:

### Selected Findings
Ranked list with score, package, severity, exploit maturity, fix available.

### Skip Summary
**Always shown.** One line per skip reason with count and example packages. Format:

```
── Skip Summary (N of M findings not remediated) ──
  below_severity  (12) — Below severity threshold (medium/low excluded)
  no_fix          (8)  — No fix available (non-critical): debug@2.2.0, qs@4.0.0, …
  already_open    (2)  — Existing PR already covers this: GHSA-xxxx
  duplicate       (5)  — Same advisory fixed via another package
```

Each skipped finding is recorded as a `SkippedFinding` (see models.py) with:
- `skip_reason`: one of `below_severity`, `no_fix`, `already_open`, `duplicate`, `not_selected`
- `skip_detail`: one-line explanation specific to that finding

Build a `TriageSummary` containing both `selected` and `skipped` lists. This summary is passed forward to the Remediate workflow for post-flight reporting.

## Notes

- This workflow does NOT modify the repository
- Can operate on stale findings — useful for re-triaging after partial remediation
- Every finding must appear in either `selected` or `skipped` — nothing silently disappears
