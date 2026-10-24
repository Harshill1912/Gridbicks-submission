"""Local snapshot of the upstream data, stored as CSV.

January 2026 is history, so the app serves from this snapshot: fast, and it
keeps working when Elexon is slow or down.
"""
from __future__ import annotations

import csv
from datetime import datetime
from pathlib import Path
from typing import Iterable

from ..domain.models import Actual, Forecast
from .elexon_client import parse_ts

ACTUALS_FILE = "actuals_wind.csv"
FORECASTS_FILE = "forecasts_wind.csv"


class CsvWindStore:
    """Implements ActualSource and ForecastSource over two CSV files."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self._actuals: list[Actual] | None = None
        self._forecasts: list[Forecast] | None = None

    # writing (ingestion)
    def save(self, actuals: Iterable[Actual], forecasts: Iterable[Forecast]) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)
        actual_rows = {a.start_time: a for a in actuals}  # dedupe by target time
        forecast_rows = {(f.start_time, f.publish_time): f for f in forecasts}
        with open(self.data_dir / ACTUALS_FILE, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["start_time", "generation_mw"])
            for a in sorted(actual_rows.values(), key=lambda a: a.start_time):
                w.writerow([a.start_time.isoformat(), a.generation_mw])
        with open(self.data_dir / FORECASTS_FILE, "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["start_time", "publish_time", "generation_mw"])
            for f in sorted(forecast_rows.values(), key=lambda f: (f.start_time, f.publish_time)):
                w.writerow([f.start_time.isoformat(), f.publish_time.isoformat(), f.generation_mw])
        self._actuals = self._forecasts = None

    # reading (serving)
    def _load(self) -> None:
        if self._actuals is not None:
            return
        with open(self.data_dir / ACTUALS_FILE, newline="") as fh:
            self._actuals = [Actual(parse_ts(r["start_time"]), float(r["generation_mw"])) for r in csv.DictReader(fh)]
        with open(self.data_dir / FORECASTS_FILE, newline="") as fh:
            self._forecasts = [
                Forecast(parse_ts(r["start_time"]), parse_ts(r["publish_time"]), float(r["generation_mw"]))
                for r in csv.DictReader(fh)
            ]

    def get_actuals(self, start: datetime, end: datetime) -> list[Actual]:
        self._load()
        return [a for a in self._actuals if start <= a.start_time < end]

    def get_forecasts(self, start: datetime, end: datetime) -> list[Forecast]:
        self._load()
        return [f for f in self._forecasts if start <= f.start_time < end]
