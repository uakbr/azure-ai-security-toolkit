"""Copilot usage analytics and reporting."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class CopilotUsage:
    user: str
    accepted_suggestions: int
    rejected_suggestions: int

    @property
    def acceptance_rate(self) -> float:
        total = self.accepted_suggestions + self.rejected_suggestions
        return self.accepted_suggestions / total if total else 0.0


def generate_report(usages: List[CopilotUsage], path: Path) -> Path:
    summary = {
        "total_users": len(usages),
        "average_acceptance_rate": (
            sum(u.acceptance_rate for u in usages) / len(usages)
            if usages else 0.0
        ),
        "users": [
            {
                "user": usage.user,
                "acceptance_rate": usage.acceptance_rate,
                "accepted": usage.accepted_suggestions,
                "rejected": usage.rejected_suggestions,
            }
            for usage in usages
        ],
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return path
