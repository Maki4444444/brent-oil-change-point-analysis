# Brent Oil Dashboard (Task 3)

Interactive Flask + React dashboard for exploring the Brent oil change point
analysis: historical prices, detected Bayesian change points, and the
researched events dataset, all in one filterable view.

## Screenshots

| Desktop | Filtered (event category) |
|---|---|
| ![Desktop dashboard](screenshots/dashboard_desktop.png) | ![Filtered dashboard](screenshots/dashboard_filtered.png) |

| Tablet | Mobile |
|---|---|
| ![Tablet dashboard](screenshots/dashboard_tablet.png) | ![Mobile dashboard](screenshots/dashboard_mobile.png) |

## Architecture

```
backend/
├── app.py                      # Flask app: API + serves the built frontend
├── requirements.txt
├── data/
│   ├── BrentOilPrices.csv
│   ├── key_events_verified.csv
│   └── change_point_results.json   # static export of Task 2 model results
├── screenshots/
└── frontend/                   # React app (Vite)
    ├── src/
    │   ├── App.jsx
    │   ├── api.js               # API client
    │   ├── dashboard.css
    │   └── components/
    │       ├── Header.jsx
    │       ├── FilterPanel.jsx
    │       ├── PriceChart.jsx
    │       ├── StatsCards.jsx
    │       ├── ChangePointCards.jsx
    │       └── EventTable.jsx
    └── vite.config.js           # dev-mode proxy: /api -> localhost:5000
```

`change_point_results.json` is a static export of the Task 2 notebook's
results (change point dates, before/after means, r_hat convergence
diagnostics, associated events). The Flask backend serves this file
directly, so it does **not** need PyMC installed at runtime — only
`flask`, `flask-cors`, `pandas`, and `numpy`.

## API Endpoints

| Endpoint | Description |
|---|---|
| `GET /api/health` | Backend + data-load status check |
| `GET /api/prices?start=&end=` | Historical daily prices (optionally date-filtered) |
| `GET /api/change-points` | Bayesian change point model results (Task 2) |
| `GET /api/events?start=&end=&category=` | Researched events (optionally filtered) |
| `GET /api/stats?start=&end=` | Summary stats for a window: avg price, volatility, min/max, % change |

All date-range endpoints return `400` with a clear error message on an
unparseable date, and `404` on an empty result where applicable.

## Setup

### 1. Backend (Flask)

```bash
cd backend
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

The API is now running at `http://localhost:5000`. Check it with:

```bash
curl http://localhost:5000/api/health
```

### 2. Frontend (React) development mode

In a **second terminal**, with the Flask backend still running:

```bash
cd backend/frontend
npm install
npm run dev
```

Open the URL Vite prints (typically `http://localhost:5173`). The dev
server proxies `/api/*` requests to the Flask backend on port 5000 (see
`vite.config.js`), so both must be running simultaneously in dev mode.

### 3. Production mode (single server)

To serve everything from Flask alone (no separate frontend dev server):

```bash
cd backend/frontend
npm install
npm run build
cd ..
python app.py
```

Now visit `http://localhost:5000` — Flask serves the built React app
directly alongside the API.

## Dashboard Features

- **Price chart** full history or any custom/preset date range, with
  dashed reference lines marking detected change points and dots marking
  catalogued events. Includes a brush control at the bottom for
  click-and-drag zooming.
- **Date range filtering** manual start/end date pickers, plus one-click
  presets for each major event window (2008 crisis, 2014 OPEC crash, 2020
  COVID/price war, 2022 Russia-Ukraine).
- **Event category filters** toggle Geopolitical / OPEC Policy / Economic
  / Market Shock events on or off.
- **Change point drill-down** click any of the four model cards (baseline
  + 3 event case studies) to jump the chart straight to that model's
  analysis window and see its quantified impact ($ before/after, % change,
  associated event).
- **Event highlight** click any row in the events table to highlight that
  event's marker on the chart.
- **Key indicators** average price, % change over the current window,
  volatility (std. dev. of daily log returns), and price range, all
  recalculated live as the date range changes.
- **Responsive layout** filter panel collapses above the content on
  tablet/mobile; stat cards and change point cards reflow to fewer columns
  on narrow screens.

## Notes

- Chart rendering downsamples very long ranges (>1,500 points) for
  performance; this only affects what's drawn, not the underlying
  computed statistics, which are always calculated server-side on the
  full-resolution data.
- `change_point_results.json` is a static snapshot. If you re-run
  `notebooks/02_change_point_model.ipynb` with different data or settings,
  regenerate this file to keep the dashboard in sync (see the export cell
  at the end of that notebook, or `scripts/export_change_points.py`).
