"""
app.py

Flask backend for the Brent Oil Change Point Analysis dashboard (Task 3).

Serves three categories of data to the React frontend:
  - Historical price data      (/api/prices)
  - Change point model results (/api/change-points)
  - Event / correlation data   (/api/events, /api/stats)

In production, this app also serves the built React frontend as static
files from frontend/dist (see the catch-all route at the bottom).

Run (development):
    python app.py
    # API available at http://localhost:5000/api/...
    # (run the React dev server separately for hot-reload frontend work)

Run (production-style, serving the built frontend):
    cd frontend && npm run build && cd ..
    python app.py
    # Full app available at http://localhost:5000
"""

from pathlib import Path

import numpy as np
import pandas as pd
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"

PRICES_PATH = DATA_DIR / "BrentOilPrices.csv"
EVENTS_PATH = DATA_DIR / "key_events_verified.csv"
CHANGE_POINTS_PATH = DATA_DIR / "change_point_results.json"

app = Flask(__name__, static_folder=None)
CORS(app)  # allows the React dev server (different port) to call this API


# ---------------------------------------------------------------------------
# Data loading (cached in memory at startup; this dataset is small enough
# that re-reading from disk on every request is unnecessary).
# ---------------------------------------------------------------------------

def _load_prices() -> pd.DataFrame:
    """Load and clean the Brent price CSV, tolerating the two date formats
    present in the raw file, and raising a clear error if the file is
    missing or malformed."""
    if not PRICES_PATH.exists():
        raise FileNotFoundError(f"Price data not found at {PRICES_PATH}")

    df = pd.read_csv(PRICES_PATH)
    if not {"Date", "Price"}.issubset(df.columns):
        raise ValueError("BrentOilPrices.csv must contain 'Date' and 'Price' columns")

    parsed = pd.to_datetime(df["Date"], format="%d-%b-%y", errors="coerce")
    remaining = parsed.isna()
    if remaining.any():
        parsed.loc[remaining] = pd.to_datetime(
            df.loc[remaining, "Date"], format="%b %d, %Y", errors="coerce"
        )
    df["Date"] = parsed
    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    df = df.dropna(subset=["Date", "Price"]).sort_values("Date")
    df["LogReturn"] = np.log(df["Price"]).diff()
    return df.reset_index(drop=True)


def _load_events() -> pd.DataFrame:
    if not EVENTS_PATH.exists():
        raise FileNotFoundError(f"Events data not found at {EVENTS_PATH}")
    df = pd.read_csv(EVENTS_PATH)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df.dropna(subset=["date"]).sort_values("date").reset_index(drop=True)


try:
    PRICES_DF = _load_prices()
    EVENTS_DF = _load_events()
    DATA_LOAD_ERROR = None
except (FileNotFoundError, ValueError) as exc:
    PRICES_DF = pd.DataFrame(columns=["Date", "Price", "LogReturn"])
    EVENTS_DF = pd.DataFrame(columns=["date"])
    DATA_LOAD_ERROR = str(exc)


def _parse_date_arg(name: str):
    """Parse an optional ?start=/?end= query arg into a Timestamp, or None.
    Raises ValueError (caught by the route) on an unparseable value."""
    raw = request.args.get(name)
    if not raw:
        return None
    parsed = pd.to_datetime(raw, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"Could not parse '{name}' query parameter: {raw!r}")
    return parsed


def _filter_by_date(df: pd.DataFrame, date_col: str, start, end) -> pd.DataFrame:
    out = df
    if start is not None:
        out = out[out[date_col] >= start]
    if end is not None:
        out = out[out[date_col] <= end]
    return out


# ---------------------------------------------------------------------------
# API routes
# ---------------------------------------------------------------------------

@app.route("/api/health")
def health():
    """Simple health/status check, also surfaces a data-loading error if
    the CSVs were missing/malformed at startup rather than failing every
    subsequent request opaquely."""
    return jsonify({
        "status": "ok" if DATA_LOAD_ERROR is None else "data_error",
        "error": DATA_LOAD_ERROR,
        "n_price_rows": len(PRICES_DF),
        "n_events": len(EVENTS_DF),
    })


@app.route("/api/prices")
def get_prices():
    """
    Historical Brent oil price data.

    Query params:
      start (YYYY-MM-DD, optional) - inclusive lower bound
      end   (YYYY-MM-DD, optional) - inclusive upper bound

    Returns: { data: [ {date, price, log_return}, ... ], count: int }
    """
    try:
        start = _parse_date_arg("start")
        end = _parse_date_arg("end")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    df = _filter_by_date(PRICES_DF, "Date", start, end)
    records = [
        {
            "date": row.Date.strftime("%Y-%m-%d"),
            "price": round(float(row.Price), 2),
            "log_return": None if pd.isna(row.LogReturn) else round(float(row.LogReturn), 6),
        }
        for row in df.itertuples()
    ]
    return jsonify({"data": records, "count": len(records)})


@app.route("/api/change-points")
def get_change_points():
    """
    Bayesian change point model results (Task 2), served from a static
    JSON export rather than re-running PyMC at request time.

    Returns the full contents of data/change_point_results.json.
    """
    if not CHANGE_POINTS_PATH.exists():
        return jsonify({"error": "change_point_results.json not found"}), 404
    import json
    with open(CHANGE_POINTS_PATH) as f:
        return jsonify(json.load(f))


@app.route("/api/events")
def get_events():
    """
    Researched key events dataset, optionally filtered.

    Query params:
      start    (YYYY-MM-DD, optional)
      end      (YYYY-MM-DD, optional)
      category (optional, exact match, e.g. "OPEC Policy")

    Returns: { data: [ {event_id, date, event_name, category, ...}, ... ], count: int }
    """
    try:
        start = _parse_date_arg("start")
        end = _parse_date_arg("end")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    df = _filter_by_date(EVENTS_DF, "date", start, end)

    category = request.args.get("category")
    if category:
        df = df[df["category"].str.lower() == category.lower()]

    records = []
    for row in df.itertuples():
        records.append({
            "event_id": int(row.event_id),
            "date": row.date.strftime("%Y-%m-%d"),
            "event_name": row.event_name,
            "category": row.category,
            "description": row.description,
            "price_impact": row.price_impact,
            "source_url": row.source_url,
        })
    return jsonify({"data": records, "count": len(records)})


@app.route("/api/stats")
def get_stats():
    """
    Summary indicators for a given date window: average price, price
    volatility (std. dev. of daily log returns), and the min/max price
    seen in the window. Used by the dashboard's key-indicator cards.

    Query params:
      start (YYYY-MM-DD, optional)
      end   (YYYY-MM-DD, optional)
    """
    try:
        start = _parse_date_arg("start")
        end = _parse_date_arg("end")
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    df = _filter_by_date(PRICES_DF, "Date", start, end)
    if df.empty:
        return jsonify({"error": "No data in the requested date range"}), 404

    log_returns = df["LogReturn"].dropna()
    stats = {
        "start": df["Date"].min().strftime("%Y-%m-%d"),
        "end": df["Date"].max().strftime("%Y-%m-%d"),
        "n_observations": int(len(df)),
        "avg_price": round(float(df["Price"].mean()), 2),
        "min_price": round(float(df["Price"].min()), 2),
        "max_price": round(float(df["Price"].max()), 2),
        "volatility_daily_log_return_std": round(float(log_returns.std()), 5) if len(log_returns) else None,
        "start_price": round(float(df["Price"].iloc[0]), 2),
        "end_price": round(float(df["Price"].iloc[-1]), 2),
        "pct_change_over_window": round(
            float((df["Price"].iloc[-1] - df["Price"].iloc[0]) / df["Price"].iloc[0] * 100), 2
        ) if df["Price"].iloc[0] != 0 else None,
    }
    return jsonify(stats)


# ---------------------------------------------------------------------------
# Serve the built React frontend (production mode).
# In development, run `npm run dev` inside frontend/ separately instead and
# ignore these routes (Vite's dev server serves the UI on its own port).
# ---------------------------------------------------------------------------

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def serve_frontend(path):
    if not FRONTEND_DIST.exists():
        return jsonify({
            "message": "React build not found. Run 'npm run build' inside frontend/, "
                       "or use 'npm run dev' for local development on its own port.",
        }), 200

    target = FRONTEND_DIST / path
    if path and target.exists():
        return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, "index.html")


if __name__ == "__main__":
    app.run(debug=True, port=5000)
