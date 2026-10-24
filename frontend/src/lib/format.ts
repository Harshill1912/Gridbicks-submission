// Display helpers. All times are shown in UK local time, which is what traders work in.
const UK = "Europe/London";

export const gw = (mw: number | null | undefined, digits = 1) =>
  mw == null ? "–" : `${(mw / 1000).toFixed(digits)} GW`;

export const signedGw = (mw: number | null | undefined, digits = 1) =>
  mw == null ? "–" : `${mw > 0 ? "+" : mw < 0 ? "−" : ""}${Math.abs(mw / 1000).toFixed(digits)} GW`;

export const pct = (x: number | null | undefined, digits = 0) => (x == null ? "–" : `${(x * 100).toFixed(digits)}%`);

export const ukTime = (iso: string) =>
  new Date(iso).toLocaleTimeString("en-GB", { timeZone: UK, hour: "2-digit", minute: "2-digit" });

export const ukDateTime = (iso: string) =>
  new Date(iso).toLocaleString("en-GB", {
    timeZone: UK, weekday: "short", day: "numeric", month: "short", hour: "2-digit", minute: "2-digit",
  });

export const longDate = (day: string) =>
  new Date(`${day}T12:00:00Z`).toLocaleDateString("en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" });

/** "10:00" from a backend "10:00:00". */
export const hhmm = (t: string) => t.slice(0, 5);
