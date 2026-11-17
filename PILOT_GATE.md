# Development Pilot and Locked-Test Gate

The project separates method development from final evaluation so that 2021-2024 outcomes are not used to make design decisions.

## Gate A - source preparation

Before the analysis script is run, the data owner must:
1. Export the complete monthly cell table and fractional-area ecoregion crosswalk.
2. Complete the retrieval and processing manifest.
3. Verify QA bit decoding against the exact product versions.
4. Check row continuity, grid coverage, units, coverage thresholds and spatial-area reconciliation.
5. Perform independent visual and numeric spot checks against source imagery.

Do not use zero to represent missing or unmapped observations.

## Gate B - development and validation

Run only the default mode:

~~~bash
python analysis/feasibility_pilot.py --input data/cell_monthly.csv --crosswalk data/cell_ecoregion_weights.csv --output pilot_outputs --run-sensitivity
~~~

Review training and validation label availability, event prevalence and category counts, threshold fallback rates, regional sample sizes, all five model specifications at both horizons, log10 likelihood, Brier score, calibration gap, block-bootstrap intervals, tile-size sensitivity, missingness and QA sensitivity.

The validation period is for model and protocol review. If design changes are made, document them and update the protocol version.

## Gate C - author-authored prior and freeze

Before any test summary is read:
1. Create `author_prior_prediction.md` privately and write the prediction in your own words. This personal prior is intentionally not tracked in Git.
2. Review the training and validation outputs.
3. Complete extraction_manifest.json using the actual asset IDs, retrieval records, export checksums and independent QA review.
4. Complete analysis_freeze.template.json as analysis_freeze.json.
5. Record SHA-256 hashes for the exact analysis script, protocol, input table, crosswalk, extraction manifest and author prior.
6. Confirm thresholds, predictors, validation review and the student's prior are frozen.
7. Record the freeze date and author notes.

The script checks every source hash and author freeze field.

## Gate D - one-time test release

Only after Gates A-C, run:

~~~bash
python analysis/feasibility_pilot.py --input data/cell_monthly.csv --crosswalk data/cell_ecoregion_weights.csv --manifest extraction_manifest.json --output pilot_outputs --open-locked-test --prior author_prior_prediction.md --freeze analysis_freeze.json
~~~

The release marker is persistent. Do not delete it or rerun the test. Preserve output files and compute checksums. Any later test-informed analysis must be labelled exploratory, not a fresh confirmatory test.

## Status

The personal prior is supplied as a private local file and is not tracked in this public repository. The analysis software cannot create or impersonate the author's scientific expectation. The held-out release remains unavailable until the source data, independent QA, prior and exact analysis freeze satisfy every programmatic check.
