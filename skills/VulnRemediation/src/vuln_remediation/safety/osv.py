"""OSV.dev vulnerability database client."""

from __future__ import annotations

import httpx
from pydantic import BaseModel

from vuln_remediation.models import CandidateCheck, Severity


class OSVClient:
    """Query OSV.dev for known vulnerabilities in a package version."""

    BASE_URL = "https://api.osv.dev/v1"

    async def check_version(self, purl: str, version: str) -> CandidateCheck:
        """Check if a package version has known vulnerabilities."""
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{self.BASE_URL}/query",
                json={"package": {"purl": purl}, "version": version},
            )
            resp.raise_for_status()
            data = resp.json()

            advisories = [v["id"] for v in data.get("vulns", [])]
            safe = len(advisories) == 0

            # Extract severity if available (simplified for now)
            severity_introduced = None

            return CandidateCheck(
                version=version,
                safe=safe,
                advisories=advisories,
                severity_introduced=severity_introduced,
            )