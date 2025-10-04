"""Model card generator with security considerations."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime, UTC
from pathlib import Path
from typing import Dict, List


@dataclass
class RiskMitigation:
    category: str
    description: str
    status: str


@dataclass
class ModelCard:
    model_name: str
    version: str
    owners: List[str]
    intended_use: str
    security_review_date: str
    threat_model_summary: str
    mitigations: List[RiskMitigation]
    evaluation_data: Dict[str, str]

    def to_markdown(self) -> str:
        lines = [f"# Model Card: {self.model_name} ({self.version})\n"]
        lines.append(f"**Owners:** {', '.join(self.owners)}")
        lines.append(f"**Intended Use:** {self.intended_use}")
        lines.append(f"**Security Review Date:** {self.security_review_date}")
        lines.append("\n## Threat Model\n")
        lines.append(self.threat_model_summary)
        lines.append("\n## Risk Mitigations\n")
        for mitigation in self.mitigations:
            lines.append(f"- **{mitigation.category}** ({mitigation.status}): {mitigation.description}")
        lines.append("\n## Evaluation Data\n")
        for key, value in self.evaluation_data.items():
            lines.append(f"- **{key}**: {value}")
        lines.append(f"\n_Generated: {datetime.now(UTC).isoformat()}_\n")
        return "\n".join(lines)

    def save(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.to_markdown(), encoding="utf-8")
        return path


def create_model_card(template: Dict[str, str]) -> ModelCard:
    required_fields = ["model_name", "version", "owners", "intended_use"]
    for field in required_fields:
        if field not in template:
            raise ValueError(f"Missing required field in template: {field}")
    
    if not isinstance(template.get("owners"), list):
        raise ValueError("Field 'owners' must be a list")
    
    mitigations = [
        RiskMitigation(category=entry["category"], description=entry["description"], status=entry["status"])
        for entry in template.get("mitigations", [])
        if isinstance(entry, dict) and all(k in entry for k in ["category", "description", "status"])
    ]
    return ModelCard(
        model_name=template["model_name"],
        version=template["version"],
        owners=template["owners"],
        intended_use=template["intended_use"],
        security_review_date=template.get("security_review_date", datetime.now(UTC).date().isoformat()),
        threat_model_summary=template.get("threat_model_summary", ""),
        mitigations=mitigations,
        evaluation_data=template.get("evaluation_data", {}),
    )
