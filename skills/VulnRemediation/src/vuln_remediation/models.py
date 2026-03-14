"""Pydantic models for the vulnerability remediation skill."""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class Severity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class DependencyType(StrEnum):
    DIRECT = "direct"
    TRANSITIVE = "transitive"
    BASE_IMAGE = "base_image"


class Ecosystem(StrEnum):
    NPM = "npm"
    MAVEN = "maven"
    DOCKER = "docker"
    PNPM = "pnpm"
    YARN = "yarn"
    GRADLE = "gradle"


class StrategyType(StrEnum):
    UPDATE = "update"
    PATCH = "patch"
    REPLACE = "replace"
    MITIGATE = "mitigate"


class RemediationStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    PR_OPENED = "pr_opened"
    REPORT_ONLY = "report_only"
    SKIPPED = "skipped"
    FAILED = "failed"


class Finding(BaseModel):
    """Normalized vulnerability finding from any scanner."""

    finding_id: str
    source_system: str
    repository: str
    branch: str
    manifest_path: str
    ecosystem: Ecosystem
    package_name: str
    purl: str
    current_version: str
    candidate_fixed_versions: list[str] = Field(default_factory=list)
    dependency_type: DependencyType
    dependency_path: list[str] = Field(default_factory=list)
    severity: Severity
    cvss: float | None = None
    epss: float | None = None
    exploit_maturity: str | None = None
    reachable: bool | None = None
    runtime_exposure: str | None = None
    advisory_ids: list[str] = Field(default_factory=list)
    scanner_evidence_urls: list[str] = Field(default_factory=list)
    introduced_via: str | None = None
    fix_types_available: list[StrategyType] = Field(default_factory=list)


class CandidateCheck(BaseModel):
    """Result of checking a candidate version against advisory databases."""

    version: str
    safe: bool
    advisories: list[str] = Field(default_factory=list)
    severity_introduced: Severity | None = None


class BreakingChangeSignal(BaseModel):
    """Structured breaking change evidence."""

    semver_delta: str  # major | minor | patch
    changelog_url: str | None = None
    breaking_changes: list[str] = Field(default_factory=list)
    deprecations: list[str] = Field(default_factory=list)
    api_changes: list[str] = Field(default_factory=list)


class StrategyRecommendation(BaseModel):
    """Output of the strategy engine."""

    finding: Finding
    recommended_strategy: StrategyType
    target_version: str | None = None
    confidence: float
    rationale: str
    breaking_change_signals: BreakingChangeSignal | None = None
    candidate_checks: list[CandidateCheck] = Field(default_factory=list)
    alternatives_considered: list[str] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Output of the validate step."""

    success: bool
    test_passed: bool
    build_passed: bool
    rescan_clean: bool
    confidence: float
    test_output_summary: str
    scan_output_summary: str
    lockfile_diff_summary: str
    execution_mode: str  # direct | docker | docker-restricted


class DedupCheckResult(BaseModel):
    """Result of checking for existing remediation work."""

    existing_pr: dict | None = None  # {url, status, branch}
    existing_branch: str | None = None


class RemediationRecord(BaseModel):
    """Full remediation lifecycle record — written to decision log."""

    finding: Finding
    strategy: StrategyRecommendation
    validation: ValidationResult | None = None
    pr_url: str | None = None
    status: RemediationStatus = RemediationStatus.PENDING
    started_at: datetime = Field(default_factory=datetime.now)
    completed_at: datetime | None = None
    decision_rationale: str = ""
    downstream_consumers: list[str] = Field(default_factory=list)
