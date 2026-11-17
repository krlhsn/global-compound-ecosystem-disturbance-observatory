# Google Earth Engine Extraction Plan

This document describes the upstream data-preparation work required before running the Python pilot. It is an extraction plan rather than a claim that global exports have already been produced.

## Why partition the export?

The target grid is global at 0.5°. A multi-decade monthly table can contain tens of millions of cell-month records. A single global export may exceed memory, task or storage limits. Use deterministic partitions such as calendar year × latitude band, and make each partition independently verifiable. Never change spatial resolution or randomly sample cells after seeing validation outcomes without documenting a protocol amendment.

## Required source collections

| Source | Earth Engine collection | Required content |
|---|---|---|
| ERA5-Land | ECMWF/ERA5_LAND/MONTHLY_AGGR | swvl1–3, temperature_2m, total_precipitation_sum |
| MODIS NDVI | MODIS/061/MOD13C2 | NDVI, DetailedQA |
| MODIS burned area | MODIS/061/MCD64A1 | BurnDate, QA |
| Ecoregions | RESOLVE/ECOREGIONS/2017 | ECO_ID, ECO_NAME, BIOME_NAME, REALM |

Check product metadata and band names in the official catalogs before every new extraction version.

## Grid and crosswalk

1. Construct a deterministic global 0.5° cell grid with stable identifiers.
2. Apply a declared terrestrial land mask and compute cell land area.
3. Intersect cell polygons with RESOLVE 2017 terrestrial ecoregions.
4. Calculate intersection land area and each intersection's fraction of its cell land area.
5. Export a separate cell–ecoregion crosswalk.
6. Check fractions sum to 1 within 0.001 and crosswalk land area agrees with the main cell table within 1%.
7. Assign a dominant ecoregion only when it covers at least 50% of cell land area; otherwise store MIXED.

Do not assign an entire mixed cell to one ecoregion in regional summaries.

## ERA5-Land aggregation

- Retrieve monthly means covering October 1980–December 2024.
- Preserve soil-water layer values as volumetric fractions.
- Convert temperature from K to °C.
- Convert monthly precipitation depth from m to mm.
- Aggregate source pixels to 0.5° cell values using area weighting.
- Record valid contributing area and missingness for every variable.

## MOD13C2 NDVI quality

- Confirm NDVI and DetailedQA band definitions in the V061 product guide.
- Apply scale factor 0.0001 after excluding fill values.
- Implement the proposed QA bit rule in RESEARCH_PROTOCOL.md and DATA_DICTIONARY.md.
- Calculate the share of terrestrial contributing area passing QA.
- Export NDVI and its good-area fraction; retain QA counts/fractions for sensitivity checks.
- Do not interpret a missing/low-quality observation as zero vegetation greenness.

## MCD64A1 burned-area quality

- Confirm QA bit meanings against the precise V061 guide.
- Valid full-month land mask requires land, valid data and no shortened mapping period.
- Calculate burned area from BurnDate > 0 under this mask.
- Calculate valid mapped area from all pixels under the same mask, including BurnDate = 0.
- Exclude shortened, invalid, unmapped and water pixels from both totals.
- Export shortened-area share separately for audit.
- Mark June 2001 unavailable for the F indicator.

## Export structure

Recommended layout outside Git:
- partitioned cell_monthly files;
- one cell_ecoregion_weights crosswalk;
- immutable extraction_manifest.json;
- QA summaries and spot-check artifacts;
- SHA-256 checksums for every partition and crosswalk.

The monthly data must retain all grid cell-month rows even when one product has no valid observation. Use explicit null values.

## Completion gate

Before the Python pilot:
- confirm every requested month is represented;
- check grid geometry, coordinates, units and area denominators;
- compare random locations with source imagery and product QA layers;
- inspect missingness by product, month, latitude and biome;
- record asset IDs, collection versions, export tasks and code commit;
- obtain independent review of QA decoding and spatial aggregation.

Only then should the real data be passed to analysis/feasibility_pilot.py.
