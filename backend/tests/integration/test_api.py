"""API tests against a small in-memory dataset (no files, no network)."""
from datetime import date, datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from app.api.deps import build_container, get_container
from app.domain.models import Actual, Forecast
from app.main import create_app
from app.services.window import DeliveryWindow

DAY1, DAY2 = date(2026, 1, 2), date(2026, 1, 3)


class FakeStore:
    """Two delivery days. Forecast is always 10,000 MW; actual is 9,000 + hour * 40."""

    def __init__(self):
        self.actuals, self.forecasts = [], []
        for d in (DAY1, DAY2):
            base = datetime(d.year, d.month, d.day, tzinfo=timezone.utc)
            for half in range(48):
                t = base + timedelta(minutes=30 * half)
                self.actuals.append(Actual(t, 9000 + (half // 2) * 40))
                if half % 2 == 0:
                    eve = base - timedelta(days=1)
                    self.forecasts.append(Forecast(t, eve + timedelta(hours=9, minutes=30), 10000))  # before cut-off
                    self.forecasts.append(Forecast(t, eve + timedelta(hours=11, minutes=30), 99999))  # after cut-off

    def get_actuals(self, start, end):
        return [a for a in self.actuals if start <= a.start_time < end]

    def get_forecasts(self, start, end):
        return [f for f in self.forecasts if start <= f.start_time < end]


@pytest.fixture
def client():
    app = create_app()
    container = build_container(FakeStore(), DeliveryWindow(DAY1, DAY2))
    app.dependency_overrides[get_container] = lambda: container
    return TestClient(app)


def test_health(client):
    body = client.get("/api/health").json()
    assert body == {
        "status": "ok", "first_delivery_day": "2026-01-02", "last_delivery_day": "2026-01-03",
        "actual_rows": 96, "forecast_rows": 96,
    }


def test_series_uses_only_pre_cutoff_forecast(client):
    body = client.get("/api/series", params={"day": "2026-01-02"}).json()
    assert body["deadline"] == "2026-01-01T10:00:00Z"
    pts = body["points"]
    assert len(pts) == 48  # half-hourly actuals
    hourly = [p for p in pts if p["forecast_mw"] is not None]
    assert len(hourly) == 24 and {p["forecast_mw"] for p in hourly} == {10000}
    assert pts[1]["forecast_mw"] is None  # :30 slot has no hourly forecast
    # Band = forecast + P10/P90 of the OTHER day's errors (-1000..-80 in steps of 40)
    assert hourly[0]["band_low_mw"] == pytest.approx(10000 - 908)
    assert hourly[0]["band_high_mw"] == pytest.approx(10000 - 172)


def test_later_cutoff_picks_later_forecast(client):
    body = client.get("/api/series", params={"day": "2026-01-02", "cutoff": "12:00"}).json()
    assert {p["forecast_mw"] for p in body["points"] if p["forecast_mw"]} == {99999}


def test_series_rejects_day_outside_window(client):
    r = client.get("/api/series", params={"day": "2026-03-01"})
    assert r.status_code == 404


def test_metrics_summary(client):
    body = client.get("/api/metrics").json()
    assert body["count"] == 48 and body["missing_forecast"] == 0
    # errors are -1000, -960, ... -80 for each hour of each day
    assert body["metrics"]["bias_mw"] == pytest.approx(-540)
    assert body["metrics"]["mae_mw"] == pytest.approx(540)


def test_breakdowns(client):
    hours = client.get("/api/metrics/by-hour").json()
    assert len(hours) == 24 and hours[0] == {**hours[0], "hour": 0, "count": 2, "bias_mw": -1000}
    levels = client.get("/api/metrics/by-wind-level").json()
    assert [r["forecast_from_mw"] for r in levels] == [9000]
    horizons = client.get("/api/metrics/by-horizon").json()
    assert horizons[0]["horizon_h"] == 1 and horizons[0]["count"] == 48
    assert len(client.get("/api/metrics/scatter").json()) == 48


def test_plan_and_backtest(client):
    plan = client.get("/api/plan", params={"day": "2026-01-02", "confidence": 0.9}).json()
    assert len(plan["hours"]) == 24
    assert all(h["planned_wind_mw"] < h["forecast_mw"] for h in plan["hours"])
    assert plan["shortfalls_naive"] == 24  # forecast always too high in the fake data
    bt = client.get("/api/plan/backtest", params={"confidence": 0.9}).json()
    assert bt["shortfall_rate_planned"] < bt["shortfall_rate_naive"] == 1.0


def test_confidence_validation(client):
    assert client.get("/api/plan/backtest", params={"confidence": 1.5}).status_code == 422
