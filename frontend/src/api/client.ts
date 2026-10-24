import type {
  Backtest, DayPlan, DaySeries, Health, HorizonRow, HourRow, ScatterPoint, Summary, WindLevelRow,
} from "./types";

// Empty in dev and in docker-compose (same origin via proxy); the API's URL on Vercel.
const BASE = (import.meta.env.VITE_API_URL ?? "").replace(/\/$/, "");

export class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
  }
}

async function get<T>(path: string, params: Record<string, string | number> = {}): Promise<T> {
  const qs = new URLSearchParams(Object.entries(params).map(([k, v]) => [k, String(v)]));
  const res = await fetch(`${BASE}/api${path}${qs.size ? `?${qs}` : ""}`);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new ApiError(res.status, body.detail ?? `Request failed (${res.status})`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => get<Health>("/health"),
  series: (day: string, cutoff: string) => get<DaySeries>("/series", { day, cutoff }),
  summary: (cutoff: string) => get<Summary>("/metrics", { cutoff }),
  byHorizon: () => get<HorizonRow[]>("/metrics/by-horizon"),
  byHour: (cutoff: string) => get<HourRow[]>("/metrics/by-hour", { cutoff }),
  byWindLevel: (cutoff: string) => get<WindLevelRow[]>("/metrics/by-wind-level", { cutoff }),
  scatter: (cutoff: string) => get<ScatterPoint[]>("/metrics/scatter", { cutoff }),
  plan: (day: string, confidence: number, cutoff: string) => get<DayPlan>("/plan", { day, confidence, cutoff }),
  backtest: (confidence: number, cutoff: string) => get<Backtest>("/plan/backtest", { confidence, cutoff }),
};
