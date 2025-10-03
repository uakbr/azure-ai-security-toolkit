"""Threat hunting routines for AI workloads."""
from __future__ import annotations

from typing import List


def generate_hunting_queries(model_name: str) -> List[str]:
    return [
        f"SecurityAlert | where Entities has '{model_name}'",
        f"AzureDiagnostics | where ResourceId contains '{model_name}'",
    ]
