"""
data_loader.py

Utility functions for loading and preparing the Brent oil price dataset
and the associated key-events dataset for change point analysis.

The raw Brent price CSV contains two different date formats across its
history (e.g. "20-May-87" for older rows and "Nov 08, 2022" for newer
rows), so date parsing tries multiple known formats rather than assuming
a single one.
"""

from pathlib import Path

import numpy as np
import pandas as pd

# Date formats observed in the raw BrentOilPrices.csv file.
_KNOWN_DATE_FORMATS = ["%d-%b-%y", "%b %d, %Y"]


def _parse_mixed_dates(date_series: pd.Series) -> pd.Series:
    """
    Parse a Series of date strings that may follow more than one format.

    Tries each known format in turn for the rows that don't already
    parse, rather than assuming the whole column shares one format.

    Parameters
    ----------
    date_series : pd.Series
        Raw date strings.

    Returns
    -------
    pd.Series
        Parsed datetime64 values. Rows that cannot be parsed by any known
        format are left as NaT.
    """
    parsed = pd.to_datetime(pd.Series([pd.NaT] * len(date_series)))

    remaining_mask = parsed.isna()
    for fmt in _KNOWN_DATE_FORMATS:
        if not remaining_mask.any():
            break
        attempt = pd.to_datetime(
            date_series[remaining_mask], format=fmt, errors="coerce"
        )
        parsed.loc[remaining_mask] = attempt
        remaining_mask = parsed.isna()

    return parsed


def load_brent_prices(filepath: str | Path) -> pd.DataFrame:
    """
    Load and clean the Brent oil daily price dataset.

    Parameters
    ----------
    filepath : str or Path
        Path to the BrentOilPrices.csv file (expects columns Date, Price).

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by date (ascending), with columns:
        - Price       : raw price in USD/barrel
        - LogPrice    : natural log of Price
        - LogReturn   : first difference of LogPrice (daily log return)

    Raises
    ------
    FileNotFoundError
        If filepath does not exist.
    ValueError
        If the file is missing expected columns, is empty, or contains
        no parseable dates / no valid rows after cleaning.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Brent price file not found at: {filepath}")

    try:
        df = pd.read_csv(filepath)
    except pd.errors.EmptyDataError as exc:
        raise ValueError(f"Brent price file is empty: {filepath}") from exc
    except pd.errors.ParserError as exc:
        raise ValueError(f"Could not parse Brent price file: {filepath}") from exc

    expected_cols = {"Date", "Price"}
    if not expected_cols.issubset(df.columns):
        missing = expected_cols - set(df.columns)
        raise ValueError(f"Missing expected column(s) {missing} in {filepath}")

    df["Date"] = _parse_mixed_dates(df["Date"])
    n_unparsed = df["Date"].isna().sum()
    if n_unparsed:
        print(f"Warning: dropping {n_unparsed} row(s) with unparseable dates.")
    df = df.dropna(subset=["Date"])

    df["Price"] = pd.to_numeric(df["Price"], errors="coerce")
    n_bad_price = df["Price"].isna().sum()
    if n_bad_price:
        print(f"Warning: dropping {n_bad_price} row(s) with non-numeric price.")
    df = df.dropna(subset=["Price"])

    if df.empty:
        raise ValueError(f"No valid rows remaining after cleaning: {filepath}")

    df = df.sort_values("Date").drop_duplicates(subset="Date").set_index("Date")

    df["LogPrice"] = np.log(df["Price"])
    df["LogReturn"] = df["LogPrice"].diff()

    return df


def load_events(filepath: str | Path) -> pd.DataFrame:
    """
    Load the structured key-events dataset used to interpret detected
    change points.

    Parameters
    ----------
    filepath : str or Path
        Path to key_events_verified.csv.

    Returns
    -------
    pd.DataFrame
        Events DataFrame with a parsed datetime `date` column.

    Raises
    ------
    FileNotFoundError
        If filepath does not exist.
    ValueError
        If the file is missing an expected `date` column.
    """
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"Events file not found at: {filepath}")

    df = pd.read_csv(filepath)
    if "date" not in df.columns:
        raise ValueError(f"Expected a 'date' column in {filepath}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df
