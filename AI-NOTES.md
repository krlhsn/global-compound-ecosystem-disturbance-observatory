# AI Use and Project Decision Record

This project was developed with AI assistance for research organisation, documentation, software implementation, test design and interface development. The author reviewed and selected the scientific question, environmental indicators, event definition, forecast horizons, split logic and intended interpretation.

## AI-assisted contributions

- Helped organise and refine the research protocol and data dictionary.
- Assisted with Python analysis workflow structure, model pipeline code, validation metrics and locked-test safeguards.
- Assisted with the React explanatory interface, CSS, tests, repository documentation and development workflow files.
- Helped identify official dataset catalogues and source-documentation links.

## Author decisions and responsibilities

The author selected the research direction and the D/F/V indicator framework, compound-event definition, spatial-temporal scope, exact t+1/t+3 horizons, model comparison and chronological split. The author is responsible for reviewing all code, verifying source QA and licences, obtaining and checking real data, documenting any changes, interpreting results and writing the personal prior prediction.

## Data and result integrity

No global environmental raster has been extracted or empirically analysed in this repository. No event prevalence, regional ranking, model performance, confidence interval or scientific finding has been invented or added. Any future synthetic fixture must be labelled synthetic and used only for software tests, never as an empirical result.

AI assistance does not replace source verification, reproducible analysis or domain-expert review.


## Quality-control revision (2026-11-18)

During a product-guide audit, the MOD13C2.061 QA definition was corrected: DetailedQA bits 14-15 encode geospatial contribution quality for this CMG product, while a separate pixel-reliability rank identifies Good Data. The protocol, data dictionary, source register, extraction plan, interface and software were updated to use the product-specific interpretation.

The MCD64A1 unburned-area denominator was also tightened to exclude BurnDate = 0 pixels carrying a non-zero special-condition code in QA bits 5-7. A separate area-fraction field records these excluded cases. The analysis gained a threshold-sensitivity grid and stricter, hash-verified locked-test release checks.

The author remains responsible for verifying the exported QA decoder against actual GEE assets and obtaining independent QA review. No empirical result was generated during this code revision.
