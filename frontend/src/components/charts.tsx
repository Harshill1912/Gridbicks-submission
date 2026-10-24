// All charts in one place so they share colours, axes and tooltips.
import {
  Area, Bar, CartesianGrid, ComposedChart, Legend, Line, ReferenceLine, ResponsiveContainer,
  Scatter, ScatterChart, Tooltip, XAxis, YAxis, ZAxis,
} from "recharts";
import type { HorizonRow, HourPlan, HourRow, ScatterPoint, SeriesPoint } from "../api/types";
import { gw, signedGw, ukTime } from "../lib/format";

const C = {
  actual: "var(--c-actual)",
  forecast: "var(--c-forecast)",
  band: "var(--c-band)",
  plan: "var(--c-plan)",
  bad: "var(--c-bad)",
  grid: "var(--c-grid)",
  axis: "var(--c-axis)",
};

const axis = { stroke: C.axis, tick: { fill: C.axis, fontSize: 12 }, tickLine: false };
const gwTick = (v: number) => `${(v / 1000).toFixed(0)}`;
const tooltipStyle = {
  contentStyle: { background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 8, color: "var(--text)" },
  labelStyle: { color: "var(--muted)" },
};

export function ForecastChart({ points }: { points: SeriesPoint[] }) {
  const data = points.map((p) => ({
    t: ukTime(p.start_time),
    actual: p.actual_mw,
    forecast: p.forecast_mw,
    band: p.band_low_mw != null && p.band_high_mw != null ? [p.band_low_mw, p.band_high_mw] : null,
  }));
  return (
    <ResponsiveContainer width="100%" height={340}>
      <ComposedChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid stroke={C.grid} vertical={false} />
        <XAxis dataKey="t" {...axis} interval={5} />
        <YAxis {...axis} tickFormatter={gwTick} width={40} label={{ value: "GW", angle: -90, position: "insideLeft", fill: C.axis }} />
        <Tooltip {...tooltipStyle} formatter={(v, name) => [Array.isArray(v) ? `${gw(v[0] as number)} – ${gw(v[1] as number)}` : gw(v as number), name]} />
        <Legend />
        <Area dataKey="band" name="Likely range (P10–P90)" fill={C.band} stroke="none" connectNulls isAnimationActive={false} />
        <Line dataKey="forecast" name="Forecast at decision time" stroke={C.forecast} strokeWidth={2.5} dot={false} connectNulls isAnimationActive={false} />
        <Line dataKey="actual" name="Actual generation" stroke={C.actual} strokeWidth={2} dot={false} isAnimationActive={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

export function HorizonChart({ rows }: { rows: HorizonRow[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <ComposedChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 16 }}>
        <CartesianGrid stroke={C.grid} vertical={false} />
        <XAxis dataKey="horizon_h" {...axis} label={{ value: "Hours ahead the forecast was made", position: "insideBottom", offset: -8, fill: C.axis }} />
        <YAxis {...axis} tickFormatter={(v) => (v / 1000).toFixed(1)} width={40} />
        <Tooltip {...tooltipStyle} labelFormatter={(h) => `${h} h ahead`} formatter={(v, name) => [signedGw(v as number, 2), name]} />
        <Legend verticalAlign="top" />
        <Line dataKey="mae_mw" name="Typical miss (MAE)" stroke={C.forecast} strokeWidth={2.5} isAnimationActive={false} />
        <Line dataKey="rmse_mw" name="Big-miss weighted (RMSE)" stroke={C.bad} strokeWidth={2} strokeDasharray="4 3" isAnimationActive={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

export function HourChart({ rows }: { rows: HourRow[] }) {
  return (
    <ResponsiveContainer width="100%" height={280}>
      <ComposedChart data={rows} margin={{ top: 8, right: 8, left: 0, bottom: 16 }}>
        <CartesianGrid stroke={C.grid} vertical={false} />
        <XAxis dataKey="hour" {...axis} tickFormatter={(h) => `${String(h).padStart(2, "0")}h`} interval={2}
          label={{ value: "Delivery hour (UK)", position: "insideBottom", offset: -8, fill: C.axis }} />
        <YAxis {...axis} tickFormatter={(v) => (v / 1000).toFixed(1)} width={40} />
        <ReferenceLine y={0} stroke={C.axis} />
        <Tooltip {...tooltipStyle} labelFormatter={(h) => `${String(h).padStart(2, "0")}:00`} formatter={(v, name) => [signedGw(v as number, 2), name]} />
        <Legend verticalAlign="top" />
        <Bar dataKey="mae_mw" name="Typical miss (MAE)" fill={C.forecast} radius={[3, 3, 0, 0]} isAnimationActive={false} />
        <Line dataKey="bias_mw" name="Bias (− = forecast too high)" stroke={C.bad} strokeWidth={2} dot={false} isAnimationActive={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}

export function ScatterPlot({ points }: { points: ScatterPoint[] }) {
  const max = Math.max(...points.flatMap((p) => [p.forecast_mw, p.actual_mw]), 1000);
  return (
    <ResponsiveContainer width="100%" height={300}>
      <ScatterChart margin={{ top: 8, right: 8, left: 0, bottom: 16 }}>
        <CartesianGrid stroke={C.grid} />
        <XAxis type="number" dataKey="forecast_mw" name="Forecast" domain={[0, max]} {...axis} tickFormatter={gwTick}
          label={{ value: "Forecast (GW)", position: "insideBottom", offset: -8, fill: C.axis }} />
        <YAxis type="number" dataKey="actual_mw" name="Actual" domain={[0, max]} {...axis} tickFormatter={gwTick} width={40}
          label={{ value: "Actual (GW)", angle: -90, position: "insideLeft", fill: C.axis }} />
        <ZAxis range={[14, 14]} />
        <ReferenceLine segment={[{ x: 0, y: 0 }, { x: max, y: max }]} stroke={C.axis} strokeDasharray="4 4" label={{ value: "perfect", fill: C.axis, position: "insideTopLeft" }} />
        <Tooltip {...tooltipStyle} formatter={(v) => gw(v as number)} />
        <Scatter data={points} fill={C.forecast} fillOpacity={0.45} isAnimationActive={false} />
      </ScatterChart>
    </ResponsiveContainer>
  );
}

export function PlanChart({ hours }: { hours: HourPlan[] }) {
  const data = hours.map((h) => ({
    t: ukTime(h.start_time), forecast: h.forecast_mw, planned: h.planned_wind_mw, actual: h.actual_mw,
    short: h.covered ? null : h.actual_mw,
  }));
  return (
    <ResponsiveContainer width="100%" height={320}>
      <ComposedChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 0 }}>
        <CartesianGrid stroke={C.grid} vertical={false} />
        <XAxis dataKey="t" {...axis} interval={2} />
        <YAxis {...axis} tickFormatter={gwTick} width={40} label={{ value: "GW", angle: -90, position: "insideLeft", fill: C.axis }} />
        <Tooltip {...tooltipStyle} formatter={(v, name) => [gw(v as number), name]} />
        <Legend />
        <Area dataKey="planned" name="Wind to plan for" fill={C.band} stroke={C.plan} strokeWidth={2.5} isAnimationActive={false} />
        <Line dataKey="forecast" name="Forecast" stroke={C.forecast} strokeWidth={2} strokeDasharray="5 4" dot={false} isAnimationActive={false} />
        <Line dataKey="actual" name="What actually came" stroke={C.actual} strokeWidth={2} dot={false} isAnimationActive={false} />
        <Scatter dataKey="short" name="Short even with plan" fill={C.bad} isAnimationActive={false} />
      </ComposedChart>
    </ResponsiveContainer>
  );
}
