// Mirrors backend/app/api/schemas.py

export interface Health {
  status: string;
  first_delivery_day: string;
  last_delivery_day: string;
  actual_rows: number;
  forecast_rows: number;
}

export interface SeriesPoint {
  start_time: string;
  actual_mw: number | null;
  forecast_mw: number | null;
  publish_time: string | null;
  band_low_mw: number | null;
  band_high_mw: number | null;
}

export interface DaySeries {
  day: string;
  cutoff: string;
  deadline: string;
  points: SeriesPoint[];
}

export interface Metrics {
  bias_mw: number | null;
  mae_mw: number | null;
  rmse_mw: number | null;
  mape_pct: number | null;
  p10_error_mw: number | null;
  p90_error_mw: number | null;
}

export interface Summary {
  cutoff: string;
  count: number;
  missing_forecast: number;
  metrics: Metrics;
}

export interface HorizonRow extends Metrics { horizon_h: number; count: number }
export interface HourRow extends Metrics { hour: number; count: number }
export interface WindLevelRow extends Metrics { forecast_from_mw: number; count: number }

export interface ScatterPoint {
  start_time: string;
  forecast_mw: number;
  actual_mw: number;
  error_mw: number;
}

export interface HourPlan {
  start_time: string;
  forecast_mw: number;
  planned_wind_mw: number;
  buffer_mw: number;
  actual_mw: number;
  covered: boolean;
}

export interface DayPlan {
  day: string;
  confidence: number;
  hours: HourPlan[];
  total_buffer_mwh: number;
  shortfalls_naive: number;
  shortfalls_planned: number;
}

export interface Backtest {
  confidence: number;
  hours: number;
  shortfall_rate_naive: number;
  shortfall_rate_planned: number;
  avg_buffer_mw: number;
}
