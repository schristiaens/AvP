# ShipPR — Generate and Open PR with Evidence

Generate a PR from a validated fix. Renders templates, opens PR via `gh`, writes decision log.

## Triggers

- "open PR"
- "ship fix"
- "create PR"

## Input

- Validated fix on a `vuln-remediation/<advisory-id>` branch
- `StrategyRecommendation` from SelectStrategy
- `ValidationResult` from ValidateFix
- Finding(s) being remediated
- Repo config (`.vuln-remediation.yml`)

## Steps

### 1. Prepare Template Data

Assemble a JSON data file with all template inputs:

```json
{
  "findings": [...],
  "strategy": {...},
  "validation": {...},
  "consumers": [...],
  "commit_sha": "abc123",
  "has_generated_tests": false,
  "is_major_update": false
}
```

Save to `/tmp/pr-data.json`.

### 2. Render PR Body

```bash
uv run vuln-remediation render-pr /tmp/pr-data.json > /tmp/pr-body.md
```

### 3. Render Reviewer Checklist

```bash
uv run vuln-remediation render-checklist /tmp/pr-data.json >> /tmp/pr-body.md
```

Append the checklist to the PR body.

### 4. Open PR

```bash
gh pr create \
  --base main \
  --head vuln-remediation/<advisory-id> \
  --title "fix(deps): remediate <advisory-id> in <package>@<version>" \
  --body-file /tmp/pr-body.md \
  --label "security,dependencies"
```

**PR title format:** `fix(deps): remediate <advisory-id> in <package>@<version>`

### 5. Write Decision Log

```bash
uv run vuln-remediation render-decision-log /tmp/remediation-record.json > \
  .vuln-remediation/logs/$(date +%Y-%m-%d)-<advisory-id>.md
```

Create the `.vuln-remediation/logs/` directory if it doesn't exist:
```bash
mkdir -p .vuln-remediation/logs
```

### 6. Commit Decision Log

```bash
git add .vuln-remediation/logs/
git commit -m "docs: add decision log for <advisory-id> remediation"
git push origin vuln-remediation/<advisory-id>
```

### 7. Report

- Display the PR URL to the human
- Summarize: finding, strategy chosen, confidence score, validation results
- If confidence was below threshold, explain why the PR was still opened (human override) or why a report was generated instead

## PR Content Includes

Per the plan spec, every PR body contains:

- Triggering findings and advisory IDs
- Chosen strategy + rejected alternatives with reasoning
- Version delta (current → target)
- Breaking change summary
- New-vulnerability check result
- Test evidence summary
- Downstream consumer impact
- Reviewer checklist
- Rollback instructions

## Branch Naming Convention

All branches use `vuln-remediation/{advisory-id}` — this enables:
- Dedup-check across humans running the same skill
- PR discovery via `gh pr list --head vuln-remediation/...`
- Branch discovery via GitHub API

## Decision Log Location

Decision logs are committed to `.vuln-remediation/logs/` in the target repo:
- Format: `{date}-{advisory-id}.md`
- Creates a persistent audit trail visible to all humans
- Committed to the PR branch so the log arrives with the fix

## Notes

- This workflow modifies the repository (commits decision log, pushes branch, creates PR)
- If `gh pr create` fails, save PR body to `/tmp/pr-body.md` and provide manual instructions
- Labels `security` and `dependencies` are created automatically if they don't exist
