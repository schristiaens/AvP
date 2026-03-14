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
3. **Apply severity filter** — remove findings below threshold
4. **Run dedup-check** — for each finding's advisory IDs, check for existing PRs
5. **Score remaining findings** — apply weighted scoring
6. **Rank** — sort by composite score, descending
7. **Present to human**:
   - Ranked list with score, package, severity, exploit maturity, fix available
   - Excluded findings with reason for exclusion
   - Recommendation: "I recommend starting with these N findings"
8. **Human selects** which finding(s) to remediate

## Output

- Prioritized list of findings with reasoning for each inclusion/exclusion
- Human's selection (one or more findings to proceed with)

## Notes

- This workflow does NOT modify the repository
- Can operate on stale findings — useful for re-triaging after partial remediation
