"""Config loader for .vuln-remediation.yml with sane defaults."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field


class RiskThresholdConfig(BaseModel):
    min_severity: str = "high"
    allow_reachable_medium: bool = True


class StrategiesConfig(BaseModel):
    allow: list[str] = Field(default_factory=lambda: ["update", "patch", "mitigate"])
    replacement_mode: str = "advisory"


class ConsumerConfig(BaseModel):
    name: str
    type: str
    contract_tests: str | None = None


class NotificationsConfig(BaseModel):
    slack_channel: str | None = None
    jira_project: str | None = None


class ConfidenceConfig(BaseModel):
    default_min: float = 0.8
    major_min: float = 0.9


class VulnRemediationConfig(BaseModel):
    version: int = 1
    risk_threshold: RiskThresholdConfig = Field(default_factory=RiskThresholdConfig)
    supported_ecosystems: list[str] = Field(default_factory=lambda: ["npm", "maven", "docker"])
    strategies: StrategiesConfig = Field(default_factory=StrategiesConfig)
    execution_mode: str = "docker"  # direct | docker | docker-restricted
    consumers: list[ConsumerConfig] = Field(default_factory=list)
    notifications: NotificationsConfig = Field(default_factory=NotificationsConfig)
    confidence: ConfidenceConfig = Field(default_factory=ConfidenceConfig)


def _camel_to_snake(d: Any) -> Any:
    """Recursively convert camelCase keys to snake_case for config loading."""
    import re

    if isinstance(d, dict):
        out: dict = {}
        for k, v in d.items():
            snake = re.sub(r"(?<!^)(?=[A-Z])", "_", k).lower()
            out[snake] = _camel_to_snake(v)
        return out
    if isinstance(d, list):
        return [_camel_to_snake(i) for i in d]
    return d


def load_config(repo_root: Path | str | None = None) -> VulnRemediationConfig:
    """Load .vuln-remediation.yml from repo root, falling back to defaults.

    Args:
        repo_root: Path to the repository root. Defaults to cwd.

    Returns:
        Validated VulnRemediationConfig with defaults applied.
    """
    root = Path(repo_root) if repo_root else Path.cwd()
    config_path = root / ".vuln-remediation.yml"

    if not config_path.exists():
        return VulnRemediationConfig()

    with config_path.open() as f:
        raw = yaml.safe_load(f) or {}

    # Support both camelCase (spec format) and snake_case keys
    normalized = _camel_to_snake(raw)
    return VulnRemediationConfig.model_validate(normalized)
