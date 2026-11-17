# Contributing

Thank you for your interest in this project.

## Before proposing a change

1. Read RESEARCH_PROTOCOL.md, DATA_DICTIONARY.md and PILOT_GATE.md.
2. Keep the distinction between observed, missing, invalid and not-yet-extracted data explicit.
3. Do not add synthetic values to empirical outputs or screenshots without unmistakable synthetic labelling.
4. Do not inspect or tune against the locked test before the release gate is satisfied.

## Development

Python 3.10+:
~~~bash
python -m pip install -e ".[dev]"
python -m pytest
python -m py_compile analysis/feasibility_pilot.py
~~~

Interface:
~~~bash
npm install
npm run build
~~~

## Scientific changes

Changes to event thresholds, forecast horizons, feature windows, validation splits, weighting, missingness rules or model specifications are methodological changes. Explain the reason, affected files, expected consequences and whether the change was made before or after any test release. Preserve prior outputs and hashes.

## Pull requests

Keep changes focused. Include tests for new behaviour, update documentation and disclose AI-assisted code or writing contributions where relevant. Never commit restricted raw environmental data, credentials or personal information.
