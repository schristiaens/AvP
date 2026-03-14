"""Snyk Issues API v1 adapter — fetches and normalizes vulnerability findings."""

from __future__ import annotations

import logging
from typing import Any
from urllib.parse import urlencode

import httpx

from vuln_remediation.models import (
    DependencyType,
    Ecosystem,
    Finding,
    Severity,
    StrategyType,
)

logger = logging.getLogger(__name__)

# Snyk REST API version header required for v1 REST endpoints
_API_VERSION = "2024-10-15"

_SEVERITY_MAP: dict[str, Severity] = {
    "critical": Severity.CRITICAL,
    "high": Severity.HIGH,
    "medium": Severity.MEDIUM,
    "low": Severity.LOW,
}

_ECOSYSTEM_MAP: dict[str, Ecosystem] = {
    "npm": Ecosystem.NPM,
    "maven": Ecosystem.MAVEN,
    "docker": Ecosystem.DOCKER,
    "pnpm": Ecosystem.PNPM,
    "yarn": Ecosystem.YARN,
    "gradle": Ecosystem.GRADLE,
    "pip": Ecosystem.NPM,  # fallback — extend as needed
}

_DEP_TYPE_MAP: dict[str, DependencyType] = {
    "direct": DependencyType.DIRECT,
    "transitive": DependencyType.TRANSITIVE,
    "indirect": DependencyType.TRANSITIVE,
    "base_image": DependencyType.BASE_IMAGE,
}

_FIX_TYPE_MAP: dict[str, StrategyType] = {
    "upgradable": StrategyType.UPDATE,
    "patchable": StrategyType.PATCH,
    "pinnable": StrategyType.UPDATE,
}


class SnykAdapter:
    """Fetch and normalize findings from the Snyk Issues API.

    Uses the Snyk REST API (api.snyk.io/rest) with paginated listing of
    project issues. Normalizes each issue into the canonical Finding model.

    Args:
        token: Snyk API token (SNYK_TOKEN).
        org_id: Snyk organization UUID.
        project_id: Snyk project UUID.
        repository: Repository identifier for the finding (e.g. "owner/repo").
        branch: Branch the project snapshot was taken from.
    """

    BASE_URL = "https://api.snyk.io/rest"

    def __init__(
        self,
        token: str,
        org_id: str,
        project_id: str,
        *,
        repository: str = "",
        branch: str = "main",
    ) -> None:
        self.org_id = org_id
        self.project_id = project_id
        self.repository = repository
        self.branch = branch
        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"token {token}",
                "Content-Type": "application/vnd.api+json",
            },
            timeout=30.0,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> SnykAdapter:
        return self

    async def __aexit__(self, *args: Any) -> None:
        await self.close()

    async def fetch_findings(
        self,
        *,
        severity: list[str] | None = None,
        ecosystem: str | None = None,
    ) -> list[Finding]:
        """Fetch all open issues for the configured project.

        Args:
            severity: Severity levels to include. Defaults to all levels.
            ecosystem: Ecosystem filter (matched against package type).

        Returns:
            List of normalized Finding records sorted by severity (critical first).
        """
        issues = await self._paginate_issues(severity=severity)
        findings: list[Finding] = []

        for issue in issues:
            try:
                finding = self._normalize(issue)
            except Exception:
                logger.warning("Skipping malformed Snyk issue: %s", issue.get("id", "unknown"))
                continue

            if ecosystem and finding.ecosystem.value != ecosystem:
                continue

            findings.append(finding)

        # Sort critical → high → medium → low
        severity_order = {
            Severity.CRITICAL: 0,
            Severity.HIGH: 1,
            Severity.MEDIUM: 2,
            Severity.LOW: 3,
        }
        findings.sort(key=lambda f: severity_order.get(f.severity, 99))
        return findings

    async def _paginate_issues(
        self,
        *,
        severity: list[str] | None = None,
    ) -> list[dict]:
        """Fetch all pages of issues from the Snyk REST API."""
        params: dict[str, Any] = {
            "version": _API_VERSION,
            "limit": 100,
            "status": "open",
            "type": "vuln",
        }
        if severity:
            params["effective_severity_level"] = ",".join(severity)

        issues: list[dict] = []
        path = f"/orgs/{self.org_id}/issues"
        # Project-scoped filter via query param
        params["project_id"] = self.project_id

        while True:
            resp = await self._client.get(path, params=params)
            resp.raise_for_status()
            body = resp.json()

            for item in body.get("data", []):
                issues.append(item)

            # Follow pagination cursor
            next_cursor = (
                body.get("links", {}).get("next") or
                body.get("meta", {}).get("next_cursor")
            )
            if not next_cursor:
                break

            # next may be a full URL or just a cursor value
            if next_cursor.startswith("http"):
                # Strip base URL and use as path
                path = next_cursor.replace(self.BASE_URL, "")
                params = {}
            else:
                params["starting_after"] = next_cursor

        return issues

    def _normalize(self, issue: dict) -> Finding:
        """Normalize a raw Snyk REST API issue dict into a Finding."""
        attrs = issue.get("attributes", {})
        relationships = issue.get("relationships", {})

        # --- IDs and source ---
        finding_id = issue.get("id", "")
        if not attrs:
            raise ValueError(f"Issue {finding_id!r} has no attributes")
        pkg_meta = attrs.get("package", {})
        pkg_name = pkg_meta.get("name", "")
        pkg_version = pkg_meta.get("version", "")
        pkg_type = pkg_meta.get("type", "").lower()

        # --- Advisory IDs ---
        problems = attrs.get("problems", [])
        advisory_ids = [p.get("id", "") for p in problems if p.get("id")]

        # --- Severity ---
        sev_raw = attrs.get("effective_severity_level", "low").lower()
        severity = _SEVERITY_MAP.get(sev_raw, Severity.LOW)

        # --- Ecosystem ---
        ecosystem = _ECOSYSTEM_MAP.get(pkg_type, Ecosystem.NPM)

        # --- Coordinates (may be empty list) ---
        coords = attrs.get("coordinates") or []
        first_coord = coords[0] if coords else {}

        # --- PURL ---
        representations = first_coord.get("representation") or []
        purl = (representations[0] if representations else None) or (
            f"pkg:{ecosystem.value}/{pkg_name}@{pkg_version}"
        )

        # --- Dependency type ---
        dep_raw = attrs.get("dependency_type", "direct").lower()
        dep_type = _DEP_TYPE_MAP.get(dep_raw, DependencyType.DIRECT)

        # --- Dependency path ---
        dep_path: list[str] = []
        if first_coord.get("remedies"):
            # Extract upgrade path from first remedy
            dep_path = first_coord["remedies"][0].get("details", {}).get("upgrade_path", [])

        # --- Candidate fixed versions ---
        fixed_versions: list[str] = []
        fix_types: list[StrategyType] = []
        for coord in coords or []:
            for remedy in coord.get("remedies", []):
                details = remedy.get("details", {})
                target = details.get("upgrade_to") or details.get("target_version")
                if target and target not in fixed_versions:
                    fixed_versions.append(target)
                fix_type_raw = remedy.get("type", "").lower()
                ft = _FIX_TYPE_MAP.get(fix_type_raw)
                if ft and ft not in fix_types:
                    fix_types.append(ft)

        # --- CVSS / EPSS / exploit maturity ---
        risk = attrs.get("risk", {})
        cvss_score: float | None = None
        factors = risk.get("score", {}).get("factors", [])
        for factor in factors:
            if factor.get("name") == "cvssScore":
                try:
                    cvss_score = float(factor["value"])
                except (KeyError, TypeError, ValueError):
                    pass

        epss: float | None = None
        for factor in factors:
            if factor.get("name") == "epss":
                try:
                    epss = float(factor["value"])
                except (KeyError, TypeError, ValueError):
                    pass

        exploit_maturity: str | None = None
        for factor in factors:
            if factor.get("name") == "exploitMaturity":
                exploit_maturity = factor.get("value")

        # --- Reachability ---
        reachable: bool | None = None
        reachability_raw = attrs.get("reachable")
        if reachability_raw is not None:
            reachable = str(reachability_raw).lower() in ("reachable", "true", "yes")

        # --- Manifest path ---
        manifest_path = ""
        project_rel = relationships.get("scan_item", {}).get("data", {})
        # Snyk sometimes surfaces the file path under scan_item meta
        manifest_path = project_rel.get("meta", {}).get("path", "") or ""

        # Evidence URLs
        evidence_urls: list[str] = []
        for problem in problems:
            url = problem.get("url") or problem.get("source")
            if url:
                evidence_urls.append(url)

        # Introduced via
        introduced_via: str | None = None
        if dep_path:
            introduced_via = dep_path[0] if dep_path else None

        return Finding(
            finding_id=finding_id,
            source_system="snyk",
            repository=self.repository,
            branch=self.branch,
            manifest_path=manifest_path,
            ecosystem=ecosystem,
            package_name=pkg_name,
            purl=purl,
            current_version=pkg_version,
            candidate_fixed_versions=fixed_versions,
            dependency_type=dep_type,
            dependency_path=dep_path,
            severity=severity,
            cvss=cvss_score,
            epss=epss,
            exploit_maturity=exploit_maturity,
            reachable=reachable,
            runtime_exposure=None,
            advisory_ids=advisory_ids,
            scanner_evidence_urls=evidence_urls,
            introduced_via=introduced_via,
            fix_types_available=fix_types,
        )
