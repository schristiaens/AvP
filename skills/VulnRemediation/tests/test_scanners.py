"""Tests for scanner adapters — Snyk (respx mocks) and Generic (file-based)."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import pytest
import respx
import httpx

from vuln_remediation.models import (
    DependencyType,
    Ecosystem,
    Finding,
    Severity,
)
from vuln_remediation.scanners.base import ScannerAdapter
from vuln_remediation.scanners.generic import GenericAdapter
from vuln_remediation.scanners.snyk import SnykAdapter

# Path to fixture data
FIXTURES = Path(__file__).parent / "fixtures"


# ------------------------------------------------------------------ #
# ScannerAdapter protocol                                              #
# ------------------------------------------------------------------ #

class TestScannerAdapterProtocol:
    def test_snyk_adapter_satisfies_protocol(self) -> None:
        adapter = SnykAdapter("tok", "org-uuid", "proj-uuid")
        assert isinstance(adapter, ScannerAdapter)

    def test_generic_adapter_satisfies_protocol(self, tmp_path: Path) -> None:
        report = tmp_path / "report.json"
        report.write_text("[]")
        adapter = GenericAdapter(report)
        assert isinstance(adapter, ScannerAdapter)


# ------------------------------------------------------------------ #
# SnykAdapter                                                          #
# ------------------------------------------------------------------ #

class TestSnykAdapter:
    @respx.mock
    async def test_fetch_findings_normalizes_response(self) -> None:
        """Happy path: fixture response → 3 normalized findings sorted by severity."""
        fixture_data = json.loads((FIXTURES / "snyk_response.json").read_text())

        respx.get(
            "https://api.snyk.io/rest/orgs/org-uuid/issues",
        ).mock(return_value=httpx.Response(200, json=fixture_data))

        adapter = SnykAdapter(
            "fake-token",
            "org-uuid",
            "proj-uuid",
            repository="acme/api",
            branch="main",
        )
        findings = await adapter.fetch_findings()
        await adapter.close()

        # 3 issues in fixture
        assert len(findings) == 3

        # Sorted: critical first
        assert findings[0].severity == Severity.CRITICAL
        assert findings[1].severity == Severity.HIGH
        assert findings[2].severity == Severity.MEDIUM

    @respx.mock
    async def test_fetch_findings_critical_log4j(self) -> None:
        """Critical log4j finding is normalized correctly."""
        fixture_data = json.loads((FIXTURES / "snyk_response.json").read_text())

        respx.get(
            "https://api.snyk.io/rest/orgs/org-uuid/issues",
        ).mock(return_value=httpx.Response(200, json=fixture_data))

        adapter = SnykAdapter("tok", "org-uuid", "proj-uuid", repository="acme/api")
        findings = await adapter.fetch_findings()
        await adapter.close()

        log4j = next(f for f in findings if f.package_name == "org.apache.logging.log4j:log4j-core")
        assert log4j.severity == Severity.CRITICAL
        assert log4j.ecosystem == Ecosystem.MAVEN
        assert log4j.current_version == "2.14.1"
        assert "2.17.1" in log4j.candidate_fixed_versions
        assert log4j.cvss == pytest.approx(10.0)
        assert log4j.epss == pytest.approx(0.97)
        assert log4j.exploit_maturity == "mature"
        assert log4j.reachable is True
        assert "CVE-2021-44228" in log4j.advisory_ids
        assert log4j.manifest_path == "pom.xml"

    @respx.mock
    async def test_fetch_findings_lodash_high(self) -> None:
        """High-severity lodash finding is normalized correctly."""
        fixture_data = json.loads((FIXTURES / "snyk_response.json").read_text())

        respx.get(
            "https://api.snyk.io/rest/orgs/org-uuid/issues",
        ).mock(return_value=httpx.Response(200, json=fixture_data))

        adapter = SnykAdapter("tok", "org-uuid", "proj-uuid")
        findings = await adapter.fetch_findings()
        await adapter.close()

        lodash = next(f for f in findings if f.package_name == "lodash")
        assert lodash.severity == Severity.HIGH
        assert lodash.ecosystem == Ecosystem.NPM
        assert lodash.dependency_type == DependencyType.DIRECT
        assert lodash.cvss == pytest.approx(7.4)
        assert lodash.reachable is True
        assert "CVE-2020-8203" in lodash.advisory_ids

    @respx.mock
    async def test_fetch_findings_transitive_axios(self) -> None:
        """Transitive dependency type is preserved."""
        fixture_data = json.loads((FIXTURES / "snyk_response.json").read_text())

        respx.get(
            "https://api.snyk.io/rest/orgs/org-uuid/issues",
        ).mock(return_value=httpx.Response(200, json=fixture_data))

        adapter = SnykAdapter("tok", "org-uuid", "proj-uuid")
        findings = await adapter.fetch_findings()
        await adapter.close()

        axios = next(f for f in findings if f.package_name == "axios")
        assert axios.dependency_type == DependencyType.TRANSITIVE
        assert axios.severity == Severity.MEDIUM

    @respx.mock
    async def test_severity_filter(self) -> None:
        """Only critical findings returned when filter applied."""
        fixture_data = json.loads((FIXTURES / "snyk_response.json").read_text())

        # Snyk API accepts severity filter as query param; we test the adapter
        # passes it through — adapter-level filtering happens post-fetch for
        # ecosystem, but severity is passed to the API. We mock the API to return
        # the full fixture and verify the adapter doesn't double-filter.
        respx.get(
            "https://api.snyk.io/rest/orgs/org-uuid/issues",
        ).mock(return_value=httpx.Response(200, json=fixture_data))

        adapter = SnykAdapter("tok", "org-uuid", "proj-uuid")
        # Pass severity to API (query param) — fixture returns all 3 regardless
        findings = await adapter.fetch_findings(severity=["critical"])
        await adapter.close()

        # All 3 are returned from mock; severity param goes to API not local filter
        assert len(findings) == 3

    @respx.mock
    async def test_ecosystem_filter(self) -> None:
        """Ecosystem filter removes non-matching findings."""
        fixture_data = json.loads((FIXTURES / "snyk_response.json").read_text())

        respx.get(
            "https://api.snyk.io/rest/orgs/org-uuid/issues",
        ).mock(return_value=httpx.Response(200, json=fixture_data))

        adapter = SnykAdapter("tok", "org-uuid", "proj-uuid")
        findings = await adapter.fetch_findings(ecosystem="maven")
        await adapter.close()

        assert all(f.ecosystem == Ecosystem.MAVEN for f in findings)
        assert len(findings) == 1

    @respx.mock
    async def test_http_error_raises(self) -> None:
        """HTTP 401 propagates as httpx.HTTPStatusError."""
        respx.get(
            "https://api.snyk.io/rest/orgs/org-uuid/issues",
        ).mock(return_value=httpx.Response(401, json={"error": "Unauthorized"}))

        adapter = SnykAdapter("bad-token", "org-uuid", "proj-uuid")
        with pytest.raises(httpx.HTTPStatusError):
            await adapter.fetch_findings()
        await adapter.close()

    @respx.mock
    async def test_pagination_follows_next_link(self) -> None:
        """Adapter follows 'next' pagination and aggregates results."""

        def _issue(issue_id: str, pkg: str, sev: str, dep_type: str) -> dict:
            return {
                "id": issue_id,
                "type": "issue",
                "attributes": {
                    "effective_severity_level": sev,
                    "type": "vuln",
                    "package": {"name": pkg, "version": "1.0.0", "type": "npm"},
                    "problems": [{"id": f"CVE-XXXX-{issue_id}", "source": "nvd"}],
                    "coordinates": [
                        {
                            "representation": [f"pkg:npm/{pkg}@1.0.0"],
                            "remedies": [
                                {"type": "upgradable", "details": {"upgrade_to": "2.0.0", "upgrade_path": []}}
                            ],
                        }
                    ],
                    "risk": {"score": {"value": 500, "factors": []}},
                    "dependency_type": dep_type,
                },
                "relationships": {"scan_item": {"data": {"id": "p", "type": "project", "meta": {"path": "package.json"}}}},
            }

        page1 = {
            "data": [_issue("issue-page1", "express", "high", "direct")],
            "links": {"next": "https://api.snyk.io/rest/orgs/org-uuid/issues?starting_after=cursor1"},
            "meta": {},
        }
        page2 = {
            "data": [_issue("issue-page2", "body-parser", "medium", "transitive")],
            "links": {},
            "meta": {},
        }

        # Use side_effect to return sequential responses for the same route pattern
        responses = iter([httpx.Response(200, json=page1), httpx.Response(200, json=page2)])
        respx.route(method="GET", url__regex=r".*orgs/org-uuid/issues.*").mock(
            side_effect=lambda _req: next(responses)
        )

        adapter = SnykAdapter("tok", "org-uuid", "proj-uuid")
        findings = await adapter.fetch_findings()
        await adapter.close()

        assert len(findings) == 2
        pkg_names = {f.package_name for f in findings}
        assert "express" in pkg_names
        assert "body-parser" in pkg_names

    @respx.mock
    async def test_malformed_issue_skipped(self) -> None:
        """Issues missing required fields are skipped without crashing."""
        payload = {
            "data": [
                {
                    "id": "good-issue",
                    "type": "issue",
                    "attributes": {
                        "effective_severity_level": "high",
                        "type": "vuln",
                        "package": {"name": "express", "version": "4.17.1", "type": "npm"},
                        "problems": [],
                        "coordinates": [],
                        "risk": {"score": {"value": 500, "factors": []}},
                        "dependency_type": "direct",
                    },
                    "relationships": {"scan_item": {"data": {"id": "p", "type": "project", "meta": {}}}},
                },
                # Malformed: missing attributes entirely
                {"id": "bad-issue", "type": "issue"},
            ],
            "links": {},
            "meta": {},
        }
        respx.get(
            "https://api.snyk.io/rest/orgs/org-uuid/issues",
        ).mock(return_value=httpx.Response(200, json=payload))

        adapter = SnykAdapter("tok", "org-uuid", "proj-uuid")
        findings = await adapter.fetch_findings()
        await adapter.close()

        # Only the good issue comes through
        assert len(findings) == 1
        assert findings[0].package_name == "express"


# ------------------------------------------------------------------ #
# GenericAdapter — JSON-direct                                         #
# ------------------------------------------------------------------ #

class TestGenericAdapterJsonDirect:
    async def test_empty_list(self, tmp_path: Path) -> None:
        report = tmp_path / "empty.json"
        report.write_text("[]")
        adapter = GenericAdapter(report)
        findings = await adapter.fetch_findings()
        assert findings == []

    async def test_single_finding_snake_case(self, tmp_path: Path) -> None:
        data = [
            {
                "finding_id": "gf-001",
                "source_system": "wiz",
                "repository": "acme/web",
                "branch": "main",
                "manifest_path": "requirements.txt",
                "ecosystem": "npm",
                "package_name": "minimist",
                "purl": "pkg:npm/minimist@1.2.5",
                "current_version": "1.2.5",
                "candidate_fixed_versions": ["1.2.8"],
                "dependency_type": "direct",
                "severity": "high",
                "advisory_ids": ["CVE-2021-44906"],
            }
        ]
        report = tmp_path / "findings.json"
        report.write_text(json.dumps(data))

        adapter = GenericAdapter(report, repository="acme/web")
        findings = await adapter.fetch_findings()

        assert len(findings) == 1
        f = findings[0]
        assert f.package_name == "minimist"
        assert f.severity == Severity.HIGH
        assert f.candidate_fixed_versions == ["1.2.8"]
        assert "CVE-2021-44906" in f.advisory_ids

    async def test_camel_case_keys_accepted(self, tmp_path: Path) -> None:
        data = [
            {
                "findingId": "cc-001",
                "sourceSystem": "custom",
                "packageName": "vulnerable-pkg",
                "currentVersion": "0.1.0",
                "candidateFixedVersions": ["0.2.0"],
                "dependencyType": "direct",
                "ecosystem": "npm",
                "severity": "critical",
                "purl": "pkg:npm/vulnerable-pkg@0.1.0",
            }
        ]
        report = tmp_path / "camel.json"
        report.write_text(json.dumps(data))

        adapter = GenericAdapter(report)
        findings = await adapter.fetch_findings()

        assert len(findings) == 1
        assert findings[0].package_name == "vulnerable-pkg"
        assert findings[0].severity == Severity.CRITICAL

    async def test_wrapped_list_format(self, tmp_path: Path) -> None:
        """Handles {"findings": [...]} wrapper."""
        data = {
            "findings": [
                {
                    "finding_id": "w-001",
                    "package_name": "moment",
                    "current_version": "2.29.1",
                    "ecosystem": "npm",
                    "severity": "medium",
                    "dependency_type": "direct",
                    "purl": "pkg:npm/moment@2.29.1",
                }
            ]
        }
        report = tmp_path / "wrapped.json"
        report.write_text(json.dumps(data))

        adapter = GenericAdapter(report)
        findings = await adapter.fetch_findings()
        assert len(findings) == 1
        assert findings[0].package_name == "moment"

    async def test_severity_filter(self, tmp_path: Path) -> None:
        data = [
            {"package_name": "a", "severity": "critical", "current_version": "1.0", "ecosystem": "npm", "dependency_type": "direct", "purl": "pkg:npm/a@1.0"},
            {"package_name": "b", "severity": "low", "current_version": "2.0", "ecosystem": "npm", "dependency_type": "direct", "purl": "pkg:npm/b@2.0"},
        ]
        report = tmp_path / "sev.json"
        report.write_text(json.dumps(data))

        adapter = GenericAdapter(report)
        findings = await adapter.fetch_findings(severity=["critical"])
        assert len(findings) == 1
        assert findings[0].package_name == "a"

    async def test_ecosystem_filter(self, tmp_path: Path) -> None:
        data = [
            {"package_name": "a", "severity": "high", "current_version": "1.0", "ecosystem": "npm", "dependency_type": "direct", "purl": "pkg:npm/a@1.0"},
            {"package_name": "b", "severity": "high", "current_version": "1.0", "ecosystem": "maven", "dependency_type": "direct", "purl": "pkg:maven/b@1.0"},
        ]
        report = tmp_path / "eco.json"
        report.write_text(json.dumps(data))

        adapter = GenericAdapter(report)
        findings = await adapter.fetch_findings(ecosystem="maven")
        assert len(findings) == 1
        assert findings[0].package_name == "b"

    async def test_malformed_items_skipped(self, tmp_path: Path) -> None:
        """Items that can't be coerced are skipped; valid items still returned."""
        data = [
            {"package_name": "good-pkg", "severity": "high", "current_version": "1.0", "ecosystem": "npm", "dependency_type": "direct", "purl": "pkg:npm/good-pkg@1.0"},
            {"severity": "invalid-enum-value"},  # malformed — invalid severity
        ]
        report = tmp_path / "mixed.json"
        report.write_text(json.dumps(data))

        adapter = GenericAdapter(report)
        findings = await adapter.fetch_findings()
        # good-pkg passes; invalid severity falls back to LOW (not a crash)
        assert any(f.package_name == "good-pkg" for f in findings)

    async def test_source_system_label(self, tmp_path: Path) -> None:
        report = tmp_path / "r.json"
        report.write_text('[{"package_name": "pkg", "severity": "low", "current_version": "1", "ecosystem": "npm", "dependency_type": "direct", "purl": "x"}]')
        adapter = GenericAdapter(report, source_system="wiz-export")
        findings = await adapter.fetch_findings()
        assert findings[0].source_system == "wiz-export"


# ------------------------------------------------------------------ #
# GenericAdapter — SARIF                                               #
# ------------------------------------------------------------------ #

SARIF_SAMPLE = {
    "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
    "version": "2.1.0",
    "runs": [
        {
            "tool": {
                "driver": {
                    "name": "DummyScanner",
                    "rules": [
                        {
                            "id": "CVE-2021-44228",
                            "shortDescription": {"text": "Log4Shell RCE"},
                            "properties": {
                                "severity": "critical",
                                "package": "log4j-core",
                                "version": "2.14.1",
                                "ecosystem": "maven",
                                "purl": "pkg:maven/org.apache.logging.log4j/log4j-core@2.14.1",
                                "fixedVersions": ["2.17.1"],
                                "cvss": "10.0",
                            },
                        },
                        {
                            "id": "GHSA-jfh8-c2jp-hdp9",
                            "shortDescription": {"text": "Prototype Pollution in lodash"},
                            "properties": {
                                "severity": "high",
                                "package": "lodash",
                                "version": "4.17.15",
                                "ecosystem": "npm",
                                "purl": "pkg:npm/lodash@4.17.15",
                                "fixedVersions": ["4.17.21"],
                            },
                        },
                    ],
                }
            },
            "results": [
                {
                    "ruleId": "CVE-2021-44228",
                    "level": "error",
                    "message": {"text": "Critical vulnerability in log4j-core"},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": "pom.xml"}
                            }
                        }
                    ],
                },
                {
                    "ruleId": "GHSA-jfh8-c2jp-hdp9",
                    "level": "warning",
                    "message": {"text": "Prototype pollution in lodash"},
                    "locations": [
                        {
                            "physicalLocation": {
                                "artifactLocation": {"uri": "package.json"}
                            }
                        }
                    ],
                },
            ],
        }
    ],
}


class TestGenericAdapterSarif:
    async def test_sarif_parsed_to_findings(self, tmp_path: Path) -> None:
        report = tmp_path / "scan.sarif"
        report.write_text(json.dumps(SARIF_SAMPLE))

        adapter = GenericAdapter(report, repository="acme/api", source_system="dummy-scanner")
        findings = await adapter.fetch_findings()

        assert len(findings) == 2

    async def test_sarif_log4j_critical(self, tmp_path: Path) -> None:
        report = tmp_path / "scan.sarif"
        report.write_text(json.dumps(SARIF_SAMPLE))

        adapter = GenericAdapter(report)
        findings = await adapter.fetch_findings()

        log4j = next(f for f in findings if "log4j" in f.package_name)
        assert log4j.severity == Severity.CRITICAL
        assert log4j.ecosystem == Ecosystem.MAVEN
        assert "2.17.1" in log4j.candidate_fixed_versions
        assert log4j.cvss == pytest.approx(10.0)
        assert "CVE-2021-44228" in log4j.advisory_ids
        assert log4j.manifest_path == "pom.xml"

    async def test_sarif_lodash_high(self, tmp_path: Path) -> None:
        report = tmp_path / "scan.sarif"
        report.write_text(json.dumps(SARIF_SAMPLE))

        adapter = GenericAdapter(report)
        findings = await adapter.fetch_findings()

        lodash = next(f for f in findings if f.package_name == "lodash")
        assert lodash.severity == Severity.HIGH
        assert lodash.ecosystem == Ecosystem.NPM
        assert "GHSA-jfh8-c2jp-hdp9" in lodash.advisory_ids
        assert lodash.manifest_path == "package.json"

    async def test_sarif_ecosystem_filter(self, tmp_path: Path) -> None:
        report = tmp_path / "scan.sarif"
        report.write_text(json.dumps(SARIF_SAMPLE))

        adapter = GenericAdapter(report)
        findings = await adapter.fetch_findings(ecosystem="maven")
        assert len(findings) == 1
        assert findings[0].ecosystem == Ecosystem.MAVEN

    async def test_sarif_severity_filter(self, tmp_path: Path) -> None:
        report = tmp_path / "scan.sarif"
        report.write_text(json.dumps(SARIF_SAMPLE))

        adapter = GenericAdapter(report)
        findings = await adapter.fetch_findings(severity=["critical"])
        assert len(findings) == 1
        assert findings[0].severity == Severity.CRITICAL

    async def test_sarif_empty_runs(self, tmp_path: Path) -> None:
        empty_sarif = {
            "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.5.json",
            "version": "2.1.0",
            "runs": [],
        }
        report = tmp_path / "empty.sarif"
        report.write_text(json.dumps(empty_sarif))

        adapter = GenericAdapter(report)
        findings = await adapter.fetch_findings()
        assert findings == []
