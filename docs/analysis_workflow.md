# Analysis Workflow: Change Point Analysis of Brent Oil Prices

**Project:** Change Point Analysis and Statistical Modeling of Time Series Data
**Data source:** Brent crude oil daily prices, USD/barrel, 20-May-1987 to 14-Nov-2022 (`data//raw/BrentOilPrices.csv`)

## 1. Objective

Detect and quantify structural breaks in Brent oil prices using Bayesian
change point analysis, and associate detected breaks with major
geopolitical and economic events to support investment, policy, and
operational decisions.

## 2. Planned Analysis Steps (Data Loading → Insight Generation)

1. **Data loading & cleaning** load `BrentOilPrices.csv` via
   `src/data_loader.py`, which parses the two date formats present in the
   file, coerces prices to numeric, drops unparseable rows with a warning,
   and raises clear errors for a missing file or missing columns.
2. **Exploratory data analysis** plot the raw price series and daily log
   returns; assess trend, stationarity (Augmented Dickey-Fuller test), and
   volatility (rolling standard deviation, visual volatility clustering).
   See `notebooks/01_eda.ipynb`.
3. **Event research** compile a structured dataset of key geopolitical,
   OPEC, and economic events with approximate dates
   (`data/key_events_verified.csv`), each fact-checked against a cited
   source.
4. **Bayesian change point modeling** fit a change point model in PyMC
   (switch point `tau`, before/after parameters, `pm.math.switch`,
   MCMC sampling via `pm.sample()`) on log returns, motivated by the
   stationarity results from step 2.
5. **Model interpretation** check MCMC convergence (r_hat, trace plots),
   extract the posterior distribution of `tau`, and quantify the shift in
   parameters (e.g. mean return) before vs. after the change point.
6. **Associating changes with causes** compare detected change point
   date(s) against the events dataset and formulate hypotheses about likely
   drivers, explicitly distinguishing statistical association from proven
   causation (see Section 4).
7. **Insight generation & reporting** summarize quantified findings
   (e.g. "mean daily return shifted from X to Y around [date], coinciding
   with [event]") for stakeholders, and present interactively via the
   Task 3 dashboard.

## 3. Change Point Models: Purpose & Expected Outputs

A change point model detects points in time where the statistical
properties of a series (mean, variance, trend) shift abruptly, rather than
assuming one fixed set of parameters governs the whole series. This suits
oil prices well, since they react to discrete shocks (wars, OPEC decisions,
sanctions) rather than only gradual change.

**Expected outputs:**
- Identified change point date(s): a posterior distribution over `tau`,
  summarized by its most likely value and uncertainty range.
- New parameter values: posterior distributions for the "before" and
  "after" regimes (e.g. mean log return), enabling probabilistic statements
  about the size of the shift.
- Quantified impact: magnitude/direction of the change, reportable
  alongside a candidate real-world cause.

**Inherent limitations:** a detected change point coinciding with a known
event is an association in time, not proof of causation (see Section 4);
the baseline model assumes a single break, which may under-fit a series
with multiple regimes; and results are sensitive to whether the model
targets price, log price, or log returns.

## 4. Assumptions and Limitations

### Assumptions
- The Brent price series is treated as a reasonably complete and accurate
  daily record; expected gaps (weekends/holidays) are not treated as data
  errors.
- Events in `key_events_verified.csv` are plausible drivers of price
  movements based on documented, cited sources, not confirmed causes.
- A single change point model is used as the Task 2 baseline; the series
  may in reality contain multiple structural breaks.
- Modeling is performed primarily on log returns (shown to be stationary
  in the EDA), rather than raw price (shown to be non-stationary).

### Limitations
- **Statistical correlation in time vs. causal impact:** This is the
  central limitation of the whole analysis. A change point model identifies
  *when* the statistical properties of the price series shifted — it does
  **not** prove that a nearby event *caused* that shift. Multiple events
  often cluster in time, and unobserved factors (currency movements,
  broader macroeconomic conditions, speculative trading activity) may
  independently explain part of the shift. Any event association reported
  in this project should be read as a **data-informed hypothesis**, not a
  causal claim.
- **Single change point limitation:** given the 35-year span of the
  dataset, multiple structural breaks almost certainly exist; extending to
  multiple change points is a natural next step beyond the baseline model.
- **Exogenous confounders:** the baseline model does not incorporate other
  macroeconomic variables (GDP, inflation, exchange rates) that may
  independently explain part of the price variation.
- **Event date precision:** some events (e.g. a multi-day OPEC meeting or
  an extended crisis) span a range rather than a single date, making exact
  alignment with a detected change point approximate.

## 5. Deliverables (Task 1)

- This workflow document (`docs/analysis_workflow.md`)
- `data/key_events_verified.csv`  13 fact-checked events with citations
- `notebooks/01_eda.ipynb` EDA notebook (raw price plot, log return plot,
  stationarity/volatility analysis, change point model explanation)
- `src/data_loader.py` reusable, error-handled data loading module
- `tests/test_data_loader.py` unit tests for the loading module