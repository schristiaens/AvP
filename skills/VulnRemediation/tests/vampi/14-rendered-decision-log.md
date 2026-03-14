# Decision Log: GHSA-752w-5fwx-jx9f, CVE-2026-32597

**Date:** 2026-03-14 16:00
**Package:** PyJWT@2.6.0
**Repository:** erev0s/VAmPI
**Branch:** master
**Manifest:** `requirements.txt`
**Status:** PR_OPENED

---

## Finding

| Field | Value |
|---|---|
| Severity | HIGH |
| CVSS | N/A |
| EPSS | N/A |
| Ecosystem | npm |
| Dependency type | direct |
| Reachable | Unknown |
| Exploit maturity | Unknown |
| Advisories | GHSA-752w-5fwx-jx9f, CVE-2026-32597 |



## Strategy

**Recommended:** UPDATE
**Target version:** 2.12.0
**Confidence:** 92%

Minor version update resolves algorithm confusion vulnerability. OSV/GHSA confirms 2.12.0 is clean. No breaking changes detected in changelog.

### Alternatives Considered

- Update to 2.8.0 (minimum fix) — chosen 2.12.0 for broader advisory coverage



### Breaking Change Signals

- Semver delta: minor




### Candidate Version Safety

- 2.12.0: Safe



## Validation

| Check | Result |
|---|---|
| Build | Passed |
| Tests | Passed |
| Re-scan | Clean |
| Mode | direct |
| Confidence | 92% |

<details>
<summary>Test output</summary>

```
15 passing, 0 failing
```
</details>

<details>
<summary>Scan output</summary>

```
No advisories found for PyJWT@2.12.0
```
</details>

<details>
<summary>Lockfile diff</summary>

```
1 package updated (PyJWT 2.6.0 → 2.12.0)
```
</details>



## PR

https://github.com/erev0s/VAmPI/pull/42



## Downstream Consumers

- app/api/routes.py



## Decision Rationale

Minor update with clean OSV check and no breaking changes. Flask finding deferred — candidate 2.3.2 introduces new advisory GHSA-68rp-wp8r-4726.


**Completed:** 2026-03-14 16:20


