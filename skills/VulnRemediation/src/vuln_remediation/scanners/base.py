"""ScannerAdapter protocol — all scanner adapters implement this interface."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from vuln_remediation.models import Finding


@runtime_checkable
class ScannerAdapter(Protocol):
    """All scanner adapters implement this interface."""

    async def fetch_findings(
        self,
        *,
        severity: list[str] | None = None,
        ecosystem: str | None = None,
    ) -> list[Finding]:
        """Fetch and normalize findings from the scanner.

        Args:
            severity: Optional list of severity levels to filter by (e.g. ["high", "critical"]).
            ecosystem: Optional ecosystem filter (e.g. "npm", "maven").

        Returns:
            List of normalized Finding records.
        """
        ...
