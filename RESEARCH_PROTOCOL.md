# Research Protocol — Version 1.1-draft

**Project:** When Ecosystem Disturbances Compound  
**Course context:** Stanford Probability for AI, Fall 2026  
**Status:** Complete pre-analysis specification for the research framework; empirical results are not part of this software release  
**Study target period:** May 2001–December 2024  
**Forecast horizons:** Exact t+1 and exact t+3

## 1. Research question

Can multiple environmental indicators estimate the probability of compound ecosystem disturbances across global terrestrial ecosystems, and how does predictive performance vary across ecological regions and forecast lead times?

This is an exploratory retrospective forecasting experiment, not a validated operational warning service.

## 2. Study design

- Spatial scope: global terrestrial land.
- Main spatial unit: 0.5° × 0.5° latitude–longitude grid cell.
- Ecological context: RESOLVE Ecoregions 2017 (846 terrestrial ecoregions, 14 biomes and 8 realms).
- Target months: May 2001–December 2024.
- Input history: October 1980–December 2024. October 1980 permits the first three-month rolling value entering the January 1981 soil-moisture reference.
- Primary horizon: outcome in the exact month t+1, using information available through origin month t.
- Secondary horizon: outcome in the exact month t+3, using the same information cutoff t.
- Optional exploratory horizon: at least one event in any of t+1, t+2 or t+3. This is a separate outcome and must never be substituted for exact t+3.

The same target-month window is used for both horizons. Samples are assigned to the split by **target month**, not by predictor-origin month.

## 3. Environmental indicators

All three definitions are proposed operational proxies and require review after the development-only extraction and QA pilot.

### D — Root-zone soil-moisture drought proxy

1. Use ERA5-Land volumetric soil-water layers 1–3, representing 0–7 cm, 7–28 cm and 28–100 cm.
2. Compute the depth-weighted 0–100 cm proxy:

   rootzone_sm = 0.07*swvl1 + 0.21*swvl2 + 0.72*swvl3

3. Calculate the rolling three-month mean ending in each month.
4. Standardise against the 1981–2000 distribution for the matching grid cell and calendar-ending month. Require at least 15 valid reference values and a positive reference standard deviation.
5. Set D=1 when the standardised anomaly is ≤−1.0; otherwise D=0 when valid.

This is a root-zone soil-moisture proxy, not a universal measure of meteorological, hydrological or agricultural drought.

### F — Unusually high burned-area activity

1. Use MCD64A1.061 monthly burned-area observations.
2. A pixel contributes to the valid mapped terrestrial denominator only when QA bit 0 indicates land, bit 1 indicates valid data and bit 2 indicates that the mapping period was not shortened.
3. Burned area is the area of valid full-month pixels with BurnDate > 0.
4. For unburned pixels (BurnDate = 0), require the MCD64A1 QA special-condition code in bits 5–7 to equal 0. Codes 1–5 flag special circumstances behind an unburned classification; those pixels are unevaluable and are excluded from the unburned denominator.
5. Exclude water, invalid/unmapped pixels, shortened-period pixels and special-condition unburned pixels from the corresponding numerator/denominator. Never convert these pixels to unburned.
6. Define valid_land_area_km2 as the area of full-month valid land pixels that are burned (BurnDate > 0) or reliably unburned (BurnDate = 0 and bits 5–7 = 0). Exclude special-condition unburned pixels and record their area fraction separately as fire_unburned_special_fraction, expressed as a fraction of cell terrestrial land area.
7. The valid-land, special-condition-unburned and shortened-period land-area fractions are mutually exclusive components and must sum to no more than 1.00 (allowing a 0.001 numerical tolerance).
8. Require valid full-month mapped terrestrial area to cover at least 80% of the cell's terrestrial land area. A nonzero shortened-area fraction does not automatically invalidate the whole coarse cell if the remaining valid coverage passes this rule.
9. For each ecoregion × calendar month, calculate the 90th percentile of positive burned-area fractions in 2001–2016. Require at least 30 positive cell-month observations. If sparse, use the matching biome × calendar-month threshold if that group also has at least 30 positive observations. Otherwise F is unevaluable.
10. Set F=1 when a valid positive fraction is at or above its applicable threshold; set F=0 for valid observations below threshold, including reliable zero-burn months.
11. Treat June 2001 as unavailable for F because the MCD64A1 record for that month is documented as heavily degraded by a Terra MODIS outage.

This definition detects locally unusual burned-area activity. It does not determine fire cause and does not equate every mapped burn with wildfire. Small burns may be omitted and cropland burning has lower confidence.

### V — Vegetation-greenness stress proxy

1. Use MOD13C2.061 monthly NDVI and apply the 0.0001 scale factor.
2. Apply the product-specific pixel reliability rank (SummaryQA / pixel reliability) = 0 (Good Data).
3. In DetailedQA, require bits 0–1 (VI Quality) = 00, bits 2–5 (VI Usefulness) ≤ 0001, bits 11–13 (Land/Water Mask) = 001 (land), and bits 14–15 (Geospatial Quality) ≥ 10 (more than 50% of the finer 1-km resolution contributed to the CMG pixel).
4. For MOD13C2, bits 14–15 are geospatial contribution quality. They are not the snow/ice and shadow flags used in other MOD13 products. Do not apply that incorrect interpretation to MOD13C2.
5. Verify exact V061 band names, fill values and bit decoding against the product guide before extraction. Record the implemented decoder and code hash.
6. Calculate the fraction of contributing terrestrial CMG pixel area passing all QA rules; require at least 80%.
7. Calculate the cell's calendar-month anomaly against its 2001–2016 reference mean and standard deviation. Require at least 12 valid reference values and a positive standard deviation.
8. Set V=1 when the standardised anomaly is ≤−0.5; otherwise V=0 when valid.

NDVI is a vegetation-greenness proxy, not a direct measure of ecosystem health. It responds to phenology, land management, disturbance, snow, cloud and other influences.

## 4. Compound-event definition

A cell-month receives a binary label only if D, F and V are all evaluable. Missing indicators are never converted to zero.

Let k = D + F + V:

| Category | Rule |
|---|---|
| DF | D=1, F=1, V=0 |
| DV | D=1, F=0, V=1 |
| FV | D=0, F=1, V=1 |
| DFV | D=1, F=1, V=1 |
| NONE | Zero or one positive indicator |
| NOT_EVALUABLE | At least one of D/F/V is unavailable |

The primary binary outcome is Y=1 when k≥2 and Y=0 otherwise. NOT_EVALUABLE is a missing target, not a negative event.

## 5. Spatial design and ecological aggregation

- Use a stable global 0.5° cell grid and persistent grid_id values.
- Intersect cell polygons with RESOLVE 2017 terrestrial ecoregions using a consistent land mask and an appropriate area calculation.
- Create a separate cell_ecoregion_weights.csv with one row per cell–ecoregion intersection and an area fraction of the cell's terrestrial land.
- Crosswalk fractions must sum to 1 within 0.001.
- Store a dominant ecoregion on the main cell record only when it covers at least 50% of cell land area; otherwise use MIXED.
- Use the dominant ecoregion or declared biome fallback for cell-level fire-threshold grouping.
- Use the full fractional-area crosswalk for regional summaries. Never duplicate one cell-month into multiple ecoregions for model fitting.

## 6. Predictors and forecast samples

For an origin month t, each feature may use only observations at t, t−1 and t−2. No target-month environmental variable or event label may enter the predictor set.

Create separate samples for horizons h∈{1,3}; each target is the outcome in the exact month t+h. Keep samples only when the target date is between May 2001 and December 2024. An event-anytime-in-three-months outcome, if studied, is reported separately.

## 7. Chronological split

| Split | Target years | Use |
|---|---:|---|
| Training | 2001–2016 | Estimate training-referenced NDVI/fire thresholds and fit models |
| Validation | 2017–2020 | Review behaviour, sensitivity and calibration; freeze design |
| Locked test | 2021–2024 | One-time evaluation after prior and analysis freeze |

Assign by target year. The soil-moisture reference is fixed at 1981–2000. For the one-time test evaluation, refit unchanged specifications on training + validation (target years 2001–2020) and score only 2021–2024.

## 8. Model comparison

Use regularised logistic regression, with all imputation, scaling and categorical encoding fitted inside the training pipeline.

| Model | Predictors |
|---|---|
| M0 — seasonal baseline | Biome and target calendar month |
| M1 — drought-only | Baseline + soil-moisture anomaly and D history |
| M2 — fire-history-only | Baseline + burned-area fraction and F history |
| M3 — vegetation-only | Baseline + NDVI anomaly and V history |
| M4 — combined | Baseline + D/F/V histories + temperature and precipitation histories |

Each history contains the origin month and the two preceding months. Fit separate models for t+1 and t+3. Do not use class weights unless a separately justified calibration correction is specified and evaluated.

## 9. Evaluation

Primary measures:
- Mean and total log10 likelihood of observed outcomes. Larger (less negative) mean values indicate better probabilistic fit.
- Calibration gap from equal-frequency probability bins, weighted by bin size.

Supplementary measure:
- Brier score.

Always report event prevalence, evaluable sample counts and coverage beside probability scores. Accuracy alone is inadequate for a potentially imbalanced target.

Regional metrics require fractional-area weights and at least 30 events and 30 non-events in that region. A 5° spatial tile × target-year block bootstrap provides preliminary uncertainty intervals for log10 likelihood and Brier score. It is a dependence-aware approximation, not a universal guarantee of independence. Tile-size sensitivity is required; calibration-gap intervals are not currently implemented.

## 10. Sensitivity analyses

Before the test release, use only training/validation outcomes to assess:
- Drought cutoffs of −0.75 and −1.25 SD.
- Fire thresholds at the 85th and 95th percentiles.
- Vegetation cutoffs of −0.25 and −0.75 SD.
- Ecoregion-only versus biome-fallback fire thresholds.
- Alternative QA coverage requirements and NDVI QA decoding.
- Cell-boundary and land-mask handling.
- Smaller/larger spatial blocks for uncertainty.
- Area-weighted versus unweighted regional summaries, with the weighted version remaining primary.

Do not select model settings based on locked-test performance.

## 11. Student prior and locked-test release

Before any 2021–2024 test label, prevalence summary or score is inspected, the student must write a prediction in their own words addressing:
1. Whether M4 is expected to outperform M0 and the individual-indicator models.
2. Whether t+3 performance is expected to be lower, similar or higher than t+1.
3. The reasoning and confidence behind those expectations.

Record it privately in `author_prior_prediction.md`, which is excluded from version control. An AI-generated suggestion is not the author's prior; the author must review and adopt the statement in their own judgement.

After validation review, freeze the exact thresholds, predictors, hyperparameters, code hash and design decisions in analysis_freeze.json. The analysis program requires the prior, a matching code hash, affirmative freeze fields and an unused release marker. Open the test once and preserve its outputs and hashes. Any later changes prompted by test results must be labelled exploratory.

## 12. Limitations and release scope

The selected products are proxies with documented limitations. RESOLVE boundaries are static; a 0.5° cell may contain multiple ecosystems; missingness and uneven observation quality can affect regional comparability. Some ecoregions may not contain sufficient events to support stable estimates. The block-bootstrap interval is an approximation, and the proposed spatial tile size requires sensitivity analysis.

This repository release is a complete software and methodological framework. It does not include extracted global rasters, independently reviewed source exports, empirical prevalence tables or fitted-model results. No empirical performance conclusion, regional finding or operational warning capability is claimed. The distinction is intentional: a finished analysis package is not the same thing as a completed empirical study.

The protocol remains a versioned pre-analysis specification. Product-specific quality rules are documented, but any empirical run must verify the exact decoder, source metadata, spatial aggregation and coverage contract used to produce its input tables. Any change to thresholds, predictors, horizons, split logic or evaluation after feasibility review must be versioned and disclosed. The locked-test release requires a genuine author-authored prior, verified extraction manifest and matching analysis freeze.
