"""Generic scanner adapter — accepts JSON-direct or SARIF report files."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from vuln_remediation.models import (
    DependencyType,
    Ecosystem,
    Finding,
    Severity,
    StrategyType,
)

logger = logging.getLogger(__name__)

_SEVERITY_MAP: dict[str, Severity] = {
    "critical": Severity.CRITICAL,
    "high": Severity.HIGH,
    "medium": Severity.MEDIUM,
    "low": Severity.LOW,
    "warning": Severity.MEDIUM,
    "error": Severity.HIGH,
    "note": Severity.LOW,
    "none": Severity.LOW,
}

_ECOSYSTEM_MAP: dict[str, Ecosystem] = {
    "npm": Ecosystem.NPM,
    "maven": Ecosystem.MAVEN,
    "docker": Ecosystem.DOCKER,
    "pnpm": Ecosystem.PNPM,
    "yarn": Ecosystem.YARN,
    "gradle": Ecosystem.GRADLE,
}


class GenericAdapter:
    """Load findings from a JSON or SARIF report file.

    Supports two input formats:

    1. **JSON-direct**: A JSON file containing a list of objects that match
       (or can be coerced to) the Finding schema. Fields are mapped
       case-insensitively with camelCase → snake_case conversion.

    2. **SARIF** (Static Analysis Results Interchange Format v2.1.0):
       Standard output format used by many scanners. Each SARIF result is
       mapped to a Finding; rule metadata is merged in for advisory IDs and
       severity.

    Args:
        report_path: Path to the JSON or SARIF report file.
        repository: Repository identifier to stamp on all findings.
        branch: Branch name to stamp on all findings.
        source_system: Label for the originating scanner (default "generic").
    """

    def __init__(
        self,
        report_path: str | Path,
        *,
        repository: str = "",
        branch: str = "main",
        source_system: str = "generic",
    ) -> None:
        self.report_path = Path(report_path)
        self.repository = repository
        self.branch = branch
        self.source_system = source_system

    async def fetch_findings(
        self,
        *,
        severity: list[str] | None = None,
        ecosystem: str | None = None,
    ) -> list[Finding]:
        """Load and filter findings from the report file.

        Args:
            severity: Optional severity filter list.
            ecosystem: Optional ecosystem filter.

        Returns:
            List of normalized Finding records.
        """
        raw = json.loads(self.report_path.read_text())
        findings = self._detect_and_parse(raw)

        if severity:
            sev_set = {s.lower() for s in severity}
            findings = [f for f in findings if f.severity.value in sev_set]

        if ecosystem:
            findings = [f for f in findings if f.ecosystem.value == ecosystem.lower()]

        return findings

    def _detect_and_parse(self, raw: Any) -> list[Finding]:
        """Auto-detect format and delegate to appropriate parser."""
        if isinstance(raw, list):
            return self._parse_json_direct(raw)

        if isinstance(raw, dict):
            # SARIF 2.1.0: top-level "runs" array
            if "runs" in raw and "$schema" in raw:
                return self._parse_sarif(raw)
            # Single finding wrapped in object
            if "findingId" in raw or "finding_id" in raw:
                return self._parse_json_direct([raw])
            # Wrapped list: {"findings": [...]} or {"results": [...]}
            for key in ("findings", "results", "issues", "vulnerabilities"):
                if key in raw and isinstance(raw[key], list):
                    return self._parse_json_direct(raw[key])

        logger.warning("Unrecognized report format — returning empty findings list")
        return []

    # ------------------------------------------------------------------ #
    # JSON-direct parser                                                   #
    # ------------------------------------------------------------------ #

    def _parse_json_direct(self, items: list[dict]) -> list[Finding]:
        findings: list[Finding] = []
        for i, item in enumerate(items):
            try:
                findings.append(self._coerce_finding(item, index=i))
            except Exception as exc:
                logger.warning("Skipping malformed finding at index %d: %s", i, exc)
        return findings

    def _coerce_finding(self, item: dict, *, index: int) -> Finding:
        """Map a dict (with any casing) to a Finding, applying defaults."""
        # Normalize keys: camelCase → snake_case
        d = _normalize_keys(item)

        finding_id = d.get("finding_id") or d.get("id") or f"{self.source_system}-{index}"
        sev_raw = str(d.get("severity", "low")).lower()
        severity = _SEVERITY_MAP.get(sev_raw, Severity.LOW)

        eco_raw = str(d.get("ecosystem", d.get("package_type", "npm"))).lower()
        ecosystem = _ECOSYSTEM_MAP.get(eco_raw, Ecosystem.NPM)

        dep_raw = str(d.get("dependency_type", "direct")).lower()
        dep_type = DependencyType.TRANSITIVE if "trans" in dep_raw else DependencyType.DIRECT

        fix_raw: list[str] = d.get("fix_types_available", d.get("fix_type", []))
        if isinstance(fix_raw, str):
            fix_raw = [fix_raw]
        fix_types = [StrategyType(s) for s in fix_raw if s in StrategyType.__members__.values()]

        candidate_versions: list[str] = d.get(
            "candidate_fixed_versions",
            d.get("fixed_versions", d.get("upgrade_versions", [])),
        )
        if isinstance(candidate_versions, str):
            candidate_versions = [candidate_versions]

        return Finding(
            finding_id=finding_id,
            source_system=d.get("source_system", self.source_system),
            repository=d.get("repository", self.repository),
            branch=d.get("branch", self.branch),
            manifest_path=d.get("manifest_path", d.get("file_path", "")),
            ecosystem=ecosystem,
            package_name=d.get("package_name", d.get("package", "")),
            purl=d.get("purl", ""),
            current_version=d.get("current_version", d.get("version", "")),
            candidate_fixed_versions=candidate_versions,
            dependency_type=dep_type,
            dependency_path=d.get("dependency_path", []),
            severity=severity,
            cvss=_optional_float(d.get("cvss")),
            epss=_optional_float(d.get("epss")),
            exploit_maturity=d.get("exploit_maturity"),
            reachable=d.get("reachable"),
            runtime_exposure=d.get("runtime_exposure"),
            advisory_ids=d.get("advisory_ids", d.get("cve_ids", d.get("advisories", []))),
            scanner_evidence_urls=d.get("scanner_evidence_urls", d.get("evidence_urls", [])),
            introduced_via=d.get("introduced_via"),
            fix_types_available=fix_types,
        )

    # ------------------------------------------------------------------ #
    # SARIF 2.1.0 parser                                                  #
    # ------------------------------------------------------------------ #

    def _parse_sarif(self, sarif: dict) -> list[Finding]:
        findings: list[Finding] = []
        for run in sarif.get("runs", []):
            tool_rules = self._extract_sarif_rules(run)
            for result in run.get("results", []):
                try:
                    findings.append(self._sarif_result_to_finding(result, tool_rules))
                except Exception as exc:
                    logger.warning("Skipping malformed SARIF result: %s", exc)
        return findings

    def _extract_sarif_rules(self, run: dict) -> dict[str, dict]:
        """Build a rule_id → rule_metadata dict from the SARIF run's tool driver."""
        rules: dict[str, dict] = {}
        driver = run.get("tool", {}).get("driver", {})
        for rule in driver.get("rules", []):
            rule_id = rule.get("id", "")
            rules[rule_id] = rule
        return rules

    def _sarif_result_to_finding(self, result: dict, rules: dict[str, dict]) -> Finding:
        """Map a single SARIF result to a Finding."""
        rule_id = result.get("ruleId", "")
        rule = rules.get(rule_id, {})

        # Severity from SARIF level → our Severity enum
        level = result.get("level", "warning").lower()
        severity = _SEVERITY_MAP.get(level, Severity.MEDIUM)

        # Some SARIF emitters put severity in rule properties
        rule_sev = (
            rule.get("properties", {}).get("severity", "") or
            rule.get("properties", {}).get("problem.severity", "")
        )
        if rule_sev:
            severity = _SEVERITY_MAP.get(rule_sev.lower(), severity)

        # Physical location → manifest path
        locations = result.get("locations", [])
        manifest_path = ""
        if locations:
            pl = locations[0].get("physicalLocation", {})
            manifest_path = pl.get("artifactLocation", {}).get("uri", "")

        # Package info from rule properties or result properties
        props = result.get("properties", {}) or {}
        rule_props = rule.get("properties", {}) or {}

        pkg_name = props.get("package") or rule_props.get("package") or ""
        pkg_version = props.get("version") or rule_props.get("version") or ""
        purl = props.get("purl") or rule_props.get("purl") or ""

        eco_raw = props.get("ecosystem") or rule_props.get("ecosystem") or "npm"
        ecosystem = _ECOSYSTEM_MAP.get(eco_raw.lower(), Ecosystem.NPM)

        fixed_versions_raw = (
            props.get("fixedVersions") or props.get("fixed_versions") or
            rule_props.get("fixedVersions") or rule_props.get("fixed_versions") or []
        )
        if isinstance(fixed_versions_raw, str):
            fixed_versions_raw = [fixed_versions_raw]

        advisory_ids: list[str] = []
        # Rule id itself is often an advisory (CVE-XXXX, GHSA-XXXX)
        if rule_id.startswith(("CVE-", "GHSA-", "OSV-", "SNYK-")):
            advisory_ids.append(rule_id)
        # Also check props
        for key in ("advisories", "advisory_ids", "cve"):
            val = props.get(key) or rule_props.get(key)
            if val:
                if isinstance(val, list):
                    advisory_ids.extend(val)
                else:
                    advisory_ids.append(str(val))

        cvss = _optional_float(props.get("cvss") or rule_props.get("cvss"))

        return Finding(
            finding_id=result.get("guid") or f"{rule_id}-{manifest_path}",
            source_system=self.source_system,
            repository=self.repository,
            branch=self.branch,
            manifest_path=manifest_path,
            ecosystem=ecosystem,
            package_name=pkg_name,
            purl=purl,
            current_version=pkg_version,
            candidate_fixed_versions=fixed_versions_raw,
            dependency_type=DependencyType.DIRECT,
            dependency_path=[],
            severity=severity,
            cvss=cvss,
            epss=None,
            exploit_maturity=None,
            reachable=None,
            runtime_exposure=None,
            advisory_ids=list(dict.fromkeys(advisory_ids)),  # deduplicate, preserve order
            scanner_evidence_urls=[],
            introduced_via=None,
            fix_types_available=[],
        )


# ------------------------------------------------------------------ #
# Helpers                                                              #
# ------------------------------------------------------------------ #

def _normalize_keys(d: dict) -> dict:
    """Convert camelCase dict keys to snake_case."""
    import re

    out: dict = {}
    for k, v in d.items():
        snake = re.sub(r"(?<=[a-z0-9])(?=[A-Z])", "_", k).lower()
        out[snake] = v
    return out


def _optional_float(val: Any) -> float | None:
    if val is None:
        return None
    try:
        return float(val)
    except (TypeError, ValueError):
        return None
