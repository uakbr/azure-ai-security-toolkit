"""Prompt injection and content safety detectors."""
from __future__ import annotations

import asyncio
import re
from dataclasses import dataclass
from typing import Dict, List

try:
    from presidio_analyzer import AnalyzerEngine
except ImportError:  # pragma: no cover - optional dependency
    AnalyzerEngine = None  # type: ignore

JAILBREAK_PATTERNS = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in [
        r"ignore (all|any) previous instructions",
        r"disregard your (policy|policies)",
        r"disregard (?:all )?(?:rules|policies|instructions)",
        r"system prompt",
        r"now you are (?:allowed|permitted)",
        r"<\/?system>",
    ]
]


@dataclass
class DetectionResult:
    detected: bool
    confidence: float
    reasons: List[str]


class PromptInjectionDetector:
    """Composite detector for common prompt injection & jailbreak patterns."""

    def __init__(self) -> None:
        self._pii_analyzer = AnalyzerEngine() if AnalyzerEngine else None

    async def detect(self, content: str) -> DetectionResult:
        reasons: List[str] = []
        confidence = 0.0

        if any(pattern.search(content) for pattern in JAILBREAK_PATTERNS):
            reasons.append("Matched known jailbreak pattern")
            confidence = max(confidence, 0.8)

        if "base64" in content.lower() and "system" in content.lower():
            reasons.append("Potential obfuscated system prompt request")
            confidence = max(confidence, 0.6)

        if self._pii_analyzer:
            pii_entities = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._pii_analyzer.analyze(text=content, language="en"),
            )
            if pii_entities:
                reasons.append("Detected potential PII in request")
                confidence = max(confidence, 0.7)

        return DetectionResult(bool(reasons), confidence, reasons)


class DataExfiltrationDetector:
    """Detect sensitive data exfiltration patterns."""

    SENSITIVE_KEYWORDS = [
        "internal", "confidential", "secret", "classified", "proprietary"
    ]

    async def detect(self, content: str) -> DetectionResult:
        matches = [keyword for keyword in self.SENSITIVE_KEYWORDS if keyword in content.lower()]
        confidence = 0.5 + 0.1 * len(matches) if matches else 0.0
        return DetectionResult(bool(matches), min(confidence, 0.95), matches)
