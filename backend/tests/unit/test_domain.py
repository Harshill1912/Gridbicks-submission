from datetime import datetime, time, timezone

import pytest

from app.domain.alignment import Aligner
from app.domain.metrics import MAE, MAPE, RMSE, Bias, ErrorQuantile, MetricSuite, quantile
from app.domain.models import Actual, AlignedPoint, Forecast
from app.domain.planning import ErrorQuantilePlanner
from app.domain.selection import DecisionCutoffSelector, FixedHorizonSelector


def utc(*args):
    return datetime(*args, tzinfo=timezone.utc)


TARGET = utc(2026, 1, 15, 18)  # delivery 15 Jan -> decision cut-off 14 Jan 10:00 UK (= UTC in winter)


def fc(publish, mw=1000.0, target=TARGET):
    return Forecast(target, publish, mw)


class TestDecisionCutoffSelector:
    sel = DecisionCutoffSelector(time(10, 0))

    def test_deadline_is_previous_uk_day_at_cutoff(self):
        assert self.sel.deadline_for(TARGET) == utc(2026, 1, 14, 10)

    def test_deadline_uses_uk_local_time_in_summer(self):
        # BST: 10:00 UK on 14 Jul = 09:00 UTC
        assert self.sel.deadline_for(utc(2026, 7, 15, 12)) == utc(2026, 7, 14, 9)

    def test_picks_latest_before_cutoff(self):
        early, latest, late = fc(utc(2026, 1, 14, 7, 30), 1), fc(utc(2026, 1, 14, 9, 30), 2), fc(utc(2026, 1, 14, 11, 30), 3)
        assert self.sel.select(TARGET, [late, early, latest]) is latest

    def test_published_exactly_at_cutoff_is_usable(self):
        on_time = fc(utc(2026, 1, 14, 10))
        assert self.sel.select(TARGET, [on_time]) is on_time

    def test_published_after_cutoff_is_rejected(self):
        assert self.sel.select(TARGET, [fc(utc(2026, 1, 14, 10, 0, 1))]) is None

    def test_ignores_other_targets(self):
        other = fc(utc(2026, 1, 14, 9), target=utc(2026, 1, 15, 19))
        assert self.sel.select(TARGET, [other]) is None


def test_fixed_horizon_selector():
    sel = FixedHorizonSelector(hours=12)
    ok, too_late = fc(utc(2026, 1, 15, 6)), fc(utc(2026, 1, 15, 7))
    assert sel.select(TARGET, [ok, too_late]) is ok


def test_aligner_pairs_and_reports_missing():
    actuals = [Actual(TARGET, 800), Actual(utc(2026, 1, 15, 18, 30), 810), Actual(utc(2026, 1, 15, 19), 900)]
    forecasts = [fc(utc(2026, 1, 14, 9), 1000), fc(utc(2026, 1, 14, 11), 1100, target=utc(2026, 1, 15, 19))]
    result = Aligner(DecisionCutoffSelector()).align(actuals, forecasts)
    assert [(p.actual_mw, p.forecast_mw) for p in result.points] == [(800, 1000)]
    assert result.missing_forecast == [utc(2026, 1, 15, 19)]  # only a post-cut-off forecast existed
    assert result.points[0].error_mw == -200
    assert result.points[0].horizon_h == 33


# Worked example: errors -2, +1, -3, 0 (GW)
POINTS = [AlignedPoint(TARGET, a, f, utc(2026, 1, 14, 9)) for f, a in [(10, 8), (6, 7), (9, 6), (5, 5)]]


def test_metrics_match_hand_calculation():
    assert Bias().compute(POINTS) == -1
    assert MAE().compute(POINTS) == 1.5
    assert RMSE().compute(POINTS) == pytest.approx(3.5**0.5)
    assert MAPE(min_actual_mw=0).compute(POINTS) == pytest.approx(100 * (2 / 8 + 1 / 7 + 3 / 6 + 0) / 4)


def test_mape_skips_low_actuals():
    assert MAPE(min_actual_mw=1000).compute(POINTS) is None


def test_metrics_on_empty_are_none():
    assert all(v is None for v in MetricSuite().compute([]).values())


def test_quantile_interpolates():
    assert quantile([0, 10], 0.1) == 1
    assert ErrorQuantile(0.1).name == "p10_error_mw"


def test_grouped_metrics_count_each_group():
    groups = MetricSuite([MAE()]).grouped(POINTS, key=lambda p: p.forecast_mw > 7)
    assert groups[True] == {"count": 2, "mae_mw": 2.5}


class TestPlanner:
    history = [AlignedPoint(TARGET, 1000 + e, 1000, utc(2026, 1, 14, 9)) for e in range(-100, 1)]  # errors -100..0

    def test_plan_subtracts_low_quantile(self):
        plan = ErrorQuantilePlanner(self.history).plan(5000, 0.9)
        assert plan.planned_wind_mw == pytest.approx(4910)
        assert plan.buffer_mw == pytest.approx(90)

    def test_plan_never_negative(self):
        assert ErrorQuantilePlanner(self.history).plan(10, 0.99).planned_wind_mw == 0

    def test_shortfall_rate_matches_confidence(self):
        assert ErrorQuantilePlanner(self.history).shortfall_rate(0.9) == pytest.approx(0.1, abs=0.01)

    def test_rejects_bad_confidence(self):
        with pytest.raises(ValueError):
            ErrorQuantilePlanner(self.history).plan(100, 1.0)
