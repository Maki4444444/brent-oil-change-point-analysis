import { useEffect, useMemo, useState, useCallback } from "react";
import Header from "./components/Header";
import FilterPanel from "./components/FilterPanel";
import PriceChart from "./components/PriceChart";
import StatsCards from "./components/StatsCards";
import ChangePointCards from "./components/ChangePointCards";
import EventTable from "./components/EventTable";
import { fetchPrices, fetchChangePoints, fetchEvents, fetchStats } from "./api";
import "./dashboard.css";

const DEFAULT_START = "1987-05-20";
const DEFAULT_END = "2022-11-14";

export default function App() {
  const [range, setRange] = useState({ start: DEFAULT_START, end: DEFAULT_END });
  const [prices, setPrices] = useState([]);
  const [changePointData, setChangePointData] = useState(null);
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState(null);
  const [activeCategories, setActiveCategories] = useState(new Set());
  const [selectedModelId, setSelectedModelId] = useState(null);
  const [highlightedEventDate, setHighlightedEventDate] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Change point results are static for the whole dataset; fetch once.
  useEffect(() => {
    fetchChangePoints()
      .then(setChangePointData)
      .catch((e) => setError(e.message));
  }, []);

  // Prices, events, and stats re-fetch whenever the date range changes.
  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);

    Promise.all([
      fetchPrices(range.start, range.end),
      fetchEvents(range.start, range.end),
      fetchStats(range.start, range.end),
    ])
      .then(([priceRes, eventRes, statsRes]) => {
        if (cancelled) return;
        setPrices(priceRes.data);
        setEvents(eventRes.data);
        setStats(statsRes);
      })
      .catch((e) => {
        if (!cancelled) setError(e.response?.data?.error || e.message);
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [range.start, range.end]);

  const handleRangeChange = useCallback((start, end) => {
    setRange({ start, end });
    setHighlightedEventDate(null);
    setSelectedModelId(null);
  }, []);

  const handleToggleCategory = useCallback((cat) => {
    setActiveCategories((prev) => {
      const next = new Set(prev);
      if (next.has(cat)) next.delete(cat);
      else next.add(cat);
      return next;
    });
  }, []);

  const filteredEvents = useMemo(() => {
    if (activeCategories.size === 0) return events;
    return events.filter((ev) => activeCategories.has(ev.category));
  }, [events, activeCategories]);

  const visibleChangePoints = useMemo(() => {
    if (!changePointData) return [];
    return changePointData.models.filter(
      (m) => m.change_point_date >= range.start && m.change_point_date <= range.end
    );
  }, [changePointData, range]);

  const handleSelectModel = useCallback((model) => {
    setSelectedModelId(model.id);
    setRange({ start: model.window_start, end: model.window_end });
    setHighlightedEventDate(null);
  }, []);

  const handleSelectEvent = useCallback((event) => {
    setHighlightedEventDate(event.date);
  }, []);

  const handleBrushChange = useCallback(
    (brushRange) => {
      if (!brushRange || brushRange.startIndex == null || !prices.length) return;
      const startDate = prices[brushRange.startIndex]?.date;
      const endDate = prices[brushRange.endIndex]?.date;
      // Brush drag is a visual zoom only; it does not refetch, so we don't
      // call handleRangeChange here to avoid feedback loops with the
      // filter panel's own inputs.
      void startDate;
      void endDate;
    },
    [prices]
  );

  return (
    <div className="app-shell">
      <Header datasetRange={changePointData?.dataset_range} />

      <main className="main-grid">
        <FilterPanel
          start={range.start}
          end={range.end}
          onRangeChange={handleRangeChange}
          activeCategories={activeCategories}
          onToggleCategory={handleToggleCategory}
        />

        <section className="content-col">
          {error && <div className="error-banner">{error}</div>}

          <StatsCards stats={stats} loading={loading} />

          <div className="panel">
            <h2 className="panel-heading">Price history with detected change points</h2>
            <PriceChart
              data={prices}
              changePoints={visibleChangePoints}
              events={filteredEvents}
              highlightedEventDate={highlightedEventDate}
              onBrushChange={handleBrushChange}
            />
          </div>

          <div className="panel">
            <h2 className="panel-heading">Change point models</h2>
            <p className="panel-subheading">
              Select a model to jump the chart to its analysis window and see the quantified
              impact.
            </p>
            <ChangePointCards
              models={changePointData?.models || []}
              onSelect={handleSelectModel}
              selectedId={selectedModelId}
            />
          </div>

          <div className="panel">
            <h2 className="panel-heading">
              Catalogued events{" "}
              <span className="panel-heading-count">({filteredEvents.length})</span>
            </h2>
            <p className="panel-subheading">
              Click a row to highlight it on the chart above.
            </p>
            <EventTable
              events={filteredEvents}
              onSelectEvent={handleSelectEvent}
              highlightedEventDate={highlightedEventDate}
            />
          </div>
        </section>
      </main>

      <footer className="app-footer">
        Change Point Analysis and Statistical Modeling of Brent Oil Prices &middot; Birhan
        Energies &middot; 10 Academy KAIM
      </footer>
    </div>
  );
}
