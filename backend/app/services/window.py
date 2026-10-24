"""The analysis window: delivery days whose purchase decision falls in January."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from ..domain.selection import UK


@dataclass(frozen=True)
class DeliveryWindow:
    first_day: date
    last_day: date

    @classmethod
    def for_decisions(cls, decision_from: date, decision_to: date) -> "DeliveryWindow":
        return cls(decision_from + timedelta(days=1), decision_to + timedelta(days=1))

    def contains(self, day: date) -> bool:
        return self.first_day <= day <= self.last_day

    @staticmethod
    def day_bounds(day: date) -> tuple[datetime, datetime]:
        """UTC [start, end) of a UK delivery day."""
        start = datetime.combine(day, time(0), tzinfo=UK).astimezone(timezone.utc)
        end = datetime.combine(day + timedelta(days=1), time(0), tzinfo=UK).astimezone(timezone.utc)
        return start, end

    def bounds(self) -> tuple[datetime, datetime]:
        return self.day_bounds(self.first_day)[0], self.day_bounds(self.last_day)[1]
