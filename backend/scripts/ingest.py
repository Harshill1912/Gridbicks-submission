"""Download the January 2026 wind snapshot from Elexon into backend/data/.

Usage (from backend/):  python -m scripts.ingest
"""
from __future__ import annotations

from datetime import datetime, time, timedelta, timezone

from app.config import settings
from app.data.csv_store import CsvWindStore
from app.data.elexon_client import ElexonClient


def main() -> None:
    client = ElexonClient()
    first_delivery = settings.decision_from + timedelta(days=1)
    last_delivery = settings.decision_to + timedelta(days=1)

    actuals = client.fetch_actuals(first_delivery, last_delivery)
    # Forecasts published from 2 days before the first decision until the last
    # delivery day ends; this covers every cut-off and every horizon we analyse.
    published_from = datetime.combine(settings.decision_from - timedelta(days=2), time(0), timezone.utc)
    published_to = datetime.combine(last_delivery + timedelta(days=1), time(0), timezone.utc)
    forecasts = client.fetch_forecasts(published_from, published_to)

    CsvWindStore(settings.data_dir).save(actuals, forecasts)
    print(f"actuals: {len(actuals)} rows, forecasts: {len(forecasts)} rows -> {settings.data_dir}")


if __name__ == "__main__":
    main()
