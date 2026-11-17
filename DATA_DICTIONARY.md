# Data Dictionary and Extraction Contract

## Observation and time coverage

- Main observation: one 0.5° grid cell × calendar month.
- Target dates: May 2001–December 2024.
- Input history: October 1980–December 2024.
- Every cell/month row must be retained, even when an upstream product is unavailable. Encode unavailable values as NA, never as zero.
- Store source version, asset ID, projection, export date, QA implementation, processing-code hash and checksums in the extraction manifest.

## Required monthly table: cell_monthly.csv

| Column | Type / unit | Definition |
|---|---|---|
| grid_id | string | Stable identifier for a 0.5° cell |
| date | YYYY-MM-01 | Calendar month represented |
| latitude, longitude | degrees | Grid-cell centre |
| land_area_km2 | km² | Terrestrial area represented by the cell under the declared land mask |
| ecoregion_id | string | Dominant ecoregion only when it covers at least 50% of cell land area; otherwise MIXED |
| ecoregion_name | string | Dominant name or Mixed boundary cell |
| biome_name | string | Dominant biome context; mixed-cell rule must be documented |
| realm | string | Dominant realm context; mixed-cell rule must be documented |
| ecoregion_fraction | 0–1 | Dominant ecoregion land-area share; descriptive only |
| swvl1, swvl2, swvl3 | m³/m³ | Area-weighted volumetric soil water for 0–7, 7–28 and 28–100 cm |
| t2m_c | °C | Area-weighted monthly mean 2 m air temperature |
| precip_mm | mm | Area-weighted monthly accumulated precipitation depth |
| ndvi | unitless | Area-weighted NDVI after 0.0001 scale factor and QA filter |
| ndvi_good_fraction | 0–1 | Terrestrial contributing-area share passing NDVI QA |
| burned_area_km2 | km² | Burned pixel area under the full-month valid land mask |
| valid_land_area_km2 | km² | Denominator area: burned valid land plus reliably unburned land (BurnDate = 0 and QA special-condition bits 5–7 = 0) |
| fire_shortened_fraction | 0–1 | Terrestrial area share flagged as shortened; retained for audit |
| fire_unburned_special_fraction | 0–1 | Terrestrial area share classified unburned with a non-zero MCD64A1 special-condition code; excluded from the burned-fraction denominator |

## Required ecoregion crosswalk

File: cell_ecoregion_weights.csv

One row per grid_id × ecoregion_id, with:
- grid_id
- ecoregion_id
- ecoregion_name
- biome_name
- realm
- intersection_land_area_km2
- area_fraction_of_cell_land

The fractions for each grid cell must sum to 1 within 0.001. The intersection areas must reconcile with the cell's terrestrial land area within 1%. Use this crosswalk only for regional summaries; do not duplicate cell-month rows for model fitting.

## Upstream processing contract

### ERA5-Land

Use Earth Engine collection ECMWF/ERA5_LAND/MONTHLY_AGGR or the corresponding Copernicus product with an immutable retrieval record. Aggregate to the 0.5° grid using area weighting. Convert temperature_2m from K to °C. Convert total_precipitation_sum from m to mm. Soil-water layers are volumetric fractions. Verify exact band names and units for the retrieved collection.

### MOD13C2.061 NDVI

Retrieve the primary MOD13C2.061 monthly CMG product through NASA LP DAAC / USGS Earthdata. The current reviewed Earth Engine MODIS catalogue did not confirm a MOD13C2.061 collection ID; do not assume MODIS/061/MOD13C2 exists in Earth Engine. Keep the source granule IDs and checksums in the extraction manifest.

- Apply NDVI scale factor 0.0001 and handle fill values before aggregation.
- Require the product-specific pixel reliability rank (SummaryQA / pixel reliability) = 0 (Good Data).
- DetailedQA rules: bits 0–1 = 00 (good VI quality); bits 2–5 ≤ 0001 (highest or lower usefulness rank); bits 11–13 = 001 (land); bits 14–15 ≥ 10 (more than 50% of the finer 1-km resolution contributed to the CMG pixel).
- Important: for MOD13C2, bits 14–15 are geospatial contribution quality, not snow/ice and shadow flags. The product also has a separate pixel-reliability rank.
- Calculate good fraction from contributing terrestrial CMG pixel area, not the count of pixels alone.
- Require ndvi_good_fraction ≥0.80 for the primary V indicator.
- Verify V061 SDS names and bit decoding against the product guide; record exact decoder code and granule-level provenance in the manifest.

### MCD64A1.061 burned area

- Valid full-month terrestrial pixel mask: QA bit 0 = land, bit 1 = valid observation, bit 2 = mapping period not shortened.
- Burned numerator: pixel area where BurnDate > 0 under this mask.
- Valid denominator: pixel area of every pixel under this same mask, including BurnDate = 0.
- Exclude water, invalid, unmapped and shortened-period pixels from numerator and denominator.
- Require valid_land_area_km2 / land_area_km2 ≥0.80.
- Do not treat shortened/unmapped pixels as unburned.
- F is unavailable in June 2001 because of documented product degradation.

## Derived fields

| Field | Rule |
|---|---|
| rootzone_sm | 0.07×swvl1 + 0.21×swvl2 + 0.72×swvl3 |
| rootzone_sm_3m | Three-month rolling mean ending in the current month |
| soil_moisture_z | Same-cell/calendar-month z-score against 1981–2000; minimum 15 values |
| D | 1 if soil_moisture_z ≤−1.0; else 0 when valid |
| ndvi_z | Same-cell/calendar-month z-score against 2001–2016; minimum 12 values |
| V | 1 if ndvi_z ≤−0.5; else 0 when valid |
| burned_fraction | burned_area_km2 / valid_land_area_km2 |
| fire_threshold | 90th percentile of positive training-period burned fractions by ecoregion × month; biome × month fallback if fewer than 30 positives |
| F | 1 if valid positive burned fraction ≥ threshold; else 0 when valid |
| event_count | D + F + V when all three exist |
| event_category | DF, DV, FV, DFV, NONE, or NOT_EVALUABLE |
| Y | 1 when event_count ≥2; otherwise 0, only when all indicators exist |

## Forecast features and sample construction

For each cell and origin month t, predictors include only t, t−1 and t−2. Target labels are shifted by exactly one or three calendar rows within each continuous grid-cell series. Samples are included only when their target month lies between May 2001 and December 2024. Split membership follows target year.

## Validation checks

Before analysis:
- no duplicate grid_id/date pairs;
- continuous monthly rows per grid_id;
- valid latitude/longitude bounds;
- non-negative area fields and burned_area ≤ valid_land_area;
- fractions between 0 and 1;
- one valid crosswalk mapping per cell/ecoregion pair;
- area fractions sum to 1;
- crosswalk area reconciles to cell terrestrial area;
- extraction manifest and source QA checks are complete.

Do not infer or impute missing observations as no disturbance. Any additional imputation belongs inside the model pipeline and must be fitted using training data only.
