## Vulnerability Remediation

### Triggering Findings

- **PyJWT@2.6.0** — HIGH
  - Advisory: GHSA-752w-5fwx-jx9f, CVE-2026-32597
  - Type: direct
  - Path: `requirements.txt`


### Chosen Strategy: UPDATE

**Target version:** 2.12.0
**Confidence:** 92%

Minor version update resolves algorithm confusion vulnerability. OSV/GHSA confirms 2.12.0 is clean. No breaking changes detected in changelog.

### Alternatives Considered

- Update to 2.8.0 (minimum fix) — chosen 2.12.0 for broader advisory coverage



### Breaking Change Analysis

- **Semver delta:** minor





### Candidate Version Safety

- **2.12.0**: Safe



### Validation Evidence

| Check | Result |
|---|---|
| Build | Passed |
| Tests | Passed |
| Re-scan | Clean |
| Execution mode | direct |
| Confidence | 92% |

<details>
<summary>Test output</summary>

```
15 passing, 0 failing
```
</details>

<details>
<summary>Lockfile diff</summary>

```
1 package updated (PyJWT 2.6.0 → 2.12.0)
```
</details>

<details>
<summary>Scan output</summary>

```
No advisories found for PyJWT@2.12.0
```
</details>



### Downstream Consumer Impact

- **app/api/routes.py**



### Rollback

```bash
git revert def789abc012
```

Or manually revert `PyJWT` to `2.6.0`.

