"""HTTP routes. Thin: validate input, call one service, shape the response."""
from __future__ import annotations

from datetime import date, time

from fastapi import APIRouter, Depends, HTTPException, Query

from ..config import settings
from .deps import Container, get_container
from .schemas import (
    BacktestOut,
    DayPlanOut,
    DaySeriesOut,
    Health,
    HorizonRow,
    HourRow,
    ScatterPoint,
    SummaryOut,
    WindLevelRow,
)

router = APIRouter(prefix="/api")

Cutoff = Query(settings.default_cutoff, description="Decision cut-off, UK local time on the day before delivery")
Confidence = Query(0.9, gt=0, lt=1, description="Share of hours the planned wind level should hold")


def _check_day(day: date, c: Container) -> None:
    if not c.window.contains(day):
        raise HTTPException(404, f"No data for {day}; delivery days are {c.window.first_day} to {c.window.last_day}")


@router.get("/health", response_model=Health)
def health(c: Container = Depends(get_container)):
    start, end = c.window.bounds()
    return Health(
        status="ok",
        first_delivery_day=c.window.first_day,
        last_delivery_day=c.window.last_day,
        actual_rows=len(c.store.get_actuals(start, end)),
        forecast_rows=len(c.store.get_forecasts(start, end)),
    )


@router.get("/series", response_model=DaySeriesOut)
def series(day: date, cutoff: time = Cutoff, c: Container = Depends(get_container)):
    _check_day(day, c)
    return c.forecasts.day_series(day, cutoff)


@router.get("/metrics", response_model=SummaryOut)
def metrics(cutoff: time = Cutoff, c: Container = Depends(get_container)):
    s = c.accuracy.summary(cutoff)
    return {"cutoff": cutoff, "count": s.count, "missing_forecast": s.missing_forecast, "metrics": s.metrics}


@router.get("/metrics/by-horizon", response_model=list[HorizonRow])
def by_horizon(c: Container = Depends(get_container)):
    return c.accuracy.by_horizon()


@router.get("/metrics/by-hour", response_model=list[HourRow])
def by_hour(cutoff: time = Cutoff, c: Container = Depends(get_container)):
    return c.accuracy.by_hour_of_day(cutoff)


@router.get("/metrics/by-wind-level", response_model=list[WindLevelRow])
def by_wind_level(cutoff: time = Cutoff, c: Container = Depends(get_container)):
    return c.accuracy.by_wind_level(cutoff)


@router.get("/metrics/scatter", response_model=list[ScatterPoint])
def scatter(cutoff: time = Cutoff, c: Container = Depends(get_container)):
    return [
        ScatterPoint(start_time=p.start_time, forecast_mw=p.forecast_mw, actual_mw=p.actual_mw, error_mw=p.error_mw)
        for p in c.accuracy.scatter(cutoff)
    ]


@router.get("/plan", response_model=DayPlanOut)
def plan(day: date, confidence: float = Confidence, cutoff: time = Cutoff, c: Container = Depends(get_container)):
    _check_day(day, c)
    return c.planning.day_plan(day, confidence, cutoff)


@router.get("/plan/backtest", response_model=BacktestOut)
def backtest(confidence: float = Confidence, cutoff: time = Cutoff, c: Container = Depends(get_container)):
    return c.planning.backtest(confidence, cutoff)
