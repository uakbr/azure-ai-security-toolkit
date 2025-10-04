"""Policy-as-code evaluator for AI governance controls."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List

import yaml


class PolicyViolation(Exception):
    """Raised when policy requirements are not met."""


def load_policies(path: Path) -> List[Dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle) or []
        return payload if isinstance(payload, list) else [payload]


def evaluate_policy(policy: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
    field = policy.get("field", "")
    if not field:
        raise ValueError("Policy missing required 'field' key")
    if "equals" not in policy:
        raise ValueError("Policy missing required 'equals' key")
    
    expected = policy["equals"]
    severity = policy.get("severity", "MEDIUM")
    actual = context
    for segment in field.split('.'):
        if isinstance(actual, dict):
            actual = actual.get(segment)
        else:
            actual = None
            break
    compliant = actual == expected
    return {
        "policy_id": policy.get("id", "UNKNOWN"),
        "description": policy.get("description", ""),
        "severity": severity,
        "compliant": compliant,
        "actual": actual,
        "expected": expected,
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Evaluate AI governance policies.")
    parser.add_argument("--config", required=True, help="Path to policies YAML file")
    parser.add_argument(
        "--context",
        required=False,
        default="governance/context.json",
        help="Context JSON file containing evaluated values",
    )
    args = parser.parse_args(argv)

    policies = load_policies(Path(args.config))
    context_path = Path(args.context)
    context = json.loads(context_path.read_text()) if context_path.exists() else {}

    results = [evaluate_policy(policy, context) for policy in policies]
    failures = [r for r in results if not r["compliant"]]
    if failures:
        print(json.dumps(results, indent=2))
        raise PolicyViolation(f"Policy violations detected: {[f['policy_id'] for f in failures]}")

    print(json.dumps(results, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
