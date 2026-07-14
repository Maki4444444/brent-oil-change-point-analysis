"""
export_change_points.py

Regenerates data/change_point_results.json, the static export of the
Task 2 Bayesian change point model results that the dashboard backend
serves (see app.py's /api/change-points endpoint).

This script does NOT re-run PyMC/MCMC itself (the dashboard backend has
no PyMC dependency by design). Instead, it holds the source-of-truth
values that were produced by notebooks/02_change_point_model.ipynb.

If you re-run that notebook with different data, priors, or sampling
settings, update the MODELS list below to match the new printed results,
then re-run this script:

    python scripts/export_change_points.py
"""

import json
from pathlib import Path

OUTPUT_PATH = Path(__file__).resolve().parent.parent / "data" / "change_point_results.json"

DATASET_RANGE = {
    "start": "1987-05-20",
    "end": "2022-11-14",
    "n_observations": 9011,
}

# Source: notebooks/02_change_point_model.ipynb, Sections 3-4.
MODELS = [
    {
        "id": "baseline",
        "label": "Full History Baseline",
        "description": (
            "Single change point fit over the entire 1987-2022 price history. "
            "Identifies the single largest structural break (the mid-2000s "
            "commodity supercycle), not a specific discrete event."
        ),
        "window_start": "1987-05-20",
        "window_end": "2022-11-14",
        "change_point_date": "2005-02-22",
        "mean_before": 21.42,
        "mean_after": 75.60,
        "pct_change": 252.9,
        "r_hat": {"tau": 1.00, "mu1": 1.00, "mu2": 1.00, "sigma": 1.00},
        "associated_event_id": None,
        "associated_event_name": None,
        "days_from_event": None,
    },
    {
        "id": "case_2014_opec",
        "label": '2014 OPEC "No Cut" Decision',
        "description": (
            "Focused window around OPEC's November 2014 decision to maintain "
            "output despite falling prices."
        ),
        "window_start": "2014-06-01",
        "window_end": "2015-03-01",
        "change_point_date": "2014-11-12",
        "mean_before": 99.27,
        "mean_after": 59.13,
        "pct_change": -40.4,
        "r_hat": {"tau": 1.02, "mu1": 1.00, "mu2": 1.01, "sigma": 1.00},
        "associated_event_id": 8,
        "associated_event_name": "OPEC Declines to Cut Production (Thanksgiving Meeting)",
        "days_from_event": 15,
    },
    {
        "id": "case_2020_pricewar",
        "label": "2020 Saudi-Russia Price War / COVID-19",
        "description": (
            "Focused window around the collapse of the OPEC+ alliance and the "
            "onset of the COVID-19 pandemic demand shock."
        ),
        "window_start": "2020-01-01",
        "window_end": "2020-06-30",
        "change_point_date": "2020-03-06",
        "mean_before": 59.14,
        "mean_after": 29.21,
        "pct_change": -50.6,
        "r_hat": {"tau": 1.00, "mu1": 1.00, "mu2": 1.00, "sigma": 1.00},
        "associated_event_id": 10,
        "associated_event_name": "Collapse of Saudi-Russia OPEC+ Alliance",
        "days_from_event": 0,
    },
    {
        "id": "case_2022_ukraine",
        "label": "2022 Russian Invasion of Ukraine",
        "description": (
            "Focused window around Russia's invasion of Ukraine and the "
            "lead-up period of escalating tensions."
        ),
        "window_start": "2021-11-01",
        "window_end": "2022-06-01",
        "change_point_date": "2022-02-03",
        "mean_before": 81.42,
        "mean_after": 109.51,
        "pct_change": 34.5,
        "r_hat": {"tau": 1.01, "mu1": 1.00, "mu2": 1.00, "sigma": 1.00},
        "associated_event_id": 13,
        "associated_event_name": "Russian Invasion of Ukraine",
        "days_from_event": -21,
    },
]


def main():
    output = {
        "generated_from": "notebooks/02_change_point_model.ipynb",
        "generated_note": (
            "Static export of Task 2 Bayesian change point model results, "
            "precomputed so the dashboard backend does not require PyMC at "
            "runtime."
        ),
        "dataset_range": DATASET_RANGE,
        "models": MODELS,
    }
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w") as f:
        json.dump(output, f, indent=2)
    print(f"Wrote {OUTPUT_PATH} ({len(MODELS)} models)")


if __name__ == "__main__":
    main()
