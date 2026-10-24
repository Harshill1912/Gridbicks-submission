"""Settings, overridable by environment variables."""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import date, time
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class Settings:
    data_dir: Path = field(default_factory=lambda: Path(os.getenv("DATA_DIR", BACKEND_DIR / "data")))
    # Purchase decisions made 1-31 Jan 2026 deliver on 2 Jan - 1 Feb 2026.
    decision_from: date = date(2026, 1, 1)
    decision_to: date = date(2026, 1, 31)
    # GB day-ahead auction gate, UK local time, on the day before delivery.
    default_cutoff: time = time(10, 0)
    cors_origins: tuple[str, ...] = tuple(os.getenv("CORS_ORIGINS", "*").split(","))


settings = Settings()
