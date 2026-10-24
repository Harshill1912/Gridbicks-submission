"""HTTP response contracts. Kept separate from domain objects so either can change."""
from __future__ import annotations

from datetime import date, datetime, time

from pydantic import BaseModel, ConfigDict


class _Out(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Health(_Out):
    status: str
    first_delivery_day: date
    last_delivery_day: date
    actual_rows: int
    forecast_rows: int


class SeriesPointOut(_Out):
    start_time: datetime
    actual_mw: float | None
    forecast_mw: float | None
    publish_time: datetime | None
    band_low_mw: float | None
    band_high_mw: float | None


class DaySeriesOut(_Out):
    day: date
    cutoff: time
    deadline: datetime
    points: list[SeriesPointOut]


class Metrics(_Out):
    bias_mw: float | None
    mae_mw: float | None
    rmse_mw: float | None
    mape_pct: float | None
    p10_error_mw: float | None
    p90_error_mw: float | None


class SummaryOut(_Out):
    cutoff: time
    count: int
    missing_forecast: int
    metrics: Metrics


class HorizonRow(Metrics):
    horizon_h: float
    count: int


class HourRow(Metrics):
    hour: int
    count: int


class WindLevelRow(Metrics):
    forecast_from_mw: int
    count: int


class ScatterPoint(_Out):
    start_time: datetime
    forecast_mw: float
    actual_mw: float
    error_mw: float


class HourPlanOut(_Out):
    start_time: datetime
    forecast_mw: float
    planned_wind_mw: float
    buffer_mw: float
    actual_mw: float
    covered: bool


class DayPlanOut(_Out):
    day: date
    confidence: float
    hours: list[HourPlanOut]
    total_buffer_mwh: float
    shortfalls_naive: int
    shortfalls_planned: int


class BacktestOut(_Out):
    confidence: float
    hours: int
    shortfall_rate_naive: float
    shortfall_rate_planned: float
    avg_buffer_mw: float
