"""Pairs actuals with the forecast chosen by a selector."""
from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

from .models import Actual, AlignedPoint, Forecast
from .selection import ForecastSelector


@dataclass(frozen=True)
class AlignmentResult:
    points: list[AlignedPoint]
    missing_forecast: list[datetime]  # targets with an actual but no usable forecast


class Aligner:
    def __init__(self, selector: ForecastSelector) -> None:
        self.selector = selector

    def align(self, actuals: Iterable[Actual], forecasts: Iterable[Forecast]) -> AlignmentResult:
        by_target: dict[datetime, list[Forecast]] = defaultdict(list)
        for f in forecasts:
            by_target[f.start_time].append(f)

        points: list[AlignedPoint] = []
        missing: list[datetime] = []
        for a in sorted(actuals, key=lambda a: a.start_time):
            candidates = by_target.get(a.start_time)
            if not candidates:
                continue  # forecasts are hourly; half-hour actuals have no counterpart
            chosen = self.selector.select(a.start_time, candidates)
            if chosen is None:
                missing.append(a.start_time)
                continue
            points.append(AlignedPoint(a.start_time, a.generation_mw, chosen.generation_mw, chosen.publish_time))
        return AlignmentResult(points, missing)
