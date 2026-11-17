# Sources, Product Metadata and Attribution

This is the planned source register. Record actual retrieval dates, immutable asset identifiers, export parameters, QA code hashes and output checksums after extraction. The scientific target window remains fixed at May 2001–December 2024 regardless of current product availability.

## 1. RESOLVE Ecoregions 2017

- Earth Engine asset: RESOLVE/ECOREGIONS/2017
- Provider: RESOLVE Biodiversity and Wildlife Solutions
- Catalog: https://developers.google.com/earth-engine/datasets/catalog/RESOLVE_ECOREGIONS_2017
- Coverage: 846 terrestrial ecoregions grouped into 14 biomes and 8 realms.
- Fields: ECO_ID, ECO_NAME, BIOME_NAME, REALM.
- Licence: CC BY 4.0; preserve attribution and the source citation.
- Citation: Dinerstein, E. et al. (2017). An Ecoregion-Based Approach to Protecting Half the Terrestrial Realm. BioScience, 67(6), 534–545. https://doi.org/10.1093/biosci/bix014

## 2. ERA5-Land monthly aggregated data

- Earth Engine collection: ECMWF/ERA5_LAND/MONTHLY_AGGR
- Catalog: https://developers.google.com/earth-engine/datasets/catalog/ECMWF_ERA5_LAND_MONTHLY_AGGR
- Copernicus Climate Data Store: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-land-monthly-means
- Variables: volumetric_soil_water_layer_1, _2, _3; temperature_2m; total_precipitation_sum.
- Units: soil water is volumetric fraction; temperature is K; precipitation is accumulated depth in m in the Earth Engine aggregate. Convert temperature to °C and precipitation to mm.
- Citation: Muñoz-Sabater, J. et al. (2021). ERA5-Land: a state-of-the-art global reanalysis dataset for land applications. Earth System Science Data, 13, 4349–4383. https://doi.org/10.5194/essd-13-4349-2021
- Attribution: acknowledge Copernicus Climate Change Service / ECMWF under the current dataset terms. Verify current licence and acknowledgement wording at retrieval time.

## 3. MODIS/Terra MOD13C2.061

- Product: MODIS/Terra Vegetation Indices Monthly L3 Global 0.05° CMG V061.
- DOI: https://doi.org/10.5067/MODIS/MOD13C2.061
- Collection guide: https://lpdaac.usgs.gov/documents/621/MOD13_User_Guide_V61.pdf
- Scale: NDVI scale factor 0.0001. Confirm valid range and fill values from the V061 guide.
- QA: DetailedQA contains VI Quality, VI Usefulness, land/water, snow/ice and shadow fields. The proposed bit filter is documented in RESEARCH_PROTOCOL.md and DATA_DICTIONARY.md and must be verified against V061 metadata before export.
- Attribution: retain NASA LP DAAC / MODIS product acknowledgement and citation in derivative work.

## 4. MODIS/Terra+Aqua MCD64A1.061

- Product: MODIS/Terra+Aqua Burned Area Monthly Global 500 m V061.
- Earth Engine catalog: https://developers.google.com/earth-engine/datasets/catalog/MODIS_061_MCD64A1
- User guide: https://lpdaac.usgs.gov/documents/1006/MCD64_User_Guide_V61.pdf
- DOI: https://doi.org/10.5067/MODIS/MCD64A1.061
- QA: bit 0 = land; bit 1 = valid data; bit 2 = shortened mapping period. Verify this against the actual product guide version used.
- Known limitations: small burned areas may be omitted; cropland burning has lower confidence; June 2001 is heavily degraded in the product documentation.
- Use terms: the Earth Engine catalog states MODIS products acquired through LP DAAC have no restrictions on subsequent use, sale or redistribution; retain citation and attribution.

## Retrieval and processing record

The source rasters have not yet been exported into this repository. Complete this record after actual extraction:

- Earth Engine project/account:
- Retrieval date for each source:
- Exact collection/product IDs and temporal filter:
- MOD13C2 QA decoding implementation and code hash:
- MCD64A1 QA decoding implementation and code hash:
- Grid asset ID and geometry hash:
- Cell–ecoregion crosswalk ID/hash:
- ERA5-Land unit conversion and aggregation code hash:
- Export task IDs and output checksums:
- Source licence/attribution text checked:
- Independent QA review and sign-off:
