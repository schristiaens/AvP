# ValidateFix — Apply Fix, Build, Test, Re-scan

Apply a proposed fix and run full validation. Creates a branch, applies the change, runs build/test/re-scan.

## Triggers

- "validate fix"
- "test fix"
- "verify update"

## Input

- Repo path (current working directory)
- Proposed fix: package name, target version, strategy type
- Execution mode from config: `direct`, `docker`, or `docker-restricted`

## Steps

### 1. Create Feature Branch

```bash
git checkout -b vuln-remediation/<advisory-id>
```

Branch naming convention enforced — enables dedup-check across humans.

### 2. Apply the Fix

Based on the strategy type and ecosystem:

**UPDATE (npm):**
```bash
npm install <package>@<target-version> --save-exact
```

**UPDATE (maven):**
- Edit `pom.xml` to set new version
- Run `mvn dependency:resolve`

**UPDATE (transitive — npm):**
- Add `overrides` entry in `package.json`
- Run `npm install`

After applying:
```bash
# Verify lockfile regenerated cleanly
git diff --stat
```

### 3. Run Build

Execution depends on configured mode:

**Direct mode:**
```bash
npm ci && npm run build
```

**Docker mode (recommended):**
```bash
docker run --rm \
  -v $(pwd):/workspace:rw \
  -w /workspace \
  --network=host \
  node:20-slim \
  sh -c "npm ci && npm run build"
```

**Docker restricted mode:**
```bash
docker run --rm \
  --security-opt no-new-privileges \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid \
  -v $(pwd):/workspace:rw \
  -w /workspace \
  --network=none \
  node:20-slim \
  sh -c "npm ci --prefer-offline && npm run build"
```

### 4. Run Tests

Same execution mode as build:
```bash
npm test 2>&1 | tee /tmp/test-output.txt
```

Capture full test output for evidence.

### 5. Re-scan

Run the scanner again to verify the fix resolved the finding:
```bash
snyk test --json > /tmp/rescan-output.json
```

Check that the target advisory no longer appears in results.

### 6. Diff Analysis

```bash
# Lockfile changes
git diff --stat package-lock.json > /tmp/lockfile-diff.txt

# Check for unrelated dependency churn
git diff package-lock.json | grep -c "^[+-]" # line count
```

Reject if lockfile diff introduces unrelated major changes (> 50 changed packages).

### 7. Compute Confidence Score

| Signal | Weight | Scoring |
|---|---|---|
| Build passed | 0.25 | 1.0 if passed, 0.0 if failed |
| Tests passed | 0.25 | 1.0 if passed, 0.0 if failed |
| Re-scan clean | 0.25 | 1.0 if advisory removed, 0.0 if still present |
| Lockfile stability | 0.15 | 1.0 if < 10 packages changed, 0.5 if 10-50, 0.0 if > 50 |
| Semver delta | 0.10 | 1.0 for patch, 0.7 for minor, 0.4 for major |

**Confidence = weighted sum of all signals.**

### 8. Decision

- If confidence >= threshold (default 0.80, or 0.90 for major): recommend PR
- If confidence < threshold: recommend report-only, do NOT open PR

## Output

- `ValidationResult` model with:
  - `success`: overall pass/fail
  - `build_passed`: bool
  - `test_passed`: bool
  - `rescan_clean`: bool
  - `confidence`: float
  - `test_output_summary`: truncated test output
  - `scan_output_summary`: truncated scan output
  - `lockfile_diff_summary`: lockfile change summary
  - `execution_mode`: which mode was used

## Rollback

If validation fails, clean up:
```bash
git checkout main
git branch -D vuln-remediation/<advisory-id>
```

## Notes

- This workflow DOES modify the repository (on a feature branch)
- Never commits to main — always on the `vuln-remediation/` branch
- Never PRs from an unresolved dependency graph
- If Docker is unavailable and mode is `docker`, fall back to `direct` with a warning
