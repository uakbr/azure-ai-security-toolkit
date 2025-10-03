"""PagerDuty integration stub."""
from __future__ import annotations


class PagerDutyConnector:
    async def trigger_incident(self, subject: str) -> None:
        print(f"[PagerDuty] Incident triggered for {subject}")
