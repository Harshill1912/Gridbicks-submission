"""Turns historical error into a 'plan for this much wind' recommendation."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence

from .metrics import quantile
from .models import AlignedPoint


@dataclass(frozen=True)
class Plan:
    forecast_mw: float
    planned_wind_mw: float  # wind you can count on at the chosen confidence
    buffer_mw: float  # extra power to procure beyond forecast-based buying
    confidence: float


class ErrorQuantilePlanner:
    """Plans for forecast + the (1 - confidence) quantile of historical error.

    At 90% confidence, actual wind fell below the planned level in only ~10%
    of the historical cases.
    """

    def __init__(self, history: Sequence[AlignedPoint]) -> None:
        self.errors = [p.error_mw for p in history]

    def plan(self, forecast_mw: float, confidence: float) -> Plan:
        if not 0 < confidence < 1:
            raise ValueError("confidence must be between 0 and 1")
        q = quantile(self.errors, 1 - confidence) or 0.0
        planned = max(0.0, forecast_mw + q)
        return Plan(forecast_mw, planned, forecast_mw - planned, confidence)

    def shortfall_rate(self, confidence: float) -> float | None:
        """Share of historical periods where actual came in below the plan."""
        if not self.errors:
            return None
        q = quantile(self.errors, 1 - confidence) or 0.0
        return sum(1 for e in self.errors if e < q) / len(self.errors)
