"""Azure Defender for Cloud connector."""
from __future__ import annotations

from typing import Dict


class DefenderConnector:
    async def isolate_resource(self, resource_id: str) -> Dict[str, str]:
        return {"status": "isolated", "resource_id": resource_id}
