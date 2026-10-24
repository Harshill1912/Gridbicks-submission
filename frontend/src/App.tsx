import { useEffect, useState } from "react";
import { CutoffSelect, DaySelect, daysBetween } from "./components/Controls";
import { QueryState } from "./components/Card";
import { useHealth } from "./hooks/useApi";
import { AccuracyPage } from "./pages/AccuracyPage";
import { ForecastPage } from "./pages/ForecastPage";
import { PlannerPage } from "./pages/PlannerPage";

const TABS = [
  { id: "forecast", label: "Forecast", blurb: "What you'd have seen when buying" },
  { id: "accuracy", label: "Accuracy", blurb: "How far to trust it" },
  { id: "planner", label: "Planner", blurb: "How much to buy" },
] as const;
type Tab = (typeof TABS)[number]["id"];

export default function App() {
  const health = useHealth();
  const [tab, setTab] = useState<Tab>("forecast");
  const [day, setDay] = useState("");
  const [cutoff, setCutoff] = useState("10:00");

  useEffect(() => {
    if (health.data && !day) setDay(health.data.first_delivery_day);
  }, [health.data, day]);

  return (
    <div className="app">
      <header className="top">
        <div className="brand">
          <span className="logo" aria-hidden>≋</span>
          <div>
            <h1>Wind Forecast Monitor</h1>
            <p className="muted">GB national wind · day-ahead decisions, January 2026 · source: Elexon BMRS</p>
          </div>
        </div>
        <nav className="tabs" role="tablist">
          {TABS.map((t) => (
            <button key={t.id} role="tab" aria-selected={tab === t.id} className={tab === t.id ? "tab active" : "tab"} onClick={() => setTab(t.id)}>
              <span>{t.label}</span>
              <small>{t.blurb}</small>
            </button>
          ))}
        </nav>
      </header>

      <QueryState query={health} height={400}>
        {(h) => (
          <main>
            <div className="controls">
              {tab !== "accuracy" && <DaySelect days={daysBetween(h.first_delivery_day, h.last_delivery_day)} value={day} onChange={setDay} />}
              <CutoffSelect value={cutoff} onChange={setCutoff} />
            </div>
            {day && tab === "forecast" && <ForecastPage day={day} cutoff={cutoff} />}
            {tab === "accuracy" && <AccuracyPage cutoff={cutoff} />}
            {day && tab === "planner" && <PlannerPage day={day} cutoff={cutoff} />}
          </main>
        )}
      </QueryState>

      <footer className="muted small">Actuals: FUELHH (fuelType WIND). Forecasts: WINDFOR. Times in UK local time.</footer>
    </div>
  );
}
