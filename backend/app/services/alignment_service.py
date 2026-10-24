"""Builds (and memoises) aligned forecast/actual pairs for the whole window.

Every other service reads from here, so the matching rule lives in one place.
"""
from __future__ import annotations

from datetime import time
from functools import lru_cache

from ..data.ports import ActualSource, ForecastSource
from ..domain.alignment import Aligner, AlignmentResult
from ..domain.selection import DecisionCutoffSelector, FixedHorizonSelector, ForecastSelector
from .window import DeliveryWindow


class AlignmentService:
    def __init__(self, actuals: ActualSource, forecasts: ForecastSource, window: DeliveryWindow) -> None:
        self.actual_source = actuals
        self.forecast_source = forecasts
        self.window = window
        # Selectors are value-like, so results are cached per rule.
        self.at_cutoff = lru_cache(maxsize=32)(self._at_cutoff)
        self.at_horizon = lru_cache(maxsize=64)(self._at_horizon)

    def _align(self, selector: ForecastSelector) -> AlignmentResult:
        start, end = self.window.bounds()
        return Aligner(selector).align(
            self.actual_source.get_actuals(start, end), self.forecast_source.get_forecasts(start, end)
        )

    def _at_cutoff(self, cutoff: time) -> AlignmentResult:
        return self._align(DecisionCutoffSelector(cutoff))

    def _at_horizon(self, hours: float) -> AlignmentResult:
        return self._align(FixedHorizonSelector(hours))
