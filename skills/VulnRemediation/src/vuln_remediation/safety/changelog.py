"""Changelog and breaking change analysis."""

from __future__ import annotations

import httpx
from packaging.version import Version

from vuln_remediation.models import BreakingChangeSignal


class ChangelogFetcher:
    """Fetch release notes and extract breaking change signals."""

    async def fetch(
        self,
        package_name: str,
        from_version: str,
        to_version: str,
        ecosystem: str = "npm",
    ) -> BreakingChangeSignal:
        """Fetch changelog between versions and analyze breaking changes."""
        from_ver, to_ver = Version(from_version), Version(to_version)

        # Determine semver delta
        if to_ver.major > from_ver.major:
            delta = "major"
        elif to_ver.minor > from_ver.minor:
            delta = "minor"
        else:
            delta = "patch"

        # For now, return a basic signal
        # In production, this would fetch actual changelogs from registries
        return BreakingChangeSignal(
            semver_delta=delta,
            changelog_url=f"https://www.npmjs.com/package/{package_name}/v/{to_version}",
            breaking_changes=[],
            deprecations=[],
            api_changes=[],
        )