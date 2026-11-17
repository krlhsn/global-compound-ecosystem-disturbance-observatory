# Architecture

## Components

**Research specification**
- RESEARCH_PROTOCOL.md defines the question, D/F/V operational proxies, binary target, exact horizons, model family and chronological split.
- DATA_DICTIONARY.md defines the accepted input schema and upstream QA contract.
- SOURCES.md records the official data products and attribution.

**Data preparation**
- gee/EXTRACTION_PLAN.md defines the source-to-grid workflow.
- Raw raster data and partitioned exports are intentionally kept outside Git.
- The Python entry point expects prepared cell-month and ecoregion-crosswalk CSV files.

**Analysis**
- analysis/feasibility_pilot.py validates input tables.
- It derives D/F/V indicators and compound labels using training-only thresholds where specified.
- It creates exact t+1 and t+3 samples using predictor information no later than origin month t.
- It fits five regularised logistic-regression specifications with preprocessing inside each training pipeline.
- It writes validation scores and, when supplied, fractional-area weighted ecoregion summaries.
- Test outputs are protected by a student prior, a script-hash freeze manifest and one-time marker.

**Interface**
- app/App.jsx and app/app.css are an offline React explainer.
- The interface contains no empirical chart, map or score.
- The UI is served locally by Vite using index.html and src/main.jsx.

## Design principles

1. Missing data must never be silently converted to an absence of disturbance.
2. Target-month information must never enter features for that target.
3. Regional summaries must respect fractional cell–ecoregion intersections.
4. Training-dependent transforms must be fitted only within training data.
5. Software status and empirical evidence status must be shown separately.
6. Locked-test outcomes must not guide the confirmatory specification.
