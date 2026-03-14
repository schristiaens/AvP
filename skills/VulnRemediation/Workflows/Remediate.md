# Remediate — Full End-to-End Workflow

The primary workflow. Fetch findings → triage → select strategy → validate fix → ship PR.

## Pre-flight Checks

Before starting, verify all prerequisites:

1. **Scanner access** — confirm `SNYK_TOKEN` is set:
   ```bash
   test -n "$SNYK_TOKEN" && echo "Snyk token set" || echo "ERROR: SNYK_TOKEN not set"
   ```

2. **GitHub CLI** — confirm authenticated:
   ```bash
   gh auth status
   ```

3. **Clean working tree** — confirm no uncommitted changes:
   ```bash
   git status --porcelain
   ```

4. **Python toolchain** — confirm CLI is available:
   ```bash
   uv run vuln-remediation --version
   ```

5. **Repo config** — read `.vuln-remediation.yml` if present, otherwise use defaults.

6. **Dedup check** — search for existing remediation work:
   ```bash
   uv run vuln-remediation dedup-check <owner/repo> <advisory-id>
   ```
   If an existing PR is found, inform the human and ask whether to proceed, update the existing PR, or skip.

## Step 1: Fetch Findings

Run the FetchFindings workflow (see `FetchFindings.md`).

```bash
uv run vuln-remediation fetch <org-id> <project-id> --output json > /tmp/findings.json
```

Display summary: total findings count, breakdown by severity, breakdown by ecosystem.

## Step 2: Triage

Run the TriageFindings workflow (see `TriageFindings.md`).

Apply policy from `.vuln-remediation.yml` (severity threshold, reachability, exposure). Present ranked findings to the human. Human selects which finding(s) to remediate, or accepts agent recommendation.

## Step 3: Strategy Selection

For each selected finding, run the SelectStrategy workflow (see `SelectStrategy.md`).

For each candidate version:
1. Run `uv run vuln-remediation osv-check <purl> <version>` — verify no new advisories
2. Run `uv run vuln-remediation changelog <pkg> <from> <to>` — assess breaking change risk
3. Score compatibility: semver delta, changelog signals, repo call-site analysis

Select lowest-risk viable strategy. Present recommendation to human with rationale. Human approves or overrides.

## Step 4: Validate

Run the ValidateFix workflow (see `ValidateFix.md`).

1. Create feature branch: `vuln-remediation/{advisory-id}`
2. Apply the fix (version update, lockfile regeneration, etc.)
3. Run build and test suite
4. Re-scan with scanner CLI
5. Collect evidence: test output, scan results, diff
6. Compute confidence score
7. If confidence < threshold from config, present as report instead of PR

## Step 5: Ship PR

Run the ShipPR workflow (see `ShipPR.md`).

1. Render PR body via `uv run vuln-remediation render-pr`
2. Render reviewer checklist via `uv run vuln-remediation render-checklist`
3. Open PR via `gh pr create`
4. Render decision log via `uv run vuln-remediation render-decision-log`
5. Commit decision log to `.vuln-remediation/logs/{date}-{advisory}.md` on the PR branch

## Step 6: Post-flight

Display the full disposition of every finding. Nothing silently disappears.

### Remediated
- PR URL and finding(s) it covers

### Not Remediated — Skip Summary
Merge the triage `TriageSummary.skipped` list with any findings that failed in later stages:
- Strategy confidence below threshold → `low_confidence`
- Validation (build/test/rescan) failed → `validation_failed`

Print the skip summary table (same format as triage output):

```
── Skip Summary (N of M findings not remediated) ──
  below_severity      (12) — medium/low excluded by policy
  no_fix              (8)  — no known fix version: debug@2.2.0, qs@4.0.0, …
  already_open        (2)  — existing PR covers this advisory
  duplicate           (5)  — same advisory fixed via another package
  not_selected        (3)  — human chose not to remediate
  low_confidence      (1)  — strategy confidence 0.45 < 0.80 threshold
  validation_failed   (1)  — build failed after updating needle@3.0.0
```

This table MUST appear in every run, even when all findings are remediated (in which case: "All N findings remediated — no skips").

## Confidence Thresholds

From config (defaults):
- `>= 0.80` for patch/minor updates → open PR
- `>= 0.90` for major updates → open PR
- Below threshold → generate report, not PR

## Error Handling

- If scanner fetch fails: report the error, suggest checking `SNYK_TOKEN` and network connectivity
- If OSV/GHSA check fails: proceed with warning, note reduced confidence
- If build/test fails: do NOT open PR — present failure evidence to human
- If `gh pr create` fails: save PR body locally, provide manual instructions
