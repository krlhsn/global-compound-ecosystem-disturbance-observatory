# Data directory

Raw raster files, large intermediate tables and empirical exports are intentionally not committed to this repository.

Expected user-provided inputs:
- cell_monthly.csv — one row per 0.5° cell/month.
- cell_ecoregion_weights.csv — one row per cell/ecoregion intersection.

Use the CSV header templates as a schema reminder only. They contain no records. Keep source files immutable, record checksums and complete an extraction manifest before analysis. See DATA_DICTIONARY.md and gee/EXTRACTION_PLAN.md.
