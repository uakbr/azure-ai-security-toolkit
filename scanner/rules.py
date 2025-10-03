"""Rule definitions for the Azure AI security scanner."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional

Severity = str
Resource = Dict[str, Any]


@dataclass
class Rule:
    """Represents a single security rule evaluated against Azure resources."""

    rule_id: str
    title: str
    description: str
    severity: Severity
    resource_types: Iterable[str]
    evaluator: Callable[[Resource], Optional[Dict[str, Any]]]
    remediation: str
    compliance: Dict[str, str]


# Built-in evaluators -----------------------------------------------------------------


def _is_public_network_enabled(resource: Resource) -> Optional[Dict[str, Any]]:
    properties = resource.get("properties", {}) or {}
    network = properties.get("publicNetworkAccess")
    if network and str(network).lower() == "enabled":
        return {
            "message": "Public network access is enabled; enforce private endpoints.",
        }
    return None


def _has_soft_delete_disabled(resource: Resource) -> Optional[Dict[str, Any]]:
    props = resource.get("properties", {})
    if props and not props.get("disableSoftDelete", False):
        return None
    return {"message": "Soft delete is disabled; enable to prevent accidental loss."}


def _missing_customer_managed_key(resource: Resource) -> Optional[Dict[str, Any]]:
    encryption = resource.get("properties", {}).get("encryption", {})
    if encryption.get("status", "Disabled") == "Disabled":
        return {"message": "Customer-managed key not configured."}
    return None


DEFAULT_RULES: List[Rule] = [
    Rule(
        rule_id="OPENAI-001",
        title="Disable public access",
        description="Azure OpenAI accounts must restrict public network access.",
        severity="CRITICAL",
        resource_types=["azure_openai"],
        evaluator=_is_public_network_enabled,
        remediation=(
            "Configure Azure OpenAI account to use private endpoints or set publicNetworkAccess to Disabled."
        ),
        compliance={
            "OWASP-LLM": "LLM02",
            "NIST-AI-RMF": "GOVERN-MAP-1",
            "MITRE-ATLAS": "AML.T0051",
        },
    ),
    Rule(
        rule_id="ML-001",
        title="Encryption at rest",
        description="Azure ML workspaces should enforce customer-managed keys.",
        severity="HIGH",
        resource_types=["ml_workspaces"],
        evaluator=_missing_customer_managed_key,
        remediation="Configure workspace encryption with customer-managed keys.",
        compliance={
            "OWASP-LLM": "LLM03",
            "NIST-AI-RMF": "MEASURE-1",
            "MITRE-ATLAS": "AML.T0020",
        },
    ),
    Rule(
        rule_id="COGNITIVE-002",
        title="Soft delete must remain enabled",
        description="Cognitive Services accounts must enable soft delete for resiliency.",
        severity="MEDIUM",
        resource_types=["cognitive_services"],
        evaluator=_has_soft_delete_disabled,
        remediation="Enable soft delete in Azure portal or API.",
        compliance={
            "OWASP-LLM": "LLM08",
            "NIST-AI-RMF": "MANAGE-3",
            "MITRE-ATLAS": "AML.T0024",
        },
    ),
]


# Dynamic rule helpers ----------------------------------------------------------------


def _evaluate_condition(resource: Resource, condition: Dict[str, Any]) -> bool:
    """Evaluate a simple condition tree from YAML definitions."""
    operator = condition.get("operator", "equals").lower()
    field = condition.get("field", "")
    expected = condition.get("value")

    current = resource
    for part in field.split("."):
        if isinstance(current, dict):
            current = current.get(part)
        else:
            current = None
            break

    if operator == "equals":
        return str(current).lower() == str(expected).lower()
    if operator == "not_equals":
        return str(current).lower() != str(expected).lower()
    if operator == "in":
        return current in expected  # type: ignore[operator]
    if operator == "exists":
        return current is not None
    if operator == "not_exists":
        return current is None

    raise ValueError(f"Unsupported operator: {operator}")


def from_yaml_rule(payload: Dict[str, Any]) -> Rule:
    """Create a rule from YAML payload with declarative conditions."""

    condition = payload.get("condition") or {}
    message = payload.get("message", "Condition matched.")

    def evaluator(resource: Resource) -> Optional[Dict[str, Any]]:
        if _evaluate_condition(resource, condition):
            return {"message": message, "evidence": condition}
        return None

    return Rule(
        rule_id=payload["rule_id"],
        title=payload["title"],
        description=payload.get("description", ""),
        severity=payload.get("severity", "MEDIUM"),
        resource_types=payload.get("resource_types", []),
        evaluator=evaluator,
        remediation=payload.get("remediation", ""),
        compliance=payload.get("compliance", {}),
    )


def load_rules(extra_rules: Optional[Iterable[Rule]] = None) -> List[Rule]:
    """Return default rules optionally extended by user-provided rules."""
    rules = list(DEFAULT_RULES)
    if extra_rules:
        rules.extend(extra_rules)
    return rules


def load_rules_from_files(paths: Iterable[Path]) -> List[Rule]:
    """Load declarative rule definitions from YAML files."""
    try:
        import yaml  # type: ignore
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("Install PyYAML to load custom rules from disk") from exc

    loaded: List[Rule] = []
    for path in paths:
        with Path(path).open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle) or []
            if isinstance(payload, dict):
                payload = [payload]
            for item in payload:
                loaded.append(from_yaml_rule(item))
    return loaded
