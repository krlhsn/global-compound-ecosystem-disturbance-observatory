# When Ecosystem Disturbances Compound

<p align="center">
  <img src="assets/observatory-banner.svg" alt="Global ecosystem observatory banner with a world grid, vegetation, drought and fire signal motifs" width="100%">
</p>

<p align="center">
  <strong>Observe the signals. Model the overlap. Respect the uncertainty.</strong><br>
  A global, retrospective research framework for studying compound ecosystem disturbance with probabilistic models.
</p>

<p align="center">
  <a href="https://github.com/krlhsn/global-compound-ecosystem-disturbance-observatory/actions/workflows/tests.yml"><img alt="Analysis tests" src="https://github.com/krlhsn/global-compound-ecosystem-disturbance-observatory/actions/workflows/tests.yml/badge.svg"></a>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/interface-React-149ECA?logo=react&logoColor=white">
  <img alt="Research status" src="https://img.shields.io/badge/status-research%20prototype-c47b42">
  <img alt="Data status" src="https://img.shields.io/badge/empirical%20data-pending-d18a36">
  <img alt="License MIT" src="https://img.shields.io/badge/license-MIT-7A5CFA">
</p>

---

## At a glance

**When Ecosystem Disturbances Compound** asks whether drought, unusually high burned-area activity and vegetation-greenness stress can be combined to estimate the probability of compound environmental disturbance across global terrestrial ecosystems.

The project pairs a transparent research protocol with a Python analysis workflow and an offline React explainer. It is designed around a crucial distinction: **a probabilistic model should express uncertainty, not disguise missing data or turn a proxy into a claim about ecosystem health.**

> **Research status:** this repository currently contains the protocol, analysis implementation, interface and reproducibility materials. The global input rasters have not yet been extracted and quality-controlled. No empirical event prevalence, regional ranking, fitted-model score or predictive-performance result is claimed.

## Research question

Can multiple environmental indicators estimate the probability of compound ecosystem disturbances across global terrestrial ecosystems, and how does predictive performance vary across ecological regions and forecast lead times?

The proposed study is retrospective and uses a 0.5° terrestrial grid with monthly observations. Its target window is **May 2001–December 2024**; the soil-moisture reference requires earlier ERA5-Land history.

## The three environmental signals

| Signal | Proposed proxy | Primary event threshold |
|---|---|---|
| **D — Drought** | ERA5-Land root-zone soil-moisture proxy, smoothed over three months | Standardised anomaly ≤ −1.0 SD against the fixed 1981–2000 calendar-month reference |
| **F — Fire activity** | MCD64A1.061 burned-area fraction over valid, full-month mapped land | At or above the 90th percentile of positive training-period fractions by ecoregion × calendar month, with a biome fallback |
| **V — Vegetation stress** | MOD13C2.061 NDVI anomaly | Standardised anomaly ≤ −0.5 SD against the 2001–2016 cell/calendar-month reference; ≥80% good-quality coverage |

These are operational proxies, not interchangeable measures of drought, wildfire or ecosystem condition. Missing or unevaluable indicators remain missing.

### What counts as a compound event?

All three indicators must be evaluable. A cell-month is a compound event when at least two are positive:

- `DF`: drought + fire activity
- `DV`: drought + vegetation stress
- `FV`: fire activity + vegetation stress
- `DFV`: all three signals
- `NONE`: zero or one positive signal
- `NOT_EVALUABLE`: at least one indicator is unavailable

The binary outcome is (Y=1) when (D+F+V\geq2), otherwise (Y=0). `NOT_EVALUABLE` is not a negative outcome.

## Forecast design

For an origin month (t), predictors use information available through (t), including the current month and the previous two months. Separate models estimate the outcome in the **exact** month (t+1) and the **exact** month (t+3). An exploratory three-month event window, if later added, must be reported separately.

| Period | Target years | Purpose |
|---|---:|---|
| Training | 2001–2016 | Estimate training-referenced thresholds and fit models |
| Validation | 2017–2020 | Review model behaviour and freeze design decisions |
| Locked test | 2021–2024 | One-time evaluation after a student-authored prior and analysis freeze |

The split is assigned by **target month**, not simply by predictor-origin year. Test outcomes remain gated in the analysis program.

## Model comparison

Five regularised logistic-regression specifications are planned for each forecast horizon:

| Model | Information supplied |
|---|---|
| **M0 — Seasonal baseline** | Biome and target calendar month |
| **M1 — Drought-only** | Baseline context + soil-moisture anomaly and drought history |
| **M2 — Fire-history-only** | Baseline context + burned-area fraction and fire history |
| **M3 — Vegetation-only** | Baseline context + NDVI anomaly and vegetation-stress history |
| **M4 — Combined** | D/F/V histories + temperature and precipitation histories |

Primary evaluation uses mean and total log₁₀ likelihood. Brier score and calibration gap provide complementary views of probabilistic quality. Event prevalence and sample counts must accompany scores. Spatial and temporal dependence is addressed with a 5° spatial-tile × target-year block-bootstrap approximation; tile-size sensitivity is required before strong interpretation.

## What is in this repository?

- **[Research protocol](RESEARCH_PROTOCOL.md)** — question, study design, indicator definitions, forecast horizons, model plan, evaluation, sensitivity analysis and scientific limitations.
- **[Data dictionary](DATA_DICTIONARY.md)** — exact monthly input schema, quality fields and cell–ecoregion crosswalk contract.
- **[Sources and attribution](SOURCES.md)** — official data products, versioning, access routes and attribution notes.
- **[Pilot gate](PILOT_GATE.md)** — the boundary between development work and test-set release.
- **[Python analysis](analysis/feasibility_pilot.py)** — validates input tables, builds D/F/V labels, constructs lagged forecasts, fits five model specifications and writes development/validation outputs.
- **[React explainer](app/App.jsx)** — offline interface describing the research design without fabricated maps, counts or scores.
- **[Extraction plan](gee/EXTRACTION_PLAN.md)** — partitioning and quality-control plan for preparing data in Google Earth Engine.
- **[Documentation](docs/)** — architecture, reproducibility and interpretation guidance.
- **[Tests](tests/)** and **[GitHub Actions](.github/workflows/tests.yml)** — automated checks for the core event and forecast logic.

## Quick start

### 1. Set up the analysis environment

Python 3.10 or newer is required.

```bash
git clone https://github.com/krlhsn/global-compound-ecosystem-disturbance-observatory.git
cd global-compound-ecosystem-disturbance-observatory
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

### 2. Validate a prepared input table

After preparing a real `cell_monthly.csv` following the [data dictionary](DATA_DICTIONARY.md):

```bash
python analysis/feasibility_pilot.py \
  --input data/cell_monthly.csv \
  --crosswalk data/cell_ecoregion_weights.csv \
  --output pilot_outputs
```

By default, this writes **development and validation** outputs only. It does not expose 2021–2024 test scores.

### 3. Run the tests

```bash
python -m pytest
```

### 4. Run the explainer interface locally

```bash
npm install
npm run dev
```

The React app is a methodological explainer, not a live dashboard. It makes no runtime requests and does not display synthetic values as observed environmental data.

## Expected data

The analysis expects two prepared CSV files:

1. `cell_monthly.csv`: one row per 0.5° terrestrial grid cell and calendar month, with environmental variables already quality-filtered and area-aggregated.
2. `cell_ecoregion_weights.csv`: one row per grid-cell/ecoregion intersection, containing fractional terrestrial-area weights.

Rows must be retained for months with incomplete product coverage. Represent missing source values as `NA`; do not convert missing observations to zero. The full extraction provenance, product versions, QA logic and checksums belong in a separate manifest.

The project does not redistribute the upstream global raster products. They must be retrieved through their official providers and processed under their access terms.

## Responsible interpretation

This is a **research prototype**, not an operational early-warning service, ecological diagnosis, fire-detection system or conservation decision tool. NDVI is a greenness proxy; burned area is not synonymous with wildfire; soil moisture is one drought-related signal. Spatial aggregation, source QA, temporal coverage, ecological heterogeneity, missingness and confounding can all affect conclusions.

A high probability is a model output conditional on the chosen data and specification. It is not a causal explanation, and it does not by itself establish that a disturbance will occur.

The locked test must not be opened until the student has written a genuine prior prediction, reviewed development/validation outputs and frozen the analysis. The assistant must not invent a personal prior on the student's behalf.

## Roadmap

- [x] Define the research question, indicator proxies and compound-event rule.
- [x] Specify exact t+1 and t+3 forecast targets and target-year splits.
- [x] Implement development/validation modelling and a locked-test release gate.
- [x] Build an offline explanatory interface.
- [x] Document required datasets, input schema and quality safeguards.
- [ ] Complete global raster extraction and independent QA review.
- [ ] Run and review the real-data development/validation pilot.
- [ ] Freeze the protocol, code hash and model decisions after validation review.
- [ ] Open the locked test once and preserve its output hashes.
- [ ] Add only verified, reproducible empirical results to the interface.

## Author

**Kamrul Hassan**  
[GitHub](https://github.com/krlhsn) · [LinkedIn](https://www.linkedin.com/in/krlhsn/) · [ORCID](https://orcid.org/0009-0008-2990-1036)

## Citation

See [CITATION.cff](CITATION.cff). Please cite the specific upstream data products and versions used in any derivative analysis.

## License

Code and documentation in this repository are released under the [MIT License](LICENSE), except where individual upstream datasets retain their own terms. The MIT license does not relicense external datasets.

---

<p align="center"><em>Compound risk is a question of overlapping signals — and of being honest about what the signals cannot tell us.</em></p>
