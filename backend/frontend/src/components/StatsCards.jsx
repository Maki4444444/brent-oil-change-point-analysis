function Card({ label, value, sub, tone }) {
  return (
    <div className="stat-card">
      <p className="stat-label">{label}</p>
      <p className={"stat-value mono" + (tone ? ` tone-${tone}` : "")}>{value}</p>
      {sub && <p className="stat-sub">{sub}</p>}
    </div>
  );
}

export default function StatsCards({ stats, loading }) {
  if (loading || !stats) {
    return (
      <div className="stats-grid">
        {Array.from({ length: 4 }).map((_, i) => (
          <div className="stat-card stat-card-loading" key={i} />
        ))}
      </div>
    );
  }

  const pct = stats.pct_change_over_window;
  const tone = pct == null ? undefined : pct >= 0 ? "positive" : "negative";

  return (
    <div className="stats-grid">
      <Card
        label="Average price"
        value={`$${stats.avg_price.toFixed(2)}`}
        sub={`${stats.n_observations.toLocaleString()} trading days`}
      />
      <Card
        label="Change over window"
        value={pct == null ? "—" : `${pct >= 0 ? "+" : ""}${pct.toFixed(1)}%`}
        sub={`$${stats.start_price.toFixed(2)} → $${stats.end_price.toFixed(2)}`}
        tone={tone}
      />
      <Card
        label="Volatility"
        value={
          stats.volatility_daily_log_return_std == null
            ? "—"
            : stats.volatility_daily_log_return_std.toFixed(4)
        }
        sub="std. dev. of daily log returns"
      />
      <Card
        label="Range"
        value={`$${stats.min_price.toFixed(2)} – $${stats.max_price.toFixed(2)}`}
        sub="min / max in window"
      />
    </div>
  );
}
