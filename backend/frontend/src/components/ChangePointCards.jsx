export default function ChangePointCards({ models, onSelect, selectedId }) {
  return (
    <div className="cp-grid">
      {models.map((m) => {
        const isPositive = m.pct_change >= 0;
        return (
          <button
            key={m.id}
            type="button"
            className={"cp-card" + (selectedId === m.id ? " active" : "")}
            onClick={() => onSelect(m)}
          >
            <p className="cp-card-label">{m.label}</p>
            <p className="cp-card-date mono">{m.change_point_date}</p>
            <p className={"cp-card-pct mono " + (isPositive ? "tone-positive" : "tone-negative")}>
              {isPositive ? "+" : ""}
              {m.pct_change.toFixed(1)}%
            </p>
            <p className="cp-card-shift mono">
              ${m.mean_before.toFixed(2)} &rarr; ${m.mean_after.toFixed(2)}
            </p>
            {m.associated_event_name && (
              <p className="cp-card-event">
                {m.associated_event_name}
                <span className="cp-card-offset">
                  {" "}
                  ({m.days_from_event === 0
                    ? "same day"
                    : `${Math.abs(m.days_from_event)}d ${m.days_from_event > 0 ? "after" : "before"}`}
                  )
                </span>
              </p>
            )}
          </button>
        );
      })}
    </div>
  );
}
