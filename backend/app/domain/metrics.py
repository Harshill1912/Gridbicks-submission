"""Forecast-error metrics. One class per metric; add a metric by adding a class."""
from __future__ import annotations

import math
from typing import Callable, Protocol, Sequence

from .models import AlignedPoint


class Metric(Protocol):
    name: str

    def compute(self, points: Sequence[AlignedPoint]) -> float | None: ...


def _errors(points: Sequence[AlignedPoint]) -> list[float]:
    return [p.error_mw for p in points]


class Bias:
    """Mean of (actual - forecast). Negative = forecasts run too high."""

    name = "bias_mw"

    def compute(self, points):
        e = _errors(points)
        return sum(e) / len(e) if e else None


class MAE:
    name = "mae_mw"

    def compute(self, points):
        e = _errors(points)
        return sum(abs(x) for x in e) / len(e) if e else None


class RMSE:
    name = "rmse_mw"

    def compute(self, points):
        e = _errors(points)
        return math.sqrt(sum(x * x for x in e) / len(e)) if e else None


class MAPE:
    """Mean absolute % error, skipping near-zero actuals where % is meaningless."""

    name = "mape_pct"

    def __init__(self, min_actual_mw: float = 500.0) -> None:
        self.min_actual_mw = min_actual_mw

    def compute(self, points):
        usable = [p for p in points if p.actual_mw >= self.min_actual_mw]
        if not usable:
            return None
        return 100 * sum(abs(p.error_mw) / p.actual_mw for p in usable) / len(usable)


def quantile(values: Sequence[float], q: float) -> float | None:
    """Linear-interpolated quantile, q in [0, 1]."""
    if not values:
        return None
    s = sorted(values)
    pos = (len(s) - 1) * q
    lo, hi = math.floor(pos), math.ceil(pos)
    return s[lo] + (s[hi] - s[lo]) * (pos - lo)


class ErrorQuantile:
    def __init__(self, q: float) -> None:
        self.q = q
        self.name = f"p{round(q * 100)}_error_mw"

    def compute(self, points):
        return quantile(_errors(points), self.q)


def default_metrics() -> list[Metric]:
    return [Bias(), MAE(), RMSE(), MAPE(), ErrorQuantile(0.1), ErrorQuantile(0.9)]


class MetricSuite:
    def __init__(self, metrics: Sequence[Metric] | None = None) -> None:
        self.metrics = list(metrics) if metrics is not None else default_metrics()

    def compute(self, points: Sequence[AlignedPoint]) -> dict[str, float | None]:
        return {m.name: m.compute(points) for m in self.metrics}

    def grouped(
        self, points: Sequence[AlignedPoint], key: Callable[[AlignedPoint], object]
    ) -> dict[object, dict[str, float | None]]:
        groups: dict[object, list[AlignedPoint]] = {}
        for p in points:
            groups.setdefault(key(p), []).append(p)
        return {k: {"count": len(v), **self.compute(v)} for k, v in sorted(groups.items())}
