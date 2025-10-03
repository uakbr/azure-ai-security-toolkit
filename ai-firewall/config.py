"""Configuration for AI Firewall proxy."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class FirewallConfig:
    """Runtime configuration for the security proxy."""

    azure_openai_endpoint: str
    azure_openai_deployment: str
    api_key: str
    rate_limit_per_minute: int = 60
    allowed_origins: Optional[List[str]] = None
    enable_content_safety: bool = True
    enable_logging: bool = True
    sentinel_workspace_id: Optional[str] = None
    sentinel_shared_key: Optional[str] = None
