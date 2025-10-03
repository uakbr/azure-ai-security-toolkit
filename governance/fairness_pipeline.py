"""Automated fairness and bias detection pipeline."""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

import numpy as np


@dataclass
class FairnessMetric:
    name: str
    value: float
    threshold: float

    def compliant(self) -> bool:
        return self.value >= self.threshold


class FairnessPipeline:
    """Simple fairness metric calculator placeholder."""

    def __init__(self, protected_attribute: str = "gender") -> None:
        self.protected_attribute = protected_attribute

    def evaluate(self, labels: np.ndarray, predictions: np.ndarray, groups: np.ndarray) -> List[FairnessMetric]:
        metrics: List[FairnessMetric] = []
        unique_groups = np.unique(groups)
        acceptance_rates = {}
        for group in unique_groups:
            mask = groups == group
            acceptance_rates[group] = predictions[mask].mean()
        max_rate = max(acceptance_rates.values())
        parity = min(rate / max_rate for rate in acceptance_rates.values())
        metrics.append(FairnessMetric("demographic_parity", parity, 0.8))

        false_positive_rates: Dict[str, float] = {}
        for group in unique_groups:
            mask = groups == group
            fp = ((predictions[mask] == 1) & (labels[mask] == 0)).sum()
            negatives = (labels[mask] == 0).sum()
            false_positive_rates[group] = fp / max(negatives, 1)
        disparity = max(false_positive_rates.values()) - min(false_positive_rates.values())
        metrics.append(FairnessMetric("false_positive_rate_gap", 1 - disparity, 0.7))
        return metrics

    def generate_report(self, metrics: List[FairnessMetric], output_path: Path) -> Path:
        payload = {
            "protected_attribute": self.protected_attribute,
            "metrics": [
                {
                    "name": metric.name,
                    "value": metric.value,
                    "threshold": metric.threshold,
                    "compliant": metric.compliant(),
                }
                for metric in metrics
            ],
        }
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return output_path
