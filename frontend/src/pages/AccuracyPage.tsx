import { Card, MetricCard, QueryState } from "../components/Card";
import { HorizonChart, HourChart, ScatterPlot } from "../components/charts";
import { useByHorizon, useByHour, useScatter, useSummary } from "../hooks/useApi";
import { gw, signedGw } from "../lib/format";

export function AccuracyPage({ cutoff }: { cutoff: string }) {
  const summary = useSummary(cutoff);
  const horizon = useByHorizon();
  const hour = useByHour(cutoff);
  const scatter = useScatter(cutoff);

  return (
    <>
      <QueryState query={summary} height={120}>
        {({ metrics: m, count }) => (
          <>
            <div className="metrics">
              <MetricCard label="Bias" value={signedGw(m.bias_mw)} tone={m.bias_mw != null && m.bias_mw < 0 ? "warn" : "neutral"}
                hint={m.bias_mw != null && m.bias_mw < 0 ? "forecasts run too high on average" : "forecasts run low on average"} />
              <MetricCard label="Typical miss (MAE)" value={gw(m.mae_mw)} hint={`${m.mape_pct?.toFixed(0) ?? "–"}% of actual wind`} />
              <MetricCard label="Big-miss weighted (RMSE)" value={gw(m.rmse_mw)} hint="penalises large errors more" />
              <MetricCard label="80% of the time" value={`${signedGw(m.p10_error_mw)} … ${signedGw(m.p90_error_mw)}`}
                hint="actual vs forecast (P10 to P90)" />
            </div>
            <p className="muted small">Based on {count} hourly delivery periods, 2 Jan – 1 Feb 2026, forecasts as known at the {cutoff} cut-off.</p>
          </>
        )}
      </QueryState>

      <div className="grid-2">
        <Card title="Does an earlier forecast miss more?" subtitle="Error by how far ahead the forecast was published">
          <QueryState query={horizon} height={280}>{(rows) => <HorizonChart rows={rows} />}</QueryState>
        </Card>
        <Card title="When in the day are forecasts weakest?" subtitle="Error by delivery hour">
          <QueryState query={hour} height={280}>{(rows) => <HourChart rows={rows} />}</QueryState>
        </Card>
      </div>

      <Card title="Forecast vs actual, every hour of the month" subtitle="Points below the dashed line are hours when the wind fell short of the forecast">
        <QueryState query={scatter} height={300}>{(pts) => <ScatterPlot points={pts} />}</QueryState>
      </Card>
    </>
  );
}
