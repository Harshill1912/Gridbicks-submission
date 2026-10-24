"""Core value objects. Pure data, no I/O."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Actual:
    """Measured national wind generation for one settlement period."""

    start_time: datetime  # UTC
    generation_mw: float


@dataclass(frozen=True)
class Forecast:
    """One forecast value for a target time, as published at publish_time."""

    start_time: datetime  # UTC, target time
    publish_time: datetime  # UTC, when the forecast was created
    generation_mw: float

    @property
    def horizon_h(self) -> float:
        return (self.start_time - self.publish_time).total_seconds() / 3600


@dataclass(frozen=True)
class AlignedPoint:
    """A target time paired with the forecast a buyer would have used."""

    start_time: datetime
    actual_mw: float
    forecast_mw: float
    publish_time: datetime

    @property
    def error_mw(self) -> float:
        """Actual minus forecast. Negative = forecast was too optimistic."""
        return self.actual_mw - self.forecast_mw

    @property
    def horizon_h(self) -> float:
        return (self.start_time - self.publish_time).total_seconds() / 3600
