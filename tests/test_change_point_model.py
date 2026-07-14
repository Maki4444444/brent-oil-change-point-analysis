"""
Unit tests for src.change_point_model.

Uses a small synthetic series with a known, obvious mean shift so the
model should reliably recover the true change point without needing
expensive full-scale MCMC settings.
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from change_point_model import fit_change_point_model, nearest_events  # noqa: E402


@pytest.fixture
def synthetic_series():
    """A series with an obvious mean shift at index 50 (of 100)."""
    rng = np.random.default_rng(0)
    dates = pd.date_range("2020-01-01", periods=100, freq="D")
    before = rng.normal(loc=10, scale=0.5, size=50)
    after = rng.normal(loc=25, scale=0.5, size=50)
    values = np.concatenate([before, after])
    return pd.Series(values, index=dates)


def test_fit_change_point_model_recovers_known_shift(synthetic_series):
    result = fit_change_point_model(
        synthetic_series, draws=300, tune=300, chains=2, random_seed=0
    )
    # True change point is at index 49/50; allow a small tolerance window
    assert abs(result.tau_mode_idx - 49) <= 3
    assert result.mu1_mean < 15  # should be near the "before" mean (~10)
    assert result.mu2_mean > 20  # should be near the "after" mean (~25)
    assert result.pct_change > 0  # increase


def test_fit_change_point_model_rejects_nan():
    dates = pd.date_range("2020-01-01", periods=5, freq="D")
    series = pd.Series([1.0, 2.0, np.nan, 4.0, 5.0], index=dates)
    with pytest.raises(ValueError):
        fit_change_point_model(series)


def test_fit_change_point_model_rejects_too_short():
    dates = pd.date_range("2020-01-01", periods=1, freq="D")
    series = pd.Series([1.0], index=dates)
    with pytest.raises(ValueError):
        fit_change_point_model(series)


def test_nearest_events_returns_closest_and_signed_offset():
    events = pd.DataFrame(
        {
            "date": pd.to_datetime(["2020-01-01", "2020-02-01", "2020-06-01"]),
            "event_name": ["A", "B", "C"],
        }
    )
    target = pd.Timestamp("2020-01-28")
    result = nearest_events(events, target, n=2)
    assert list(result["event_name"]) == ["B", "A"]
    # B is 4 days after target -> positive offset
    assert result.loc[result["event_name"] == "B", "days_from_change_point"].iloc[0] == 4
