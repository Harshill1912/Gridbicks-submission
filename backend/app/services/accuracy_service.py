"""Use case: 'how good were the forecasts, and where are they weakest?'"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import time
from typing import Sequence

from ..domain.metrics import MetricSuite
from ..domain.models import AlignedPoint
from ..domain.selection import UK
from .alignment_service import AlignmentService

DEFAULT_HORIZONS_H: tuple[float, ...] = (1, 2, 4, 6, 8, 12, 18, 24, 30, 36, 42, 48)


@dataclass(frozen=True)
class Summary:
    count: int
    missing_forecast: int
    metrics: dict[str, float | None]


class AccuracyService:
    def __init__(self, alignment: AlignmentService, suite: MetricSuite | None = None) -> None:
        self.alignment = alignment
        self.suite = suite or MetricSuite()

    def summary(self, cutoff: time) -> Summary:
        result = self.alignment.at_cutoff(cutoff)
        return Summary(len(result.points), len(result.missing_forecast), self.suite.compute(result.points))

    def by_horizon(self, horizons: Sequence[float] = DEFAULT_HORIZONS_H) -> list[dict]:
        """Error when using the latest forecast at least N hours old."""
        rows = []
        for h in horizons:
            points = self.alignment.at_horizon(float(h)).points
            rows.append({"horizon_h": h, "count": len(points), **self.suite.compute(points)})
        return rows

    def by_hour_of_day(self, cutoff: time) -> list[dict]:
        return self._grouped(cutoff, lambda p: p.start_time.astimezone(UK).hour, "hour")

    def by_wind_level(self, cutoff: time, step_mw: int = 3000) -> list[dict]:
        """Error bucketed by forecast size, e.g. 0-3 GW, 3-6 GW."""
        return self._grouped(cutoff, lambda p: int(p.forecast_mw // step_mw) * step_mw, "forecast_from_mw")

    def scatter(self, cutoff: time) -> list[AlignedPoint]:
        return self.alignment.at_cutoff(cutoff).points

    def _grouped(self, cutoff: time, key, label: str) -> list[dict]:
        grouped = self.suite.grouped(self.alignment.at_cutoff(cutoff).points, key)
        return [{label: k, **v} for k, v in grouped.items()]
