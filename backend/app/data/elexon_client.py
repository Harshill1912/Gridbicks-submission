"""Thin HTTP client for the Elexon BMRS dataset streams."""
from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from datetime import date, datetime, timedelta, timezone

from ..domain.models import Actual, Forecast

BASE_URL = "https://data.elexon.co.uk/bmrs/api/v1/datasets"


def parse_ts(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


class ElexonClient:
    def __init__(self, base_url: str = BASE_URL, timeout_s: float = 30, retries: int = 3) -> None:
        self.base_url = base_url
        self.timeout_s = timeout_s
        self.retries = retries

    def _get(self, dataset: str, params: dict[str, str]) -> list[dict]:
        url = f"{self.base_url}/{dataset}/stream?{urllib.parse.urlencode(params)}"
        for attempt in range(self.retries):
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "wind-forecast-monitor/1.0", "Accept": "application/json"})
                with urllib.request.urlopen(req, timeout=self.timeout_s) as resp:
                    return json.load(resp)
            except OSError:
                if attempt == self.retries - 1:
                    raise
                time.sleep(2**attempt)
        return []

    def fetch_actuals(self, day_from: date, day_to: date) -> list[Actual]:
        """Wind outturn for settlement dates day_from..day_to inclusive."""
        rows = self._get(
            "FUELHH",
            {"settlementDateFrom": day_from.isoformat(), "settlementDateTo": day_to.isoformat(), "fuelType": "WIND"},
        )
        return [Actual(parse_ts(r["startTime"]), float(r["generation"])) for r in rows if r.get("fuelType") == "WIND"]

    def fetch_forecasts(self, published_from: datetime, published_to: datetime) -> list[Forecast]:
        """Forecasts published in [published_from, published_to), fetched a day at a time."""
        out: list[Forecast] = []
        cursor = published_from
        while cursor < published_to:
            nxt = min(cursor + timedelta(days=1), published_to)
            rows = self._get(
                "WINDFOR",
                {"publishDateTimeFrom": _iso(cursor), "publishDateTimeTo": _iso(nxt)},
            )
            out += [
                Forecast(parse_ts(r["startTime"]), parse_ts(r["publishTime"]), float(r["generation"]))
                for r in rows
                if cursor <= parse_ts(r["publishTime"]) < nxt  # API bounds are inclusive
            ]
            cursor = nxt
        return out


def _iso(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
