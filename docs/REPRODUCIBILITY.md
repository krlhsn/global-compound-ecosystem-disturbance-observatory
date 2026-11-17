# Reproducibility checklist

A reproducible empirical run requires more than a CSV and a score table.

## Before running

- Record exact product/collection versions and retrieval dates.
- Record the Earth Engine asset IDs and export task IDs.
- Version the grid geometry, land mask and cell–ecoregion crosswalk.
- Preserve exact QA bit decoding and unit-conversion code.
- Store SHA-256 hashes for source partitions, crosswalk, extraction code and manifest.
- Validate required columns, row continuity, units and area reconciliation.

## During development analysis

- Record Python, NumPy, pandas and scikit-learn versions.
- Record repository commit and analysis script SHA-256.
- Preserve stdout/stderr and generated validation outputs.
- Keep raw inputs immutable.
- Record any exclusions, threshold fallback and changes to the protocol.
- Do not inspect locked-test summaries.

## Before the locked test

- Complete the student's prior prediction personally.
- Review validation output and sensitivity checks.
- Complete the analysis freeze file with exact code hash and decisions.
- Confirm no locked-test marker exists.
- Preserve the frozen analysis script and input manifest.

## After one-time test release

- Preserve all test outputs unchanged.
- Hash the outputs and record release time and code commit.
- Record deviations and any post-test exploratory work separately.
- Do not describe a modified, test-informed model as a new untouched test.
