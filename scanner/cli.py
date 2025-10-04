"""Command-line interface for the Azure AI Security Scanner."""
from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from typing import Any

from .config import ScannerConfig
from .scanner import AISecurityScanner


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scan Azure AI resources for security misconfigurations.",
    )
    parser.add_argument("--subscription-id", required=True, help="Azure subscription ID")
    parser.add_argument(
        "--output-dir",
        default="reports",
        help="Directory to store generated reports",
    )
    parser.add_argument(
        "--ruleset",
        action="append",
        default=[],
        help="Path to additional YAML ruleset file",
    )
    parser.add_argument(
        "--severity-threshold",
        default="LOW",
        choices=["LOW", "MEDIUM", "HIGH", "CRITICAL"],
        help="Only include findings at or above this severity",
    )
    parser.add_argument(
        "--tag-filter",
        action="append",
        default=[],
        help="Tag filters formatted as key=value",
    )
    parser.add_argument(
        "--concurrency",
        type=int,
        default=10,
        help="Maximum concurrent API calls",
    )
    return parser


def parse_tag_filters(values: list[str]) -> dict[str, str]:
    filters: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise ValueError(f"Invalid tag filter format: {value}")
        key, tag_value = value.split("=", 1)
        filters[key.strip()] = tag_value.strip()
    return filters


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.concurrency <= 0:
        parser.error("--concurrency must be greater than 0")

    config = ScannerConfig(
        subscription_id=args.subscription_id,
        output_dir=Path(args.output_dir),
        rulesets=args.ruleset if args.ruleset else None,
        severity_threshold=args.severity_threshold,
        tag_filters=parse_tag_filters(args.tag_filter or []),
        concurrent_requests=args.concurrency,
    )

    scanner = AISecurityScanner(config)
    results: dict[str, Any] = asyncio.run(scanner.scan())
    print(json.dumps(results["summary"], indent=2))
    print(f"JSON report: {results['report_json']}")
    print(f"Markdown report: {results['report_markdown']}")
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI invocation
    raise SystemExit(main())
