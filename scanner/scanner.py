"""Core scanning logic."""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any, Dict, Iterable, List

from .client import AzureClient, gather_with_concurrency
from .config import ScannerConfig
from .reporting import ReportWriter, serialize_finding, summarize
from .rules import Rule, load_rules, load_rules_from_files


class AISecurityScanner:
    """Azure AI Security Scanner orchestrates resource discovery and rule evaluation."""

    def __init__(self, config: ScannerConfig, extra_rules: Iterable[Rule] | None = None) -> None:
        self.config = config
        builtin_rules = load_rules()
        custom_rule_files = []
        if config.rulesets:
            custom_rule_files = load_rules_from_files(self._resolve_rule_paths())
        self.rules: List[Rule] = builtin_rules + custom_rule_files
        if extra_rules:
            self.rules.extend(list(extra_rules))

    def _resolve_rule_paths(self) -> List[Path]:
        paths: List[Path] = []
        for ruleset in self.config.rulesets:
            candidate = (Path.cwd() / ruleset).resolve()
            if candidate.exists():
                paths.append(candidate)
        return paths

    async def scan(self) -> Dict[str, Any]:
        """Run scan and return payload containing summary and findings."""
        findings: List[Dict[str, Any]] = []
        async with AzureClient(self.config.subscription_id) as client:
            tasks = []
            async for resource in client.list_azure_ai_resources():
                tasks.append(self._evaluate_resource(resource))
            evaluated = await gather_with_concurrency(self.config.concurrent_requests, *tasks)
            for result in evaluated:
                findings.extend(result)

        summary = summarize(findings)
        writer = ReportWriter(self.config)
        json_path = writer.write_json(summary, findings)
        md_path = writer.write_markdown(summary, findings)
        return {
            "summary": summary,
            "findings": findings,
            "report_json": str(json_path),
            "report_markdown": str(md_path),
        }

    async def _evaluate_resource(self, resource: Dict[str, Any]) -> List[Dict[str, Any]]:
        resource_findings: List[Dict[str, Any]] = []
        for rule in self.rules:
            if resource.get("resource_type") not in rule.resource_types:
                continue
            evidence = rule.evaluator(resource)
            if asyncio.iscoroutine(evidence):
                evidence = await evidence
            if evidence:
                resource_findings.append(serialize_finding(rule, resource, evidence))
        return resource_findings


async def run_scan(config: ScannerConfig) -> Dict[str, Any]:
    scanner = AISecurityScanner(config)
    return await scanner.scan()
