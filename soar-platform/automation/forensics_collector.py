"""Collect forensic telemetry for incidents."""
from __future__ import annotations

from pathlib import Path
from typing import Dict


class ForensicsCollector:
    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    async def collect(self, context: Dict[str, str]) -> str:
        incident_id = context.get("incident_id", "unknown")
        path = self.storage_dir / f"{incident_id}-forensics.json"
        path.write_text(str(context), encoding="utf-8")
        return str(path)
