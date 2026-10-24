"""Composition root: the only place concrete classes are chosen.

Tests swap the store by overriding `get_container`.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

from ..config import settings
from ..data.csv_store import CsvWindStore
from ..services.accuracy_service import AccuracyService
from ..services.alignment_service import AlignmentService
from ..services.forecast_service import ForecastService
from ..services.planning_service import PlanningService
from ..services.window import DeliveryWindow


@dataclass
class Container:
    window: DeliveryWindow
    store: CsvWindStore
    forecasts: ForecastService
    accuracy: AccuracyService
    planning: PlanningService


def build_container(store, window: DeliveryWindow) -> Container:
    alignment = AlignmentService(store, store, window)
    return Container(
        window=window,
        store=store,
        forecasts=ForecastService(alignment, store),
        accuracy=AccuracyService(alignment),
        planning=PlanningService(alignment),
    )


@lru_cache
def get_container() -> Container:
    window = DeliveryWindow.for_decisions(settings.decision_from, settings.decision_to)
    return build_container(CsvWindStore(settings.data_dir), window)
