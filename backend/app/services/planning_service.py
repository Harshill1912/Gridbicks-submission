"""Use case: 'how much wind can I safely count on for this delivery day?'"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time

from ..domain.planning import ErrorQuantilePlanner
from ..domain.selection import UK
from .alignment_service import AlignmentService


@dataclass(frozen=True)
class HourPlan:
    start_time: datetime
    forecast_mw: float
    planned_wind_mw: float
    buffer_mw: float
    actual_mw: float
    covered: bool  # did the planned level hold (actual >= planned)?


@dataclass(frozen=True)
class DayPlan:
    day: date
    confidence: float
    hours: list[HourPlan]
    total_buffer_mwh: float
    shortfalls_naive: int  # hours where actual < forecast
    shortfalls_planned: int  # hours where actual < planned level


@dataclass(frozen=True)
class Backtest:
    confidence: float
    hours: int
    shortfall_rate_naive: float
    shortfall_rate_planned: float
    avg_buffer_mw: float


class PlanningService:
    """Leave-one-day-out: each day is planned using only the OTHER days' errors."""

    def __init__(self, alignment: AlignmentService) -> None:
        self.alignment = alignment

    def _split(self, cutoff: time, day: date):
        points = self.alignment.at_cutoff(cutoff).points
        same = [p for p in points if p.start_time.astimezone(UK).date() == day]
        other = [p for p in points if p.start_time.astimezone(UK).date() != day]
        return same, other

    def day_plan(self, day: date, confidence: float, cutoff: time) -> DayPlan:
        same, other = self._split(cutoff, day)
        planner = ErrorQuantilePlanner(other)
        hours = []
        for p in same:
            plan = planner.plan(p.forecast_mw, confidence)
            hours.append(
                HourPlan(p.start_time, p.forecast_mw, plan.planned_wind_mw, plan.buffer_mw, p.actual_mw,
                         p.actual_mw >= plan.planned_wind_mw)
            )
        return DayPlan(
            day,
            confidence,
            hours,
            total_buffer_mwh=sum(h.buffer_mw for h in hours),  # hourly slots, so MW x 1 h
            shortfalls_naive=sum(1 for h in hours if h.actual_mw < h.forecast_mw),
            shortfalls_planned=sum(1 for h in hours if not h.covered),
        )

    def backtest(self, confidence: float, cutoff: time) -> Backtest:
        points = self.alignment.at_cutoff(cutoff).points
        days = sorted({p.start_time.astimezone(UK).date() for p in points})
        plans = [self.day_plan(d, confidence, cutoff) for d in days]
        hours = [h for plan in plans for h in plan.hours]
        n = len(hours) or 1
        return Backtest(
            confidence,
            len(hours),
            shortfall_rate_naive=sum(p.shortfalls_naive for p in plans) / n,
            shortfall_rate_planned=sum(p.shortfalls_planned for p in plans) / n,
            avg_buffer_mw=sum(h.buffer_mw for h in hours) / n,
        )
