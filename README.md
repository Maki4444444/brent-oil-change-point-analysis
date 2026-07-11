# Brent Oil Change Point Analysis

Change point analysis and statistical modeling of Brent oil prices to detect
structural breaks and associate them with major political and economic events
(OPEC decisions, geopolitical conflicts, sanctions, etc.).


## Objectives

1. Identify key events that significantly impacted Brent oil prices over the
   past decade+.
2. Quantify how much these events affect price changes using Bayesian change
   point detection (PyMC).
3. Provide clear, data-driven insights for investment strategy, policy, and
   operational planning, delivered via an interactive dashboard.

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
├── src/
│   └── __init__.py
├── notebooks/
│   ├── __init__.py
│   └── README.md
├── tests/
│   └── __init__.py
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

## Data

Historical Brent oil prices (daily, USD/barrel), 20-May-1987 to 30-Sep-2022.
Place the raw CSV in `data/raw/` (not tracked in git see `.gitignore`).

## Tasks

- **Task 1** Workflow definition, event research (10–15 key events), EDA,
  assumptions & limitations.
- **Task 2** Bayesian change point modeling in PyMC, convergence checks,
  impact quantification, association with events.
- **Task 3** Interactive dashboard (Flask backend + React frontend).

