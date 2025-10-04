"""Reporting utilities for the scanner."""
from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime, UTC
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .config import ScannerConfig


class ReportWriter:
    """Persist scan findings to disk in multiple formats."""

    def __init__(self, config: ScannerConfig) -> None:
        self.config = config
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, summary: Dict[str, Any], findings: Iterable[Dict[str, Any]]) -> Path:
        payload = {
            "generated_at": datetime.now(UTC).isoformat(),
            "config": self.config.as_dict(),
            "summary": summary,
            "findings": list(findings),
        }
        path = self.output_dir / "scan-report.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return path

    def write_markdown(self, summary: Dict[str, Any], findings: Iterable[Dict[str, Any]]) -> Path:
        path = self.output_dir / "scan-report.md"
        lines: List[str] = []
        lines.append(f"# Azure AI Security Scan Report\n")
        lines.append(f"_Generated: {datetime.now(UTC).isoformat()}_\n")
        lines.append("## Summary\n")
        for key, value in summary.items():
            lines.append(f"- **{key.replace('_', ' ').title()}**: {value}")
        lines.append("\n## Findings\n")
        for finding in findings:
            lines.append(f"### {finding['rule_id']} - {finding['title']}")
            lines.append(f"- Severity: {finding['severity']}")
            lines.append(f"- Resource: `{finding['resource_id']}`")
            lines.append(f"- Message: {finding['message']}")
            compliance = finding.get("compliance")
            if compliance:
                lines.append("- Compliance Mapping:")
                for framework, control in compliance.items():
                    lines.append(f"  - {framework}: {control}")
            lines.append("")
        path.write_text("\n".join(lines), encoding="utf-8")
        return path


def serialize_finding(rule: Any, resource: Dict[str, Any], evidence: Dict[str, Any]) -> Dict[str, Any]:
    """Create a consistent finding payload for reporting."""
    return {
        "rule_id": rule.rule_id,
        "title": rule.title,
        "severity": rule.severity,
        "resource_id": resource.get("id"),
        "resource_name": resource.get("name"),
        "resource_type": resource.get("resource_type"),
        "message": evidence.get("message", ""),
        "compliance": rule.compliance,
        "remediation": rule.remediation,
        "evidence": evidence,
    }


def summarize(findings: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate summary statistics for scan results."""
    findings_list = list(findings)
    totals: Dict[str, int] = {}
    for finding in findings_list:
        severity = finding["severity"].upper()
        totals[severity] = totals.get(severity, 0) + 1

    return {
        "total_findings": len(findings_list),
        "by_severity": totals,
        "unique_resources": len({f["resource_id"] for f in findings_list}),
    }
