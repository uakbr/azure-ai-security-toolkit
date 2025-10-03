"""Detect secrets within Copilot generated suggestions."""
from __future__ import annotations

import re
from typing import Iterable, List

SECRET_PATTERNS = [
    re.compile(pattern)
    for pattern in [
        r"AKIA[0-9A-Z]{16}",
        r"(?i)-----BEGIN (?:RSA|DSA|EC) PRIVATE KEY-----",
        r"xox[baprs]-[0-9a-zA-Z]{10,48}",
        r"AIza[0-9A-Za-z\-_]{35}",
    ]
]


def detect_secrets(lines: Iterable[str]) -> List[str]:
    findings: List[str] = []
    for line in lines:
        for pattern in SECRET_PATTERNS:
            if pattern.search(line):
                findings.append(line.strip())
                break
    return findings
