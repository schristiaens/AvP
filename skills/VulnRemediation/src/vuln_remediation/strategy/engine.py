"""Strategy selection engine."""

from __future__ import annotations

from vuln_remediation.models import Finding, StrategyRecommendation, StrategyType


class StrategyEngine:
    """Select the best remediation strategy for a vulnerability."""

    async def select_strategy(self, finding: Finding) -> StrategyRecommendation:
        """Analyze finding and recommend remediation strategy."""
        # Simple logic: prefer update if available, otherwise patch
        if finding.candidate_fixed_versions:
            strategy = StrategyType.UPDATE
            target_version = finding.candidate_fixed_versions[0]
        else:
            strategy = StrategyType.PATCH
            target_version = None

        return StrategyRecommendation(
            finding=finding,
            recommended_strategy=strategy,
            target_version=target_version,
            confidence=0.8,
            rationale=f"Selected {strategy.value} strategy based on available fixes",
            breaking_change_signals=None,
            candidate_checks=[],
            alternatives_considered=["mitigate", "replace"],
        )