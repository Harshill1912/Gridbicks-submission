import { Card, MetricCard, QueryState } from "../components/Card";
import { ForecastChart } from "../components/charts";
import { useSeries } from "../hooks/useApi";
import { gw, longDate, signedGw, ukDateTime } from "../lib/format";
import type { SeriesPoint } from "../api/types";

function daySummary(points: SeriesPoint[]) {
  const paired = points.filter((p) => p.forecast_mw != null && p.actual_mw != null);
  const err = paired.map((p) => p.actual_mw! - p.forecast_mw!);
  const mean = (xs: number[]) => (xs.length ? xs.reduce((a, b) => a + b, 0) / xs.length : null);
  const publishTimes = [...new Set(paired.map((p) => p.publish_time!))].sort();
  return {
    avgForecast: mean(paired.map((p) => p.forecast_mw!)),
    avgActual: mean(paired.map((p) => p.actual_mw!)),
    bias: mean(err),
    mae: mean(err.map(Math.abs)),
    latestPublish: publishTimes.at(-1) ?? null,
  };
}

export function ForecastPage({ day, cutoff }: { day: string; cutoff: string }) {
  const series = useSeries(day, cutoff);
  return (
    <QueryState query={series} height={480}>
      {(s) => {
        const sum = daySummary(s.points);
        return (
          <>
            <div className="metrics">
              <MetricCard label="Forecast you'd have bought on" value={gw(sum.avgForecast)} hint="average across the day" />
              <MetricCard label="Wind that actually came" value={gw(sum.avgActual)} hint="average across the day" />
              <MetricCard label="Bias on this day" value={signedGw(sum.bias)} tone={sum.bias != null && sum.bias < 0 ? "warn" : "good"}
                hint={sum.bias != null && sum.bias < 0 ? "forecast was too optimistic" : "forecast was cautious"} />
              <MetricCard label="Typical miss" value={gw(sum.mae)} hint="mean absolute error, hourly" />
            </div>
            <Card
              title={`Wind on ${longDate(s.day)}`}
              subtitle={<>Forecast shown is the latest one published before the cut-off at <strong>{ukDateTime(s.deadline)}</strong>
                {sum.latestPublish && <> (published {ukDateTime(sum.latestPublish)})</>}. Later forecasts arrived too late to buy on.</>}
            >
              <ForecastChart points={s.points} />
              <p className="footnote">Likely range comes from forecast errors on the other January days, so this day's outcome never shapes its own band.</p>
            </Card>
          </>
        );
      }}
    </QueryState>
  );
}
