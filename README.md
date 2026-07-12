# Brent Oil Change Point Analysis

Change point analysis and statistical modeling of Brent crude oil prices to
detect structural breaks and associate them with major political and
economic events (OPEC decisions, geopolitical conflicts, sanctions, etc.).


## Objectives

1. Identify key events that significantly impacted Brent oil prices over
   the past several decades.
2. Quantify how much these events affect price changes using Bayesian
   change point detection (PyMC).
3. Provide clear, data-driven insights for investment strategy, policy, and
   operational planning, delivered via an interactive dashboard.

## Data Source

- **Brent oil prices:** `data/BrentOilPrices.csv` daily Brent crude oil
  prices in USD/barrel, 20-May-1987 to 14-Nov-2022.
- **Key events dataset:** `data/key_events_verified.csv` 13 fact-checked
  geopolitical, OPEC, and economic events with approximate dates,
  descriptions, and cited sources.

## Project Structure

```
├── .vscode/
│   └── settings.json
├── .github/
│   └── workflows/
│       └── unittests.yml
├── .gitignore
├── requirements.txt
├── README.md
├── data/
│   ├── BrentOilPrices.csv
│   └── key_events_verified.csv
├── docs/
│   └── analysis_workflow.md
├── src/
│   ├── __init__.py
│   └── data_loader.py
├── notebooks/
│   ├── __init__.py
│   └── 01_eda.ipynb
├── tests/
│   ├── __init__.py
│   ├── test_placeholder.py
│   └── test_data_loader.py
└── scripts/
    ├── __init__.py
    └── README.md
```

## Setup

```bash
git clone <your-repo-url>
cd brent-oil-change-point-analysis
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Running the Tests

```bash
pytest tests/ -v
```

## Running the EDA Notebook

```bash
jupyter notebook notebooks/01_eda.ipynb
```

## Tasks

- **Task 1** Workflow definition (`docs/analysis_workflow.md`), event
  research (`data/key_events_verified.csv`), EDA and change point model
  explanation (`notebooks/01_eda.ipynb`).
- **Task 2** Bayesian change point modeling in PyMC, convergence checks,
  impact quantification, association with events.
- **Task 3** Interactive dashboard (Flask backend + React frontend).
