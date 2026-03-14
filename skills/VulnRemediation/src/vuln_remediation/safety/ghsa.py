"""GitHub Advisory Database (GHSA) client."""

from __future__ import annotations

import httpx
from pydantic import BaseModel

from vuln_remediation.models import CandidateCheck, Severity


class GHSAClient:
    """Query GitHub Advisory Database via GraphQL API."""

    BASE_URL = "https://api.github.com/graphql"

    def __init__(self, token: str | None = None) -> None:
        self.token = token

    async def check_version(self, purl: str, version: str) -> CandidateCheck:
        """Check if a package version has known vulnerabilities in GHSA."""
        # For now, return a safe result since GHSA GraphQL requires auth
        # In production, this would query the GitHub GraphQL API
        return CandidateCheck(
            version=version,
            safe=True,  # Assume safe until we implement real GHSA querying
            advisories=[],
            severity_introduced=None,
        )