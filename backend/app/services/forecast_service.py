"""Use case: 'what did the buyer see for this delivery day, and what happened?'"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time

from ..data.ports import ActualSource
from ..domain.metrics import quantile
from ..domain.selection import UK, DecisionCutoffSelector
from .alignment_service import AlignmentService
from .window import DeliveryWindow


@dataclass(frozen=True)
class SeriesPoint:
    start_time: datetime
    actual_mw: float | None
    forecast_mw: float | None
    publish_time: datetime | None
    band_low_mw: float | None  # forecast + P10 of other days' errors
    band_high_mw: float | None  # forecast + P90 of other days' errors


@dataclass(frozen=True)
class DaySeries:
    day: date
    cutoff: time
    deadline: datetime
    points: list[SeriesPoint]


class ForecastService:
    def __init__(self, alignment: AlignmentService, actuals: ActualSource) -> None:
        self.alignment = alignment
        self.actuals = actuals

    def day_series(self, day: date, cutoff: time) -> DaySeries:
        start, end = DeliveryWindow.day_bounds(day)
        aligned = self.alignment.at_cutoff(cutoff).points

        # Band from every OTHER day, so a day is never judged on its own outcome.
        others = [p.error_mw for p in aligned if p.start_time.astimezone(UK).date() != day]
        lo, hi = quantile(others, 0.1), quantile(others, 0.9)

        by_time = {p.start_time: p for p in aligned if start <= p.start_time < end}
        points = []
        for a in self.actuals.get_actuals(start, end):  # half-hourly actuals, hourly forecasts
            p = by_time.get(a.start_time)
            points.append(
                SeriesPoint(
                    a.start_time,
                    a.generation_mw,
                    p.forecast_mw if p else None,
                    p.publish_time if p else None,
                    p.forecast_mw + lo if p and lo is not None else None,
                    p.forecast_mw + hi if p and hi is not None else None,
                )
            )
        deadline = DecisionCutoffSelector(cutoff).deadline_for(start)
        return DaySeries(day, cutoff, deadline, points)
