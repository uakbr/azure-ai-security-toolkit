"""Placeholder Azure Sentinel integration."""
from __future__ import annotations

from datetime import datetime
from typing import Dict


class SentinelConnector:
    def __init__(self, workspace_id: str, shared_key: str) -> None:
        self.workspace_id = workspace_id
        self.shared_key = shared_key

    async def send_incident(self, incident: Dict[str, str]) -> None:
        print(f"[Sentinel] {datetime.utcnow().isoformat()} - {incident}")
