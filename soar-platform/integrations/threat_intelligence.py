"""Threat intelligence enrichment."""
from __future__ import annotations

from typing import Dict


class ThreatIntelFeed:
    async def enrich(self, incident: Dict[str, str]) -> Dict[str, str]:
        return {
            "attack_family": "PromptInjection" if incident.get("incident_type") == "PROMPT_INJECTION" else "Unknown",
            "confidence": 0.7,
        }
