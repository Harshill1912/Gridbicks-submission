import { useState } from "react";
import { Card, MetricCard, QueryState } from "../components/Card";
import { ConfidenceSlider } from "../components/Controls";
import { PlanChart } from "../components/charts";
import { useBacktest, usePlan } from "../hooks/useApi";
import { gw, longDate, pct } from "../lib/format";

export function PlannerPage({ day, cutoff }: { day: string; cutoff: string }) {
  const [confidence, setConfidence] = useState(0.9);
  const plan = usePlan(day, confidence, cutoff);
  const backtest = useBacktest(confidence, cutoff);

  return (
    <>
      <Card title="How much wind can you count on?"
        subtitle="Instead of buying against the raw forecast, plan for the wind level that held in the chosen share of past hours.">
        <ConfidenceSlider value={confidence} onChange={setConfidence} />
      </Card>

      <QueryState query={backtest} height={120}>
        {(b) => (
          <div className="metrics">
            <MetricCard label="Short of wind, raw forecast" value={pct(b.shortfall_rate_naive)} tone="warn"
              hint="share of January hours you'd have under-bought" />
            <MetricCard label={`Short of wind, ${Math.round(confidence * 100)}% plan`} value={pct(b.shortfall_rate_planned)} tone="good"
              hint="same hours, using this plan" />
            <MetricCard label="Average extra to buy" value={gw(b.avg_buffer_mw)} hint="buffer per hour vs raw forecast" />
            <MetricCard label="Hours tested" value={String(b.hours)} hint="each day planned only from the other days" />
          </div>
        )}
      </QueryState>

      <QueryState query={plan} height={360}>
        {(p) => (
          <Card title={`Plan for ${longDate(p.day)}`}
            subtitle={<>Extra to procure across the day: <strong>{(p.total_buffer_mwh / 1000).toFixed(1)} GWh</strong>.
              Hours short of wind: <strong>{p.shortfalls_naive}</strong> with the raw forecast → <strong>{p.shortfalls_planned}</strong> with this plan.</>}>
            <PlanChart hours={p.hours} />
          </Card>
        )}
      </QueryState>
    </>
  );
}
