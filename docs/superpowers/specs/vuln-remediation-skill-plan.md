# Vulnerability Remediation Skill — Build Plan

Date: 2026-03-14
Status: Draft v1
Predecessor: vuln-remediation-service-plan.md

## What Changed and Why

The original plan described a long-running service (Temporal + PostgreSQL + Fastify + Docker workers). This document re-targets the same domain logic as a PAI skill — an AI agent capability that any human can invoke from their own Claude Code agent session.

### What the skill IS

A human-directed, single-repo vulnerability remediation assistant. A security engineer points the agent at a repo and a set of findings. The agent selects the safest fix, validates it, and opens a PR with evidence.

### What the skill IS NOT

- A portfolio-wide automation engine (that's a future service that could orchestrate skill invocations)
- A scanner (still delegates to Snyk/Wiz)
- An auto-merge bot
- A replacement for human judgment on what to fix

### Why this shape

First principles analysis shows 5 of the original 14 service components are irreducible (fetch findings, triage, strategize, validate, ship PR). The other 9 existed because the service ran unattended at scale. An attended agent needs none of them. This eliminates PostgreSQL, Temporal, Fastify, queue workers, observability stack, priority queue, persistent dedup, artifact storage, and concurrency management.

## Architecture: Service vs Skill

| Service Component | Skill Equivalent | Rationale |
|---|---|---|
| Scanner ingestion adapters | **Workflow: FetchFindings** | Agent calls scanner API via CLI or HTTP |
| Normalization/dedup store | **In-session normalization** | Agent normalizes in memory; dedup via GitHub PR search |
| Risk/policy engine | **Workflow: TriageFindings** | Policy from `.vuln-remediation.yml`, applied by agent |
| Fix strategy engine | **Workflow: SelectStrategy** | Decision tree preserved as workflow instructions |
| Execution orchestrator (Temporal) | **Agent session** | Agent IS the orchestrator |
| Docker workers | **Workflow: ValidateFix** | Agent runs build/test via Bash (Docker optional but recommended) |
| Breaking change analyzer | **Workflow step in SelectStrategy** | Agent fetches changelogs, diffs APIs, assesses risk |
| Candidate version safety | **Workflow step in SelectStrategy** | Agent queries OSV/GHSA before selecting version |
| PR composer | **Workflow: ShipPR** | Agent generates PR via `gh` CLI |
| Consumer impact discoverer | **Workflow step in ShipPR** | Agent reads repo config for consumer metadata |
| Priority queue | **Eliminated** | Human selects what to remediate |
| PostgreSQL database | **Eliminated** | Session memory + git + PR history |
| Temporal workflow engine | **Eliminated** | Agent session handles orchestration |
| Observability stack | **Eliminated** | Agent output is the observability |
| Config management | **`.vuln-remediation.yml` + skill customizations** | Preserved, simplified |

## Skill Directory Structure

```
~/.claude/skills/VulnRemediation/
├── SKILL.md                          # Routing, triggers, voice notification
├── Workflows/
│   ├── Remediate.md                  # Full workflow: fetch → triage → fix → validate → PR
│   ├── FetchFindings.md              # Standalone: pull findings from scanner
│   ├── TriageFindings.md             # Standalone: apply policy, rank by risk
│   ├── SelectStrategy.md            # Standalone: choose fix approach for a finding
│   ├── ValidateFix.md               # Standalone: apply fix, build, test, re-scan
│   └── ShipPR.md                    # Standalone: generate PR with evidence
├── Tools/
│   ├── snyk-fetch.ts                # CLI: fetch findings from Snyk API
│   ├── osv-check.ts                 # CLI: query OSV/GHSA for advisory overlap
│   ├── changelog-fetch.ts           # CLI: fetch release notes for a package version
│   ├── dedup-check.ts               # CLI: search GitHub for existing remediation PRs/branches
│   └── config.ts                    # Shared config: API endpoints, defaults
├── Templates/
│   ├── pr-body.hbs                  # PR body template with evidence sections
│   ├── reviewer-checklist.hbs       # Reviewer checklist for PR
│   └── decision-log.hbs             # Session decision log for audit trail
└── Data/
    ├── strategy-decision-tree.yaml  # 4-strategy decision tree (update/patch/replace/mitigate)
    ├── ecosystem-support.yaml       # Supported ecosystems and their toolchains
    └── curated-replacements.yaml    # Known safe package replacements
```

## SKILL.md Definition

```yaml
---
name: VulnRemediation
description: >-
  Vulnerability remediation for dependencies — fetch scanner findings,
  select fix strategy, validate in sandbox, open PR with evidence.
  USE WHEN vuln remediation, fix vulnerability, remediate CVE,
  dependency update, security fix, snyk fix, wiz remediation,
  patch vulnerability, upgrade dependency.
---
```

### Workflow Routing Table

| Trigger | Workflow | Description |
|---|---|---|
| "remediate", "fix vuln", "fix CVE" (DEFAULT) | `Workflows/Remediate.md` | Full end-to-end remediation |
| "fetch findings", "scan", "what's vulnerable" | `Workflows/FetchFindings.md` | Pull and display findings only |
| "triage", "prioritize", "which vulns matter" | `Workflows/TriageFindings.md` | Apply policy, rank findings |
| "what strategy", "how to fix", "analyze fix" | `Workflows/SelectStrategy.md` | Strategy selection for specific finding |
| "validate fix", "test fix", "verify update" | `Workflows/ValidateFix.md` | Build/test a proposed fix |
| "open PR", "ship fix", "create PR" | `Workflows/ShipPR.md` | Generate PR from validated fix |

## Workflow Details

### Remediate.md (Primary Workflow)

The full pipeline, invoked when a human says "remediate vulnerabilities in this repo."

**Steps:**

1. **Pre-flight checks**
   - Verify scanner CLI or API token is available
   - Verify GitHub CLI authenticated (`gh auth status`)
   - Verify repo is a git repo with clean working tree
   - Read `.vuln-remediation.yml` if present, else use defaults
   - Run `dedup-check.ts` — search for existing remediation PRs/branches

2. **Fetch findings**
   - Run `snyk-fetch.ts` or call scanner API directly
   - Normalize findings into uniform records (in agent memory)
   - Display summary: total findings, by severity, by ecosystem

3. **Triage**
   - Apply policy from config (severity threshold, reachability, exposure)
   - Present ranked findings to human
   - Human selects which finding(s) to remediate (or accepts agent recommendation)

4. **Strategy selection** (per selected finding)
   - Load `strategy-decision-tree.yaml`
   - For each candidate version:
     - Run `osv-check.ts` to verify no new advisories
     - Run `changelog-fetch.ts` to assess breaking change risk
     - Score compatibility: semver delta, changelog signals, repo call-site analysis
   - Select lowest-risk viable strategy
   - Present recommendation to human with rationale
   - Human approves or overrides

5. **Validate**
   - Create feature branch: `vuln-remediation/{advisory-id}`
   - Apply the fix (version update, lockfile regeneration, etc.)
   - Run build and test suite
   - Re-scan with scanner CLI
   - Collect evidence: test output, scan results, diff
   - Compute confidence score
   - If confidence < threshold, present as report instead of PR

6. **Ship PR**
   - Render `pr-body.hbs` with evidence
   - Render `reviewer-checklist.hbs`
   - Open PR via `gh pr create`
   - Write `decision-log.hbs` output to `.vuln-remediation/logs/{date}-{advisory}.md` in repo
   - Commit decision log to the PR branch

7. **Post-flight**
   - Display PR URL
   - Summarize what was done, what was skipped, and why

### FetchFindings.md (Standalone)

Fetch-only mode for reconnaissance. Agent pulls findings and presents them without taking action. Useful for a human to survey the landscape before deciding what to remediate.

**Input:** Repo path + scanner source (snyk, wiz, or generic report file)
**Output:** Formatted table of findings with severity, ecosystem, package, current version, fix available (y/n)

### TriageFindings.md (Standalone)

Apply policy to a set of findings and rank them. Can operate on output from FetchFindings or on a previously saved findings file.

**Input:** Findings (from fetch or file) + policy config
**Output:** Prioritized list with reasoning for each inclusion/exclusion

### SelectStrategy.md (Standalone)

Deep-dive on a single finding. Agent analyzes all remediation options, checks candidate versions, assesses breaking changes, and recommends a strategy.

**Input:** Single finding record (package, version, advisory)
**Output:** Strategy recommendation with evidence, alternatives considered, confidence score

### ValidateFix.md (Standalone)

Apply a proposed fix and run validation. Agent creates a branch, applies the change, runs build/test/re-scan.

**Input:** Repo + proposed fix (package, target version, strategy)
**Output:** Validation report (pass/fail, test output, scan results, confidence score)

### ShipPR.md (Standalone)

Generate and open a PR from a validated fix. Agent renders PR template with evidence, opens PR, writes decision log.

**Input:** Validated fix artifacts + repo
**Output:** PR URL + decision log committed

## Tool Specifications

### snyk-fetch.ts

```
Usage: bun snyk-fetch.ts <org-id> <project-id> [--severity high,critical] [--type npm|maven|docker]
Output: JSON array of normalized finding records
Auth: SNYK_TOKEN env var
```

Fetches issues from Snyk Issues API, normalizes to the unified schema from the original plan (finding_id, purl, severity, cvss, epss, exploit_maturity, reachable, fix_types_available, etc.).

### osv-check.ts

```
Usage: bun osv-check.ts <purl> <candidate-version>
Output: JSON { safe: boolean, advisories: [...] }
Auth: None (public API)
```

Queries OSV API and GitHub Advisory Database. Returns whether the candidate version has known advisories at or above the threshold.

### changelog-fetch.ts

```
Usage: bun changelog-fetch.ts <package-name> <from-version> <to-version> [--ecosystem npm|maven]
Output: JSON { semver_delta: "major|minor|patch", changelog_url: "...", breaking_changes: [...], deprecations: [...] }
Auth: None (public registries)
```

Fetches release notes from npm registry, Maven Central, or GitHub releases. Extracts structured breaking change signals.

### dedup-check.ts

```
Usage: bun dedup-check.ts <repo> <advisory-id>
Output: JSON { existing_pr: null | { url, status, branch }, existing_branch: null | string }
Auth: GH_TOKEN or gh CLI auth
```

Searches for existing PRs or branches matching the `vuln-remediation/{advisory-id}` naming convention. Prevents duplicate remediation work across humans.

### config.ts

Shared configuration constants:
- Scanner API base URLs
- Default policy thresholds
- Supported ecosystems and their toolchain expectations
- PR template field mappings
- Decision log output path convention

## Multi-Human Consumption Model

### What's shared (in the repo)

- `.vuln-remediation.yml` — repo-level policy config (risk thresholds, allowed strategies, consumers, notification channels)
- `.vuln-remediation/logs/` — decision logs from past remediations (committed to repo)
- PR naming convention: `vuln-remediation/{advisory-id}` — enables dedup-check across humans
- Branch naming convention: same prefix — enables branch search

### What's per-user (in their PAI installation)

- `~/.claude/skills/VulnRemediation/` — the skill definition (same for all users)
- `~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/VulnRemediation/PREFERENCES.md` — personal overrides (e.g., preferred scanner, default severity threshold, Docker usage preference)
- Scanner API tokens — in user's environment variables
- GitHub auth — in user's `gh` CLI config

### Coordination protocol

1. **Before starting:** Agent runs `dedup-check.ts` to find existing PRs/branches for the target advisory
2. **If existing PR found:** Agent reports it and asks human whether to proceed anyway, update the existing PR, or skip
3. **Branch naming convention enforced:** All branches use `vuln-remediation/{advisory-id}` so other humans' agents can discover them
4. **Decision logs committed to repo:** Each remediation writes a log file to `.vuln-remediation/logs/`, creating a persistent audit trail visible to all humans

### No runtime coordination needed

Each agent session is independent. Git and GitHub are the coordination layer. No shared database, no message queue, no locking protocol.

## Execution Isolation Options

The skill supports three execution modes for the validate step, configured in `.vuln-remediation.yml` or user preferences:

### Mode 1: Direct (fastest, least isolated)

Agent runs `npm install`, `npm test`, etc. directly in the repo working directory on a feature branch. Suitable for trusted, internal packages only.

### Mode 2: Docker container (recommended default)

Agent runs validation inside a container:
```bash
docker run --rm \
  -v $(pwd):/workspace:rw \
  -w /workspace \
  --network=host \
  node:20-slim \
  sh -c "npm ci && npm test"
```

Provides process isolation without requiring a full container orchestration system.

### Mode 3: Docker rootless + network-restricted (most isolated)

For untrusted or public-facing repos:
```bash
docker run --rm \
  --security-opt no-new-privileges \
  --read-only \
  --tmpfs /tmp:rw,noexec,nosuid \
  -v $(pwd):/workspace:rw \
  -w /workspace \
  --network=none \
  node:20-slim \
  sh -c "npm ci --prefer-offline && npm test"
```

Requires pre-cached dependencies or a registry proxy.

## Preserved Domain Logic

The following elements from the original service plan are preserved exactly in the skill's workflow instructions and data files:

### Fix Strategy Decision Tree (strategy-decision-tree.yaml)

1. **Update** — lowest safe direct version first, escalate only if lowest fails
2. **Patch** — authoritative patch only, when update path is breaking/unavailable
3. **Replace** — advisory-only unless curated replacement exists
4. **Mitigate** — config/code change + follow-up ticket for permanent fix

### Confidence Scoring

- `>=0.80` for patch/minor updates → open PR
- `>=0.90` for major updates → open PR
- Below threshold → generate report, not PR

### Breaking Change Analysis Signals

- Semver delta
- Changelog/release notes
- Registry deprecation notices
- API diff tooling (where available)
- Call-site analysis in the repo
- LLM summarization (explanation layer, not decision layer)

### Candidate Version Safety

- Query OSV + GHSA for each candidate
- Reject if new critical or new high in same scope
- Reject if total unresolved > baseline
- Re-scan post-change lockfile

### Transitive Dependency Resolution

- Attempt native override/resolution mechanisms
- Diff full lockfile for unrelated churn
- Reject if graph can't be deterministically resolved
- Never PR from unresolved dependency graph

### PR Content

- Triggering findings and advisory IDs
- Chosen strategy + rejected alternatives with reasoning
- Version delta (current → target)
- Breaking change summary
- New-vulnerability check result
- Test evidence summary
- Downstream consumer impact
- Reviewer checklist
- Rollback instructions

### Reviewer Checklist

- Lowest-risk viable strategy confirmed
- Target version not known-vulnerable in evidence
- Changelog reviewed
- Tests passed in runner
- Generated tests are relevant
- Downstream impact acknowledged
- Rollback instructions sufficient
- Major-version change has owner approval

## What Was Eliminated and Why

| Eliminated Component | Why |
|---|---|
| PostgreSQL | Session memory + git history + decision logs replace persistent store |
| Temporal | Agent session IS the workflow engine; no checkpoint/resume needed for single-repo work |
| Fastify/NestJS API | No API needed; skill is invoked directly |
| Priority queue | Human selects what to fix; agent doesn't need to optimize ordering |
| Concurrency limits | One agent, one session, one repo at a time |
| Persistent dedup store | `dedup-check.ts` searches GitHub for existing PRs/branches |
| Artifact storage (S3) | Evidence embedded in PR body + decision log committed to repo |
| Observability stack | Agent output is visible to human in real-time |
| Runner image management | User's local toolchain or standard Docker images |
| Secret rotation | User manages their own credentials |

## What Was Explicitly Deferred

| Deferred Capability | Why | Future Path |
|---|---|---|
| Portfolio-wide automation | Skill handles 1-10 findings per session | Future orchestrator service invokes skill across repos |
| Cross-repo candidate ledger | No persistent state across sessions | Could be a shared YAML in a central repo |
| Environment consistency guarantees | Users have different toolchains | Could publish recommended Docker images |
| Automated scheduling | No cron/trigger mechanism | Could wrap skill invocation in a CI pipeline |
| Multi-scanner correlation | Session handles one scanner at a time | Could add a correlation workflow later |

## Suggested Repository Config (Preserved)

```yaml
# .vuln-remediation.yml
version: 1
riskThreshold:
  minSeverity: high
  allowReachableMedium: true
supportedEcosystems:
  - npm
  - maven
  - docker
strategies:
  allow:
    - update
    - patch
    - mitigate
  replacementMode: advisory
executionMode: docker  # direct | docker | docker-restricted
consumers:
  - name: billing-api
    type: service
    contractTests: services/billing-api/contracts
notifications:
  slackChannel: "#security-remediation"
  jiraProject: SEC
confidence:
  defaultMin: 0.8
  majorMin: 0.9
```

## Build Plan

### Phase 1: Skill Skeleton + Fetch (Week 1-2)

**Deliverables:**
- SKILL.md with routing table
- `snyk-fetch.ts` tool — fetch and normalize Snyk findings
- `FetchFindings.md` workflow — pull findings, display summary
- `TriageFindings.md` workflow — apply policy from config, rank findings
- `config.ts` with defaults
- `ecosystem-support.yaml` with npm + Maven support

**Independently testable:** Human can invoke `VulnRemediation fetch findings` on any repo and see normalized output.

### Phase 2: Strategy + Safety (Week 3-4)

**Deliverables:**
- `osv-check.ts` tool — query OSV/GHSA
- `changelog-fetch.ts` tool — fetch release notes
- `strategy-decision-tree.yaml` — 4-strategy decision tree
- `SelectStrategy.md` workflow — full strategy selection with breaking change analysis
- `dedup-check.ts` tool — search for existing PRs/branches

**Independently testable:** Human can invoke `VulnRemediation analyze fix` for a specific finding and get a strategy recommendation with evidence.

### Phase 3: Validate + Ship (Week 5-6)

**Deliverables:**
- `ValidateFix.md` workflow — branch, apply fix, build, test, re-scan
- `ShipPR.md` workflow — render PR, open via gh CLI, write decision log
- `pr-body.hbs` template
- `reviewer-checklist.hbs` template
- `decision-log.hbs` template
- Three execution modes (direct, docker, docker-restricted)

**Independently testable:** Human can invoke `VulnRemediation validate fix` and `VulnRemediation ship PR` as standalone steps.

### Phase 4: Full Pipeline + Multi-Human (Week 7-8)

**Deliverables:**
- `Remediate.md` workflow — full end-to-end pipeline connecting all steps
- Multi-human coordination: dedup-check integration, branch naming enforcement, decision log commits
- `curated-replacements.yaml` — initial set of known safe replacements
- User customization support at `~/.claude/PAI/USER/SKILLCUSTOMIZATIONS/VulnRemediation/`

**Independently testable:** Human can invoke `VulnRemediation remediate` and go from findings to PR in one session. Second human can invoke on same repo without collision.

### Phase 5: Ecosystem Expansion (Week 9+)

**Deliverables:**
- Docker base image remediation support
- Generic scanner adapter (for Wiz and others)
- Additional ecosystem support (pnpm, yarn, Gradle)
- Monorepo awareness (detect packages, group by bounded context)

## Open Questions (Carried Forward)

- Which source of truth owns "external consumers": Backstage, repo config, or both?
- Is Wiz API access available, or is normalized import (exported report) the initial path?
- Should the skill support a "report-only" mode that writes findings + recommendations to a file without opening PRs?
- Is there a preferred Docker base image registry for validation containers?
- Should decision logs be committed to the target repo or to a central security-audit repo?
