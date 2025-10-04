"""Automated red team testing framework."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List


@dataclass
class TestResult:
    test_type: str
    timestamp: datetime
    success_rate: float
    notes: str = ""


class ContinuousRedTeamTesting:
    def __init__(self, target_endpoints: List[str]) -> None:
        self.target_endpoints = target_endpoints
        self.results: List[TestResult] = []
        self.baseline_score = 95.0

    async def _run_prompt_injection_tests(self) -> TestResult:
        success_rate = 0.1  # placeholder
        note = "No successful jailbreaks detected" if success_rate < 0.2 else "Investigate defenses"
        result = TestResult("prompt_injection", datetime.utcnow(), success_rate, note)
        self.results.append(result)
        return result

    async def _run_adversarial_tests(self) -> TestResult:
        success_rate = 0.3
        note = "High success rate" if success_rate > 0.25 else "Acceptable"
        result = TestResult("adversarial", datetime.utcnow(), success_rate, note)
        self.results.append(result)
        return result

    async def execute_once(self) -> List[TestResult]:
        return [
            await self._run_prompt_injection_tests(),
            await self._run_adversarial_tests(),
        ]

    def security_score(self) -> float:
        if not self.results:
            return self.baseline_score
        # Calculate penalty based on most recent test results
        recent_results = self.results[-5:]
        penalty = sum(result.success_rate * 50 for result in recent_results)
        return max(0.0, self.baseline_score - penalty)

    def trend(self, days: int = 7) -> Dict[str, float]:
        cutoff = datetime.utcnow() - timedelta(days=days)
        filtered = [r for r in self.results if r.timestamp >= cutoff]
        if not filtered:
            return {"data_points": 0, "average_success": 0.0}
        
        total = sum(r.success_rate for r in filtered)
        average = total / len(filtered)
        return {
            "data_points": len(filtered),
            "average_success": average,
        }
