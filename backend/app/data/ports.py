"""Interfaces the services depend on (dependency inversion)."""
from __future__ import annotations

from datetime import date, datetime
from typing import Protocol

from ..domain.models import Actual, Forecast


class ActualSource(Protocol):
    def get_actuals(self, start: datetime, end: datetime) -> list[Actual]:
        """Actuals with start_time in [start, end)."""
        ...


class ForecastSource(Protocol):
    def get_forecasts(self, start: datetime, end: datetime) -> list[Forecast]:
        """Forecasts whose target start_time is in [start, end)."""
        ...


class RemoteWindApi(Protocol):
    """Raw upstream access, used only by ingestion."""

    def fetch_actuals(self, day_from: date, day_to: date) -> list[Actual]: ...

    def fetch_forecasts(self, published_from: datetime, published_to: datetime) -> list[Forecast]: ...
