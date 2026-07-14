export default function EventTable({ events, onSelectEvent, highlightedEventDate }) {
  if (!events.length) {
    return <p className="empty-note">No events in the selected range/category.</p>;
  }

  return (
    <div className="event-table-wrap">
      <table className="event-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Event</th>
            <th>Category</th>
            <th>Impact</th>
          </tr>
        </thead>
        <tbody>
          {events.map((ev) => (
            <tr
              key={ev.event_id}
              className={highlightedEventDate === ev.date ? "row-active" : ""}
              onClick={() => onSelectEvent(ev)}
              tabIndex={0}
              onKeyDown={(e) => {
                if (e.key === "Enter" || e.key === " ") onSelectEvent(ev);
              }}
            >
              <td className="mono">{ev.date}</td>
              <td>
                {ev.event_name}
                <a
                  href={ev.source_url}
                  target="_blank"
                  rel="noreferrer"
                  onClick={(e) => e.stopPropagation()}
                  className="source-link"
                >
                  source
                </a>
              </td>
              <td>
                <span className="category-pill">{ev.category}</span>
              </td>
              <td>
                <span
                  className={
                    "impact-pill " +
                    (ev.price_impact === "Increase" ? "tone-positive" : "tone-negative")
                  }
                >
                  {ev.price_impact}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
