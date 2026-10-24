import type { ReactNode } from "react";

export function Card({ title, subtitle, children, actions }: {
  title?: string; subtitle?: ReactNode; children: ReactNode; actions?: ReactNode;
}) {
  return (
    <section className="card">
      {(title || actions) && (
        <header className="card-head">
          <div>
            {title && <h2>{title}</h2>}
            {subtitle && <p className="muted">{subtitle}</p>}
          </div>
          {actions}
        </header>
      )}
      {children}
    </section>
  );
}

export function MetricCard({ label, value, hint, tone = "neutral" }: {
  label: string; value: string; hint: string; tone?: "neutral" | "warn" | "good";
}) {
  return (
    <div className={`metric metric-${tone}`}>
      <span className="metric-label">{label}</span>
      <span className="metric-value">{value}</span>
      <span className="metric-hint">{hint}</span>
    </div>
  );
}

/** Wraps any query result: spinner while loading, message on error, children when ready. */
export function QueryState<T>({ query, children, height = 320 }: {
  query: { data: T | undefined; isLoading: boolean; error: Error | null };
  children: (data: T) => ReactNode;
  height?: number;
}) {
  if (query.error) return <div className="state state-error" style={{ minHeight: height }}>Couldn't load data: {query.error.message}</div>;
  if (query.isLoading || query.data === undefined) return <div className="state" style={{ minHeight: height }}><span className="spinner" /></div>;
  return <>{children(query.data)}</>;
}
