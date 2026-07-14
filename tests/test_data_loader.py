"""
Unit tests for src.data_loader.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from data_loader import load_brent_prices, load_events  # noqa: E402


@pytest.fixture
def mixed_format_csv(tmp_path):
    """A tiny CSV mimicking the real dataset's two date formats."""
    content = (
        "Date,Price\n"
        "20-May-87,18.63\n"
        "21-May-87,18.45\n"
        '"Nov 08, 2022",96.85\n'
        '"Nov 09, 2022",93.05\n'
    )
    path = tmp_path / "brent_sample.csv"
    path.write_text(content)
    return path


@pytest.fixture
def events_csv(tmp_path):
    content = (
        "event_id,date,event_name,category,description,price_impact,source_url\n"
        "1,1990-08-02,Iraqi Invasion of Kuwait,Geopolitical,desc,Increase,http://example.com\n"
    )
    path = tmp_path / "events_sample.csv"
    path.write_text(content)
    return path


def test_load_brent_prices_parses_mixed_date_formats(mixed_format_csv):
    df = load_brent_prices(mixed_format_csv)
    assert len(df) == 4
    assert isinstance(df.index, pd.DatetimeIndex)
    assert df.index.is_monotonic_increasing


def test_load_brent_prices_adds_log_columns(mixed_format_csv):
    df = load_brent_prices(mixed_format_csv)
    assert "LogPrice" in df.columns
    assert "LogReturn" in df.columns
    # First row's log return should be NaN (no prior day to diff against)
    assert pd.isna(df["LogReturn"].iloc[0])


def test_load_brent_prices_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_brent_prices("does_not_exist.csv")


def test_load_brent_prices_missing_column_raises(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("NotDate,NotPrice\n1,2\n")
    with pytest.raises(ValueError):
        load_brent_prices(path)


def test_load_events_parses_date_column(events_csv):
    df = load_events(events_csv)
    assert "date" in df.columns
    assert pd.api.types.is_datetime64_any_dtype(df["date"])


def test_load_events_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_events("does_not_exist.csv")
