"""Rules for choosing which forecast a buyer would have used for a target time.

Each rule is a small strategy behind the ForecastSelector protocol, so a new
rule is a new class (open/closed) and the aligner never changes.
"""
from __future__ import annotations

from datetime import datetime, time, timedelta, timezone
from typing import Iterable, Protocol
from zoneinfo import ZoneInfo

from .models import Forecast

UK = ZoneInfo("Europe/London")


class ForecastSelector(Protocol):
    def select(self, target: datetime, candidates: Iterable[Forecast]) -> Forecast | None: ...


def _latest(candidates: Iterable[Forecast]) -> Forecast | None:
    return max(candidates, key=lambda f: f.publish_time, default=None)


class DecisionCutoffSelector:
    """Latest forecast published at or before the day-ahead decision cut-off.

    The cut-off is a UK local wall-clock time on the day before the target's
    UK delivery day, so it stays correct across clock changes.
    """

    def __init__(self, cutoff: time = time(10, 0), tz: ZoneInfo = UK) -> None:
        self.cutoff = cutoff
        self.tz = tz

    def deadline_for(self, target: datetime) -> datetime:
        delivery_day = target.astimezone(self.tz).date()
        local = datetime.combine(delivery_day - timedelta(days=1), self.cutoff, tzinfo=self.tz)
        return local.astimezone(timezone.utc)

    def select(self, target: datetime, candidates: Iterable[Forecast]) -> Forecast | None:
        deadline = self.deadline_for(target)
        return _latest(f for f in candidates if f.start_time == target and f.publish_time <= deadline)


class FixedHorizonSelector:
    """Latest forecast published at least `hours` before the target time."""

    def __init__(self, hours: float) -> None:
        self.hours = hours

    def select(self, target: datetime, candidates: Iterable[Forecast]) -> Forecast | None:
        deadline = target - timedelta(hours=self.hours)
        return _latest(f for f in candidates if f.start_time == target and f.publish_time <= deadline)
