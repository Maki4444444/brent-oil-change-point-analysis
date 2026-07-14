const PRESETS = [
  { label: "Full History", start: "1987-05-20", end: "2022-11-14" },
  { label: "2008 Financial Crisis", start: "2008-01-01", end: "2009-06-30" },
  { label: "2014 OPEC Crash", start: "2014-06-01", end: "2015-03-01" },
  { label: "2020 COVID / Price War", start: "2020-01-01", end: "2020-06-30" },
  { label: "2022 Russia-Ukraine", start: "2021-11-01", end: "2022-06-01" },
];

const CATEGORIES = [
  "Geopolitical",
  "OPEC Policy",
  "Economic",
  "Market Shock",
];

export default function FilterPanel({
  start,
  end,
  onRangeChange,
  activeCategories,
  onToggleCategory,
}) {
  return (
    <aside className="filter-panel" aria-label="Filters">
      <div className="filter-block">
        <h2 className="filter-heading">Date range</h2>
        <div className="date-inputs">
          <label className="date-field">
            <span>Start</span>
            <input
              type="date"
              value={start}
              min="1987-05-20"
              max="2022-11-14"
              onChange={(e) => onRangeChange(e.target.value, end)}
            />
          </label>
          <label className="date-field">
            <span>End</span>
            <input
              type="date"
              value={end}
              min="1987-05-20"
              max="2022-11-14"
              onChange={(e) => onRangeChange(start, e.target.value)}
            />
          </label>
        </div>

        <div className="preset-list">
          {PRESETS.map((p) => (
            <button
              key={p.label}
              type="button"
              className={
                "preset-btn" + (start === p.start && end === p.end ? " active" : "")
              }
              onClick={() => onRangeChange(p.start, p.end)}
            >
              {p.label}
            </button>
          ))}
        </div>
      </div>

      <div className="filter-block">
        <h2 className="filter-heading">Event category</h2>
        <div className="category-list">
          {CATEGORIES.map((cat) => (
            <label key={cat} className="category-item">
              <input
                type="checkbox"
                checked={activeCategories.has(cat)}
                onChange={() => onToggleCategory(cat)}
              />
              <span>{cat}</span>
            </label>
          ))}
        </div>
      </div>
    </aside>
  );
}
