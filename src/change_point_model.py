"""
change_point_model.py

Reusable functions for building, running, and summarizing a single
Bayesian change point model (mean-shift, PyMC) on a 1-D price series.

The model structure follows the standard "switch point" formulation:
  - tau      ~ DiscreteUniform(0, n-1)      (the unknown change point index)
  - mu1, mu2 ~ Normal(...)                  (mean before / after tau)
  - sigma    ~ HalfNormal(...)              (shared observation noise)
  - mu       = switch(tau >= idx, mu1, mu2)
  - obs      ~ Normal(mu, sigma), observed = series
"""

from dataclasses import dataclass

import numpy as np
import pandas as pd
import pymc as pm


@dataclass
class ChangePointResult:
    """Container for a fitted change point model and derived summaries."""

    trace: "pm.backends.base.MultiTrace"
    dates: pd.DatetimeIndex
    series: np.ndarray
    tau_mode_idx: int
    tau_mode_date: pd.Timestamp
    mu1_mean: float
    mu2_mean: float
    pct_change: float


def fit_change_point_model(
    series: pd.Series,
    mu_sigma: float | None = None,
    obs_sigma: float | None = None,
    draws: int = 2000,
    tune: int = 1000,
    chains: int = 4,
    random_seed: int = 42,
) -> ChangePointResult:
    """
    Fit a single mean-shift Bayesian change point model to a price (or
    return) series indexed by date.

    Parameters
    ----------
    series : pd.Series
        The observed series (e.g. Price or LogReturn), indexed by date,
        with no missing values.
    mu_sigma : float, optional
        Prior standard deviation for mu1/mu2. Defaults to a data-driven
        heuristic (roughly the series' own standard deviation).
    obs_sigma : float, optional
        Prior scale (HalfNormal) for the observation noise. Defaults to a
        data-driven heuristic.
    draws, tune, chains : int
        MCMC sampling configuration.
    random_seed : int
        Seed for reproducibility.

    Returns
    -------
    ChangePointResult
        Fitted trace plus convenience summaries (mode of tau as a date,
        posterior mean of mu1/mu2, and the implied percentage change).

    Raises
    ------
    ValueError
        If the series is empty or contains NaN values.
    """
    if series.isna().any():
        raise ValueError("Input series contains NaN values; drop or fill them first.")
    if len(series) < 2:
        raise ValueError("Input series must have at least 2 observations.")

    values = series.values.astype(float)
    n = len(values)
    idx = np.arange(n)

    if mu_sigma is None:
        mu_sigma = float(values.std()) * 2 if values.std() > 0 else 1.0
    if obs_sigma is None:
        obs_sigma = float(values.std()) if values.std() > 0 else 1.0

    with pm.Model():
        tau = pm.DiscreteUniform("tau", lower=0, upper=n - 1)
        mu1 = pm.Normal("mu1", mu=float(values.mean()), sigma=mu_sigma)
        mu2 = pm.Normal("mu2", mu=float(values.mean()), sigma=mu_sigma)
        sigma = pm.HalfNormal("sigma", sigma=obs_sigma)

        mu = pm.math.switch(tau >= idx, mu1, mu2)
        pm.Normal("obs", mu=mu, sigma=sigma, observed=values)

        trace = pm.sample(
            draws=draws,
            tune=tune,
            chains=chains,
            cores=1,
            random_seed=random_seed,
            progressbar=False,
        )

    tau_samples = trace.posterior["tau"].values.flatten()
    tau_vals, tau_counts = np.unique(tau_samples, return_counts=True)
    tau_mode_idx = int(tau_vals[np.argmax(tau_counts)])

    mu1_mean = float(trace.posterior["mu1"].values.mean())
    mu2_mean = float(trace.posterior["mu2"].values.mean())
    pct_change = (mu2_mean - mu1_mean) / abs(mu1_mean) * 100 if mu1_mean != 0 else float("nan")

    return ChangePointResult(
        trace=trace,
        dates=series.index,
        series=values,
        tau_mode_idx=tau_mode_idx,
        tau_mode_date=series.index[tau_mode_idx],
        mu1_mean=mu1_mean,
        mu2_mean=mu2_mean,
        pct_change=pct_change,
    )


def nearest_events(events_df: pd.DataFrame, target_date: pd.Timestamp, n: int = 3) -> pd.DataFrame:
    """
    Return the n events (from a loaded events DataFrame with a `date`
    column) closest in time to a target date, with a signed day-offset
    column for interpretation.

    Parameters
    ----------
    events_df : pd.DataFrame
        Events dataset with a `date` column (see src/data_loader.load_events).
    target_date : pd.Timestamp
        The detected change point date to compare against.
    n : int
        Number of nearest events to return.

    Returns
    -------
    pd.DataFrame
        Copy of the n nearest rows, sorted by absolute distance, with an
        added `days_from_change_point` column (negative = event occurred
        before the detected change point).
    """
    out = events_df.copy()
    out["days_from_change_point"] = (out["date"] - target_date).dt.days
    out["abs_days"] = out["days_from_change_point"].abs()
    out = out.sort_values("abs_days").head(n).drop(columns="abs_days")
    return out
