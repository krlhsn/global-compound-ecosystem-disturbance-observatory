# When Ecosystem Disturbances Compound: Looking at Environmental Signals Together

A dry period, an unusually large burned area and a drop in vegetation greenness each describe something different about an ecosystem. Looking at any one of them can be useful, but it may leave out what is happening when several pressures overlap.

That is the question behind **When Ecosystem Disturbances Compound**, my Stanford Probability for AI research project: can drought, burned-area activity and vegetation stress be combined to estimate the probability of compound environmental disturbance across global terrestrial ecosystems? And does that estimate behave differently across ecological regions and forecast lead times?

The project is built around a simple idea: one signal rarely tells the whole story. The challenge is deciding how to measure each signal fairly, how to combine them, and how to test predictions without allowing future information to leak into the model.

## Turning broad ideas into measurable signals

I use three environmental indicators, each based on a different satellite or reanalysis product:

- **Drought (D):** a root-zone soil-moisture proxy from ERA5-Land. The design uses a three-month average and compares it with the same calendar month in a fixed historical reference period.
- **Fire activity (F):** the fraction of valid mapped land that burned in the MCD64A1 product. A month is flagged when its burned-area fraction is unusually high relative to a historical threshold for its ecological region and month of the year.
- **Vegetation stress (V):** an NDVI greenness anomaly from MOD13C2.061, compared with the same grid cell and calendar month in its reference period.

These are proxies, not perfect measurements of drought, wildfire or ecosystem health. Burned area does not by itself identify the cause of a fire, and lower NDVI does not automatically mean an ecosystem is unhealthy. The protocol therefore includes product-specific quality checks and coverage requirements.

## What counts as a compound event?

The event definition is intentionally strict. A cell-month is labelled only when all three indicators can be evaluated. If at least two of the three signals are positive, it is classified as a compound event. If any indicator is unavailable, the month is marked not evaluable rather than quietly treating missing information as a zero.

That distinction may sound small, but it changes the meaning of the dataset. Missing information is not evidence that a disturbance did not happen.

The analysis uses a global half-degree grid and an ecoregion crosswalk. This makes it possible to examine broad spatial patterns while retaining fractional-area weights when summarising results across ecological regions.

## Thinking probabilistically about the future

The project compares five regularised logistic-regression models. They range from a seasonal baseline to models using drought, fire or vegetation history, and finally a combined model containing all three types of signals alongside temperature and precipitation histories.

For each origin month, the predictors can use information from that month and the two months before it. The targets are the outcome in the exact month one month later and the exact month three months later. These are separate forecasting questions; an event occurring at any time during a three-month window is not treated as the same thing as an event in the exact third month.

The time split is also important. Target years 2001–2016 are assigned to training, 2017–2020 to validation, and 2021–2024 to a locked test period. The test is protected from decisions made during model development. Before it can be opened, the project requires a genuine prior prediction written by me, verified source exports and quality checks, and a recorded analysis freeze.

## The part that matters most: what the project does not claim

The repository currently contains the research specification, analysis software, data contract, quality-control rules and explanatory interface. It does **not** contain the extracted global environmental rasters or empirical model results. No global event prevalence, regional ranking or predictive-performance conclusion is being reported.

That boundary is deliberate. A working analysis pipeline is not the same as a completed empirical study. Producing credible results requires the source data to be retrieved, processed and independently checked. Until that happens, presenting numbers or maps as findings would be misleading.

## What I learned while designing the study

This project pushed me to think about the steps that come before a model score. A threshold needs a reference period. A forecast needs a precise information cutoff. A missing observation needs to remain distinguishable from a negative event. A test set needs protection from repeated experimentation.

Those decisions are not as visible as a prediction chart, but they determine what a chart would actually mean. Probability is useful here not because it makes uncertainty disappear, but because it gives the study a way to evaluate uncertain predictions and compare them with simpler baselines.

## Where it goes from here

The next stage is empirical: prepare the source exports, verify product quality and spatial coverage, review the development and validation outputs, and only then complete the prior and freeze required for the held-out test. Any conclusion will need to be reported with its coverage, uncertainty and limitations.

For now, this project is a documented and testable research framework. Its central question remains open. I think that is worth stating clearly: the goal is not to make environmental risk look certain, but to investigate whether combining signals can produce more useful and carefully evaluated probabilities.

---

**Project:** [When Ecosystem Disturbances Compound on GitHub](https://github.com/krlhsn/global-compound-ecosystem-disturbance-observatory)  
**Course context:** Stanford Code in Place Probability for AI, Fall 2026  
**Author:** Kamrul Hassan

**Research status:** The pre-analysis framework and software are implemented. Empirical global data extraction and model evaluation have not yet been completed.
