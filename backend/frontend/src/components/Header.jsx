export default function Header({ datasetRange }) {
  return (
    <header className="header">
      <div className="header-inner">
        <div>
          <p className="eyebrow">BIRHAN ENERGIES</p>
          <h1 className="title">Brent Crude Intelligence</h1>
          <p className="subtitle">
            Structural break detection and event correlation for Brent crude oil,{" "}
            {datasetRange ? (
              <span className="mono subtitle-range">
                {datasetRange.start} &ndash; {datasetRange.end}
              </span>
            ) : (
              "loading range…"
            )}
          </p>
        </div>
        <div className="header-badge">
          <span className="header-badge-dot" aria-hidden="true" />
          Bayesian change point model &middot; PyMC
        </div>
      </div>
    </header>
  );
}
