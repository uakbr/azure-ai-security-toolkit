"""SOAR orchestration engine for AI security incidents."""
from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Any, Dict, List


class IncidentSeverity(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AISecurityIncident:
    incident_type: str
    severity: IncidentSeverity
    context: Dict[str, Any]
    id: str = field(default_factory=lambda: datetime.now(UTC).strftime("INC%Y%m%d%H%M%S%f"))
    timestamp: datetime = field(default_factory=lambda: datetime.now(UTC))
    status: str = "NEW"
    actions_taken: List[Dict[str, Any]] = field(default_factory=list)
    resolved: bool = False


class SOAROrchestrator:
    """Coordinates incident response playbooks."""

    def __init__(self, playbooks: Dict[str, Dict[str, Any]], integrations: Dict[str, Any]) -> None:
        self.playbooks = playbooks
        self.integrations = integrations
        self.active_incidents: Dict[str, AISecurityIncident] = {}

    async def handle_event(self, event: Dict[str, Any]) -> AISecurityIncident:
        severity_str = event.get("severity", "LOW")
        try:
            severity = IncidentSeverity[severity_str]
        except KeyError:
            severity = IncidentSeverity.LOW
        
        incident = AISecurityIncident(
            incident_type=event.get("type", "UNKNOWN"),
            severity=severity,
            context=event.get("context", {}),
        )
        self.active_incidents[incident.id] = incident
        playbook = self.playbooks.get(incident.incident_type)
        if not playbook:
            incident.status = "NO_PLAYBOOK"
            return incident
        await self._execute_playbook(incident, playbook)
        incident.status = "RESOLVED" if incident.resolved else "IN_PROGRESS"
        return incident

    async def _execute_playbook(self, incident: AISecurityIncident, playbook: Dict[str, Any]) -> None:
        for step in playbook.get("steps", []):
            handler_name = step.get("action")
            if not handler_name:
                continue
            handler = getattr(self, f"_action_{handler_name}", None)
            if not handler:
                continue
            result = await handler(step, incident)
            step_name = step.get("name", handler_name)
            incident.actions_taken.append({"step": step_name, "result": result})
            if result.get("resolved"):
                incident.resolved = True
                break

    async def _action_block_user(self, step: Dict[str, Any], incident: AISecurityIncident) -> Dict[str, Any]:
        user_id = incident.context.get("user_id")
        if not user_id:
            return {"resolved": False, "message": "No user_id in incident context"}
        if "pagerduty" not in self.integrations:
            return {"resolved": False, "message": "PagerDuty integration not configured"}
        integration = self.integrations["pagerduty"]
        if not hasattr(integration, "trigger_incident"):
            return {"resolved": False, "message": "PagerDuty integration missing trigger_incident method"}
        try:
            await integration.trigger_incident(user_id)
        except Exception as exc:
            return {"resolved": False, "message": f"Failed to block user: {exc}"}
        return {"resolved": False, "message": f"User {user_id} blocked"}

    async def _action_collect_forensics(self, step: Dict[str, Any], incident: AISecurityIncident) -> Dict[str, Any]:
        if "forensics" not in self.integrations:
            return {"resolved": False, "message": "Forensics integration not configured"}
        collector = self.integrations["forensics"]
        if not hasattr(collector, "collect"):
            return {"resolved": False, "message": "Forensics integration missing collect method"}
        try:
            blob_url = await collector.collect(incident.context)
        except Exception as exc:
            return {"resolved": False, "message": f"Failed to collect forensics: {exc}"}
        return {"resolved": False, "forensics_url": blob_url}

    async def _action_quarantine_model(self, step: Dict[str, Any], incident: AISecurityIncident) -> Dict[str, Any]:
        model_name = incident.context.get("model_name")
        if not model_name:
            return {"resolved": False, "message": "No model_name in incident context"}
        if "ml" not in self.integrations:
            return {"resolved": False, "message": "ML integration not configured"}
        integration = self.integrations["ml"]
        if not hasattr(integration, "quarantine_model"):
            return {"resolved": False, "message": "ML integration missing quarantine_model method"}
        try:
            await integration.quarantine_model(model_name)
        except Exception as exc:
            return {"resolved": False, "message": f"Failed to quarantine model: {exc}"}
        return {"resolved": True, "message": f"Model {model_name} quarantined"}
