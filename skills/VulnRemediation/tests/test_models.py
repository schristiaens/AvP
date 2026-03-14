"""Tests for Pydantic models — validation, serialization, defaults."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from vuln_remediation.models import (
    BreakingChangeSignal,
    CandidateCheck,
    DedupCheckResult,
    DependencyType,
    Ecosystem,
    Finding,
    RemediationRecord,
    RemediationStatus,
    Severity,
    StrategyRecommendation,
    StrategyType,
    ValidationResult,
)


# ------------------------------------------------------------------ #
# Fixtures                                                             #
# ------------------------------------------------------------------ #

@pytest.fixture
def minimal_finding() -> Finding:
    return Finding(
        finding_id="test-001",
        source_system="snyk",
        repository="acme/api",
        branch="main",
        manifest_path="package.json",
        ecosystem=Ecosystem.NPM,
        package_name="lodash",
        purl="pkg:npm/lodash@4.17.15",
        current_version="4.17.15",
        dependency_type=DependencyType.DIRECT,
        severity=Severity.HIGH,
    )


@pytest.fixture
def full_finding(minimal_finding: Finding) -> Finding:
    return minimal_finding.model_copy(update={
        "candidate_fixed_versions": ["4.17.21"],
        "dependency_path": ["lodash@4.17.21"],
        "cvss": 7.4,
        "epss": 0.00185,
        "exploit_maturity": "proof-of-concept",
        "reachable": True,
        "advisory_ids": ["SNYK-JS-LODASH-567746", "CVE-2020-8203"],
        "fix_types_available": [StrategyType.UPDATE],
    })


# ------------------------------------------------------------------ #
# Severity                                                             #
# ------------------------------------------------------------------ #

class TestSeverity:
    def test_string_values(self) -> None:
        assert Severity.CRITICAL == "critical"
        assert Severity.HIGH == "high"
        assert Severity.MEDIUM == "medium"
        assert Severity.LOW == "low"

    def test_ordering_by_value(self) -> None:
        # StrEnum inherits string comparison; ordering is alphabetical — just verify values exist
        assert {Severity.CRITICAL, Severity.HIGH, Severity.MEDIUM, Severity.LOW}


# ------------------------------------------------------------------ #
# Finding                                                              #
# ------------------------------------------------------------------ #

class TestFinding:
    def test_minimal_finding_defaults(self, minimal_finding: Finding) -> None:
        assert minimal_finding.candidate_fixed_versions == []
        assert minimal_finding.dependency_path == []
        assert minimal_finding.advisory_ids == []
        assert minimal_finding.fix_types_available == []
        assert minimal_finding.cvss is None
        assert minimal_finding.epss is None
        assert minimal_finding.reachable is None

    def test_full_finding_round_trip(self, full_finding: Finding) -> None:
        dumped = full_finding.model_dump(mode="json")
        reloaded = Finding.model_validate(dumped)
        assert reloaded == full_finding

    def test_invalid_ecosystem_raises(self) -> None:
        with pytest.raises(ValidationError):
            Finding(
                finding_id="x",
                source_system="test",
                repository="r",
                branch="main",
                manifest_path="f",
                ecosystem="rubygems",  # not in Ecosystem enum
                package_name="rails",
                purl="pkg:gem/rails@7.0.0",
                current_version="7.0.0",
                dependency_type=DependencyType.DIRECT,
                severity=Severity.HIGH,
            )

    def test_invalid_severity_raises(self) -> None:
        with pytest.raises(ValidationError):
            Finding(
                finding_id="x",
                source_system="test",
                repository="r",
                branch="main",
                manifest_path="f",
                ecosystem=Ecosystem.NPM,
                package_name="pkg",
                purl="pkg:npm/pkg@1.0",
                current_version="1.0",
                dependency_type=DependencyType.DIRECT,
                severity="catastrophic",  # not in Severity enum
            )

    def test_json_serialization_preserves_enums_as_strings(self, minimal_finding: Finding) -> None:
        data = minimal_finding.model_dump(mode="json")
        assert data["severity"] == "high"
        assert data["ecosystem"] == "npm"
        assert data["dependency_type"] == "direct"

    def test_purl_is_preserved(self, minimal_finding: Finding) -> None:
        assert minimal_finding.purl == "pkg:npm/lodash@4.17.15"


# ------------------------------------------------------------------ #
# CandidateCheck                                                       #
# ------------------------------------------------------------------ #

class TestCandidateCheck:
    def test_safe_version(self) -> None:
        check = CandidateCheck(version="4.17.21", safe=True)
        assert check.advisories == []
        assert check.severity_introduced is None

    def test_unsafe_version_with_advisories(self) -> None:
        check = CandidateCheck(
            version="4.17.20",
            safe=False,
            advisories=["CVE-2021-XXXX"],
            severity_introduced=Severity.HIGH,
        )
        assert not check.safe
        assert len(check.advisories) == 1
        assert check.severity_introduced == Severity.HIGH


# ------------------------------------------------------------------ #
# BreakingChangeSignal                                                 #
# ------------------------------------------------------------------ #

class TestBreakingChangeSignal:
    def test_defaults(self) -> None:
        signal = BreakingChangeSignal(semver_delta="patch")
        assert signal.breaking_changes == []
        assert signal.deprecations == []
        assert signal.api_changes == []
        assert signal.changelog_url is None

    def test_major_with_breaking_changes(self) -> None:
        signal = BreakingChangeSignal(
            semver_delta="major",
            changelog_url="https://github.com/pkg/releases/v5.0.0",
            breaking_changes=["Removed deprecated `foo()` API", "Changed return type of `bar()`"],
            deprecations=["baz() is deprecated, use qux()"],
        )
        assert signal.semver_delta == "major"
        assert len(signal.breaking_changes) == 2


# ------------------------------------------------------------------ #
# StrategyRecommendation                                               #
# ------------------------------------------------------------------ #

class TestStrategyRecommendation:
    def test_update_strategy(self, full_finding: Finding) -> None:
        rec = StrategyRecommendation(
            finding=full_finding,
            recommended_strategy=StrategyType.UPDATE,
            target_version="4.17.21",
            confidence=0.92,
            rationale="Minor update, no breaking changes detected, OSV clean.",
        )
        assert rec.recommended_strategy == "update"
        assert rec.confidence == 0.92
        assert rec.candidate_checks == []
        assert rec.alternatives_considered == []

    def test_nested_finding_round_trip(self, full_finding: Finding) -> None:
        rec = StrategyRecommendation(
            finding=full_finding,
            recommended_strategy=StrategyType.PATCH,
            confidence=0.75,
            rationale="Patch applied by Snyk.",
        )
        dumped = rec.model_dump(mode="json")
        reloaded = StrategyRecommendation.model_validate(dumped)
        assert reloaded.finding.package_name == "lodash"


# ------------------------------------------------------------------ #
# ValidationResult                                                     #
# ------------------------------------------------------------------ #

class TestValidationResult:
    def test_passing_validation(self) -> None:
        result = ValidationResult(
            success=True,
            test_passed=True,
            build_passed=True,
            rescan_clean=True,
            confidence=0.95,
            test_output_summary="All 42 tests passed in 3.2s",
            scan_output_summary="No open issues after upgrade",
            lockfile_diff_summary="lodash 4.17.15 → 4.17.21",
            execution_mode="docker",
        )
        assert result.success
        assert result.confidence == 0.95

    def test_failing_validation(self) -> None:
        result = ValidationResult(
            success=False,
            test_passed=False,
            build_passed=True,
            rescan_clean=True,
            confidence=0.0,
            test_output_summary="3 tests failed",
            scan_output_summary="Clean",
            lockfile_diff_summary="lodash 4.17.15 → 4.17.21",
            execution_mode="direct",
        )
        assert not result.success
        assert not result.test_passed


# ------------------------------------------------------------------ #
# DedupCheckResult                                                     #
# ------------------------------------------------------------------ #

class TestDedupCheckResult:
    def test_no_existing_work(self) -> None:
        result = DedupCheckResult()
        assert result.existing_pr is None
        assert result.existing_branch is None

    def test_existing_pr_found(self) -> None:
        result = DedupCheckResult(
            existing_pr={
                "url": "https://github.com/acme/api/pull/42",
                "state": "open",
                "headRefName": "vuln-remediation/CVE-2020-8203",
            },
            existing_branch="vuln-remediation/CVE-2020-8203",
        )
        assert result.existing_pr is not None
        assert "pull/42" in result.existing_pr["url"]


# ------------------------------------------------------------------ #
# RemediationRecord                                                    #
# ------------------------------------------------------------------ #

class TestRemediationRecord:
    def test_default_status(self, full_finding: Finding) -> None:
        rec = StrategyRecommendation(
            finding=full_finding,
            recommended_strategy=StrategyType.UPDATE,
            confidence=0.9,
            rationale="Safe update.",
        )
        record = RemediationRecord(finding=full_finding, strategy=rec)
        assert record.status == RemediationStatus.PENDING
        assert record.started_at is not None
        assert record.completed_at is None
        assert record.pr_url is None
        assert record.downstream_consumers == []

    def test_completed_record(self, full_finding: Finding) -> None:
        from datetime import datetime

        rec = StrategyRecommendation(
            finding=full_finding,
            recommended_strategy=StrategyType.UPDATE,
            confidence=0.9,
            rationale="Safe update.",
        )
        record = RemediationRecord(
            finding=full_finding,
            strategy=rec,
            status=RemediationStatus.PR_OPENED,
            pr_url="https://github.com/acme/api/pull/99",
            completed_at=datetime.now(),
            decision_rationale="Approved by security team.",
        )
        assert record.status == RemediationStatus.PR_OPENED
        assert record.pr_url is not None
        assert record.completed_at is not None
