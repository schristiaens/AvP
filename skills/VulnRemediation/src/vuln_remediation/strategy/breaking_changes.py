"""Breaking change analysis."""

from __future__ import annotations

from vuln_remediation.models import BreakingChangeSignal


class BreakingChangeAnalyzer:
    """Analyze potential breaking changes in version updates."""

    async def analyze(
        self,
        package_name: str,
        from_version: str,
        to_version: str,
    ) -> BreakingChangeSignal:
        """Analyze breaking changes between versions."""
        # For now, return empty analysis
        # In production, this would analyze changelogs, APIs, etc.
        return BreakingChangeSignal(
            semver_delta="minor",  # Assume minor by default
            changelog_url=None,
            breaking_changes=[],
            deprecations=[],
            api_changes=[],
        )