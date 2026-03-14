# SelectStrategy — Choose Fix Approach for a Finding

Deep-dive analysis on a single finding. Analyze all remediation options, check candidate versions, assess breaking changes, and recommend a strategy.

## Triggers

- "what strategy"
- "how to fix"
- "analyze fix"

## Input

- Single finding record (package, current version, advisory IDs)
- Strategy decision tree from `data/strategy_decision_tree.yaml`
- Repo context (manifest files, lockfile, call sites)

## Strategy Decision Tree

Evaluate in order — first viable strategy wins:

### 1. UPDATE (preferred)
- Find lowest safe version that resolves the advisory
- For each candidate version (ascending from current):
  1. `uv run vuln-remediation osv-check <purl> <version>` — reject if new critical/high advisories
  2. `uv run vuln-remediation changelog <pkg> <current> <candidate>` — assess breaking changes
  3. Analyze semver delta:
     - **Patch**: high confidence, proceed
     - **Minor**: medium confidence, check changelog for deprecations
     - **Major**: low confidence, require explicit breaking change analysis
  4. Search repo for call sites of the package — assess actual usage patterns
- If lowest safe version fails validation, escalate to next version
- If all versions have breaking changes, fall through to PATCH

### 2. PATCH
- Only when an authoritative patch exists (vendor patch, backport)
- Applicable when update path is breaking or unavailable
- Verify patch applies cleanly to current version

### 3. REPLACE
- Advisory-only unless a curated replacement exists in `data/curated_replacements.yaml`
- Present replacement as a recommendation, not automatic
- Requires human approval before proceeding

### 4. MITIGATE
- Config or code change that neutralizes the vulnerability
- Always paired with a follow-up ticket for permanent fix
- Examples: WAF rule, feature flag disable, input validation

## Steps

1. **Load finding** — parse the finding record
2. **Load decision tree** — read `data/strategy_decision_tree.yaml`
3. **Check candidate versions** — iterate through `candidate_fixed_versions`
4. **For each candidate**:
   - Run OSV check
   - Run changelog fetch
   - Analyze semver delta
   - Search for call sites in the repo
5. **Score each strategy option** — compute confidence based on:
   - Version safety (OSV/GHSA clean)
   - Breaking change risk (semver + changelog signals)
   - Call-site impact (how deeply the package is used)
   - Fix availability (direct update vs. transitive resolution)
6. **Select lowest-risk viable strategy**
7. **Present recommendation** to human:
   - Recommended strategy with confidence score
   - Target version (if applicable)
   - Breaking change summary
   - Alternatives considered with reasons for rejection
8. **Human approves or overrides**

## Output

- `StrategyRecommendation` model with:
  - Recommended strategy type
  - Target version
  - Confidence score
  - Rationale
  - Breaking change signals
  - Candidate version safety checks
  - Alternatives considered

## Candidate Version Safety Rules

- Reject if new critical advisory in same scope
- Reject if new high advisory in same scope
- Reject if total unresolved advisories > baseline
- Accept only if OSV + GHSA both report clean

## Notes

- This workflow does NOT modify the repository
- LLM summarization is used for the explanation layer, not the decision layer
- The decision tree is deterministic — LLM assists with changelog interpretation only
