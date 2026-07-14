"""
Tests for the dashboard Flask backend (backend/app.py).
"""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import app as app_module  # noqa: E402


@pytest.fixture
def client():
    app_module.app.config["TESTING"] = True
    with app_module.app.test_client() as c:
        yield c


def test_health_ok(client):
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "ok"
    assert data["n_price_rows"] > 0
    assert data["n_events"] > 0


def test_prices_returns_data(client):
    res = client.get("/api/prices")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] > 0
    assert "date" in data["data"][0]
    assert "price" in data["data"][0]


def test_prices_date_range_filters(client):
    res = client.get("/api/prices?start=2022-01-01&end=2022-01-10")
    assert res.status_code == 200
    data = res.get_json()
    assert all("2022-01-01" <= r["date"] <= "2022-01-10" for r in data["data"])


def test_prices_invalid_date_returns_400(client):
    res = client.get("/api/prices?start=not-a-date")
    assert res.status_code == 400
    assert "error" in res.get_json()


def test_change_points_returns_models(client):
    res = client.get("/api/change-points")
    assert res.status_code == 200
    data = res.get_json()
    assert "models" in data
    assert len(data["models"]) == 4
    ids = {m["id"] for m in data["models"]}
    assert "baseline" in ids


def test_events_returns_data(client):
    res = client.get("/api/events")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] >= 10


def test_events_category_filter(client):
    res = client.get("/api/events?category=OPEC Policy")
    assert res.status_code == 200
    data = res.get_json()
    assert data["count"] > 0
    assert all(r["category"] == "OPEC Policy" for r in data["data"])


def test_stats_returns_summary(client):
    res = client.get("/api/stats?start=2020-01-01&end=2020-06-30")
    assert res.status_code == 200
    data = res.get_json()
    assert "avg_price" in data
    assert "volatility_daily_log_return_std" in data
    assert data["n_observations"] > 0


def test_stats_invalid_date_returns_400(client):
    res = client.get("/api/stats?start=nope")
    assert res.status_code == 400
