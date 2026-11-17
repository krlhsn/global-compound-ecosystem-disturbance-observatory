# When Ecosystem Disturbances Compound

<p align="center">
  <img src="assets/observatory-banner.svg" alt="Scientific illustration of a globe and three intersecting environmental signal paths" width="100%">
</p>

<p align="center">
  <strong>Observe the signals. Model the overlap. Respect the uncertainty.</strong><br>
  A global research framework for probabilistic analysis of compound ecosystem disturbance.
</p>

<p align="center">
  <a href="https://github.com/krlhsn/global-compound-ecosystem-disturbance-observatory/actions/workflows/tests.yml"><img alt="Research workflow checks" src="https://github.com/krlhsn/global-compound-ecosystem-disturbance-observatory/actions/workflows/tests.yml/badge.svg"></a>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="React" src="https://img.shields.io/badge/interface-React-149ECA?logo=react&logoColor=white">
  <img alt="Reproducible research" src="https://img.shields.io/badge/research-reproducible%20framework-47765e">
  <img alt="MIT License" src="https://img.shields.io/badge/license-MIT-7A5CFA">
</p>

---

## Overview

**When Ecosystem Disturbances Compound** investigates whether drought, unusually high burned-area activity and vegetation-greenness stress can be combined to estimate the probability of compound environmental disturbance across global terrestrial ecosystems.

The repository contains a documented research specification, Python analysis workflow, offline React explainer, data contract, quality-control rules, source register, reproducibility safeguards and automated software checks.

**Evidence boundary:** the repository does not contain extracted global environmental rasters or empirical results. The software and research framework are implemented, but no observed event prevalence, regional ranking, fitted-model score or predictive-performance claim is presented. The interface and documentation never substitute invented values for measurements.

## Research question

Can multiple environmental indicators estimate the probability of compound ecosystem disturbances across global terrestrial ecosystems, and how does predictive performance vary across ecological regions and forecast lead times?

The proposed retrospective study uses a 0.5° terrestrial grid and monthly observations. The target period is **May 2001–December 2024**. Earlier ERA5-Land records are required for the fixed soil-moisture reference.

## Environmental indicators

| Signal | Dataset and proxy | Proposed event threshold |
|---|---|---|
| **D — Drought** | ERA5-Land depth-weighted root-zone soil-moisture proxy, smoothed over three months | Standardised anomaly ≤ −1.0 SD against the fixed 1981–2000 calendar-month reference |
| **F — Fire activity** | MCD64A1.061 burned-area fraction over valid, full-month mapped land | At or above the 90th percentile of positive training-period fractions by ecoregion × calendar month, with a biome fallback |
| **V — Vegetation stress** | MOD13C2.061 NDVI anomaly, with product-specific pixel QA | Standardised anomaly ≤ −0.5 SD against the 2001–2016 cell/calendar-month reference and at least 80% good-quality contributing area |

These are operational proxies, not interchangeable measures of drought, wildfire or ecosystem condition. Missing or unevaluable indicators remain missing.

### Compound-event definition

All three indicators must be evaluable. A cell-month is a compound event when at least two indicators are positive.

| Category | Definition |
|---|---|
| **DF** | Drought + fire activity |
| **DV** | Drought + vegetation stress |
| **FV** | Fire activity + vegetation stress |
| **DFV** | All three signals |
| **NONE** | Zero or one positive signal |
| **NOT_EVALUABLE** | At least one indicator is unavailable |

The binary outcome is **Y = 1** when D + F + V ≥ 2 and **Y = 0** otherwise. NOT_EVALUABLE is never converted into a negative outcome.

## Forecast design

For an origin month *t*, predictors use information available through *t*, including the current month and the two preceding months. Separate models estimate the outcome in the **exact** month *t+1* and the **exact** month *t+3*. An event occurring at any point within a three-month window is a different outcome and is not substituted for exact *t+3*.

| Period | Target years | Role |
|---|---:|---|
| Training | 2001–2016 | Estimate training-referenced thresholds and fit models |
| Validation | 2017–2020 | Review model behaviour and freeze design decisions |
| Locked test | 2021–2024 | One-time evaluation after the prior and analysis freeze |

The split is assigned by **target month**, not by predictor-origin year.

## Model comparison

Five regularised logistic-regression specifications are evaluated separately at each forecast horizon.

| Model | Predictor information |
|---|---|
| **M0 — Seasonal baseline** | Biome and target calendar month |
| **M1 — Drought-only** | Baseline + soil-moisture anomaly and drought history |
| **M2 — Fire-history-only** | Baseline + burned-area fraction and fire history |
| **M3 — Vegetation-only** | Baseline + NDVI anomaly and vegetation-stress history |
| **M4 — Combined** | D/F/V histories + temperature and precipitation histories |

Primary evaluation uses mean and total log₁₀ likelihood. Brier score and calibration gap provide complementary views of probabilistic quality. Event prevalence and evaluable sample counts accompany every score. Regional metrics use fractional cell–ecoregion area weights and minimum event/non-event sample requirements. Spatial-tile × target-year block bootstrap intervals are an approximation and are interpreted with tile-size sensitivity checks.

## Repository contents

| Path | Contents |
|---|---|
| `app/` | Interactive, offline React observatory interface |
| `analysis/` | Input validation, indicator derivation, event labels, forecasting and probabilistic evaluation |
| `tests/` | Automated checks for event logic, validation, forecast alignment and end-to-end analysis software |
| `.github/workflows/` | Python tests and React production-build checks |
| `assets/` | Custom scientific banner artwork |
| `gee/` | Google Earth Engine source-preparation and export design |
| `data/templates/` | Empty CSV header templates; no fabricated observations |
| `docs/` | Architecture, reproducibility and scientific-limitations documentation |
| `RESEARCH_PROTOCOL.md` | Full research specification and analysis decisions |
| `DATA_DICTIONARY.md` | Input schema, source QA and derived-variable contract |
| `SOURCES.md` | Official source products, versions, citations and attribution |
| `PILOT_GATE.md` | Development/validation procedure and locked-test release requirements |
| `analysis_freeze.template.json` | Hash-based protocol, data and code freeze schema |
| `extraction_manifest.template.json` | Source retrieval, QA review and export-provenance schema |
| `AI-NOTES.md` | AI-use disclosure and author decision record |
| `CITATION.cff` | Software citation metadata |

## Running the project

The repository's automated workflow installs dependencies, runs the Python test suite, compiles the analysis entry point and builds the React interface on every push or pull request to `main`.

For local development, Python 3.10+ and Node.js 20+ are supported.

```bash
git clone https://github.com/krlhsn/global-compound-ecosystem-disturbance-observatory.git
cd global-compound-ecosystem-disturbance-observatory

# Python analysis and tests
python -m pip install -e ".[dev]"
python -m pytest

# React interface
npm install
npm run dev
```

The React application is an explanatory interface, not a live data dashboard. It makes no runtime network requests and contains no fabricated maps, counts or scores.

## Prepared data contract

The analysis accepts two externally prepared CSV files:

- `cell_monthly.csv`: one row per 0.5° terrestrial grid cell and calendar month, including environmental variables and quality-coverage fields.
- `cell_ecoregion_weights.csv`: one row per grid-cell/ecoregion intersection, containing the fractional terrestrial-area weight.

Input rows must be retained when a product is unavailable; missing observations are encoded as NA, never zero. Exact columns, units, QA rules and validation constraints are defined in [DATA_DICTIONARY.md](DATA_DICTIONARY.md). Large source rasters and intermediate exports are intentionally excluded from Git.

## Data sources

The study specification uses the following official products:

- [ERA5-Land monthly aggregated data](https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_MONTHLY_AGGR) for soil water, temperature and precipitation.
- [MOD13C2.061](https://doi.org/10.5067/MODIS/MOD13C2.061) from NASA LP DAAC / USGS Earthdata for monthly NDVI and vegetation-index quality. The current reviewed Earth Engine MODIS catalogue did not confirm a MOD13C2.061 collection ID, so the extraction plan does not assume one.
- [MCD64A1.061](https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD64A1) for monthly burned area and pixel-level quality.
- [RESOLVE Ecoregions 2017](https://developers.google.com/earth-engine/datasets/catalog/RESOLVE_ECOREGIONS_2017) for ecological regions, biomes and realms.

Product-specific QA, data access, attribution and known limitations are recorded in [SOURCES.md](SOURCES.md). The repository contains no source raster exports; retrieval dates, asset identifiers and output checksums must be recorded in the extraction manifest for any empirical run.

## Scientific interpretation

This is a retrospective research framework, not an operational early-warning service, ecological diagnosis, fire-detection system or conservation decision tool. NDVI is a greenness proxy; burned area is not synonymous with wildfire; soil moisture is one drought-related signal. Spatial aggregation, source QA, temporal coverage, ecological heterogeneity, missingness and confounding can all affect conclusions.

A predicted probability is conditional on the data and model specification. It is not a causal explanation and does not establish that a disturbance will occur. The 2021–2024 test is protected from design decisions until an author-authored prior and analysis freeze are recorded. The personal prior is supplied privately at analysis time and is not stored in the public repository.

## Author

**Kamrul Hassan**  
[GitHub](https://github.com/krlhsn) · [LinkedIn](https://www.linkedin.com/in/krlhsn/) · [ORCID](https://orcid.org/0009-0008-2990-1036)

## License and citation

Original code and documentation are released under the [MIT License](LICENSE). Upstream datasets retain their own terms; the MIT license does not relicense external data. See [CITATION.cff](CITATION.cff) and [SOURCES.md](SOURCES.md) for citation and attribution details.

---

<p align="center"><em>Compound risk is a question of overlapping signals — and of being honest about what those signals can tell us.</em></p>
