# Decision Log: GHSA-67hx-6x53-jw92

**Date:** 2026-03-14 15:00
**Package:** babel-traverse@*
**Repository:** OWASP/NodeGoat
**Branch:** master
**Manifest:** `package.json`
**Status:** PR_OPENED

---

## Finding

| Field | Value |
|---|---|
| Severity | CRITICAL |
| CVSS | 9.4 |
| EPSS | N/A |
| Ecosystem | npm |
| Dependency type | transitive |
| Reachable | Unknown |
| Exploit maturity | Unknown |
| Advisories | GHSA-67hx-6x53-jw92 |


**Dependency path:** node_modules/nyc/node_modules/babel-traverse


## Strategy

**Recommended:** UPDATE
**Target version:** 7.26.0
**Confidence:** 85%

Patch update resolves GHSA-67hx-6x53-jw92 with no breaking changes detected. OSV/GHSA check confirms target version is clean.

### Alternatives Considered

- Stay on 6.x line — no fix available for CVE



### Breaking Change Signals

- Semver delta: major


- Deprecated: babel-traverse is deprecated in favor of @babel/traverse



### Candidate Version Safety

- 7.26.0: Safe



## Validation

| Check | Result |
|---|---|
| Build | Passed |
| Tests | Passed |
| Re-scan | Clean |
| Mode | direct |
| Confidence | 85% |

<details>
<summary>Test output</summary>

```
42 passing, 0 failing
```
</details>

<details>
<summary>Scan output</summary>

```
GHSA-67hx-6x53-jw92 no longer present in scan results
```
</details>

<details>
<summary>Lockfile diff</summary>

```
3 packages updated, 0 removed, 1 added
```
</details>



## PR

https://github.com/OWASP/NodeGoat/pull/999



## Downstream Consumers

- app.js

- config/express.js



## Decision Rationale

Major version bump required but package is deprecated in favor of @babel/traverse. Update resolves critical prototype pollution vulnerability.


**Completed:** 2026-03-14 15:30


