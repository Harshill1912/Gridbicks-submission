import { longDate } from "../lib/format";

export const CUTOFFS = ["06:00", "08:00", "09:00", "10:00", "11:00", "12:00", "14:00", "16:00"];

/** Every day from first to last inclusive, as YYYY-MM-DD. */
export function daysBetween(first: string, last: string): string[] {
  const out: string[] = [];
  for (let d = new Date(`${first}T00:00:00Z`); d <= new Date(`${last}T00:00:00Z`); d.setUTCDate(d.getUTCDate() + 1)) {
    out.push(d.toISOString().slice(0, 10));
  }
  return out;
}

export function DaySelect({ days, value, onChange }: { days: string[]; value: string; onChange: (d: string) => void }) {
  const i = days.indexOf(value);
  return (
    <div className="control">
      <label htmlFor="day">Delivery day</label>
      <div className="stepper">
        <button aria-label="Previous day" disabled={i <= 0} onClick={() => onChange(days[i - 1])}>‹</button>
        <select id="day" value={value} onChange={(e) => onChange(e.target.value)}>
          {days.map((d) => <option key={d} value={d}>{longDate(d)}</option>)}
        </select>
        <button aria-label="Next day" disabled={i >= days.length - 1} onClick={() => onChange(days[i + 1])}>›</button>
      </div>
    </div>
  );
}

export function CutoffSelect({ value, onChange }: { value: string; onChange: (c: string) => void }) {
  return (
    <div className="control">
      <label htmlFor="cutoff">Decision cut-off (day before, UK time)</label>
      <select id="cutoff" value={value} onChange={(e) => onChange(e.target.value)}>
        {CUTOFFS.map((c) => <option key={c} value={c}>{c}{c === "10:00" ? " · auction gate" : ""}</option>)}
      </select>
    </div>
  );
}

export function ConfidenceSlider({ value, onChange }: { value: number; onChange: (c: number) => void }) {
  return (
    <div className="control control-wide">
      <label htmlFor="confidence">
        Confidence: <strong>{Math.round(value * 100)}%</strong>
        <span className="muted"> — wind should hold at the planned level this often</span>
      </label>
      <input id="confidence" type="range" min={0.5} max={0.95} step={0.05} value={value}
        onChange={(e) => onChange(Number(e.target.value))} />
      <div className="range-ticks"><span>50% · cheaper</span><span>95% · safer</span></div>
    </div>
  );
}
