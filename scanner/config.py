"""Scanner configuration models."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional


def _default_rules() -> List[str]:
    return [
        "rules/azure_openai.yaml",
        "rules/ml_workspace.yaml",
        "rules/cognitive_services.yaml",
    ]


@dataclass
class ScannerConfig:
    """Runtime configuration for the security scanner."""

    subscription_id: str
    output_dir: Path = Path("reports")
    rulesets: Iterable[str] = field(default_factory=_default_rules)
    include_resource_groups: Optional[List[str]] = None
    exclude_resource_groups: Optional[List[str]] = None
    concurrent_requests: int = 10
    severity_threshold: str = "LOW"
    enable_compliance_mapping: bool = True
    tag_filters: Optional[dict[str, str]] = None

    def as_dict(self) -> dict[str, object]:
        """Return configuration as JSON-serialisable dictionary."""

        return {
            "subscription_id": self.subscription_id,
            "output_dir": str(self.output_dir),
            "rulesets": list(self.rulesets),
            "include_resource_groups": self.include_resource_groups or [],
            "exclude_resource_groups": self.exclude_resource_groups or [],
            "concurrent_requests": self.concurrent_requests,
            "severity_threshold": self.severity_threshold,
            "enable_compliance_mapping": self.enable_compliance_mapping,
            "tag_filters": self.tag_filters or {},
        }
