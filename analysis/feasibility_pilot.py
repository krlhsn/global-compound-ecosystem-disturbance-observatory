#!/usr/bin/env python3
"""Development-only analysis for compound ecosystem disturbance.

Input is a prepared real 0.5-degree cell/month CSV. This program does not
download or fabricate environmental data. By default it writes training and
validation outputs only. The 2021-2024 test requires a student-authored prior,
a completed freeze manifest matching this exact file hash, and an explicit
--open-locked-test flag.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Iterable
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

PROTOCOL_VERSION = "1.0-draft"
TRAIN_START, TRAIN_END = 2001, 2016
VALID_START, VALID_END = 2017, 2020
TEST_START, TEST_END = 2021, 2024
TARGET_START = pd.Timestamp("2001-05-01")
TARGET_END = pd.Timestamp("2024-12-01")
REQUIRED = {
    "grid_id", "date", "latitude", "longitude", "land_area_km2",
    "ecoregion_id", "ecoregion_name", "biome_name", "realm",
    "ecoregion_fraction", "swvl1", "swvl2", "swvl3", "t2m_c",
    "precip_mm", "ndvi", "ndvi_good_fraction", "burned_area_km2",
    "valid_land_area_km2", "fire_shortened_fraction",
}
BASE_CATEGORICAL = ["biome_name", "target_month"]
MODEL_INPUTS = {
    "M0_baseline": [],
    "M1_drought": ["soil_moisture_z", "D"],
    "M2_fire_history": ["burned_fraction", "F"],
    "M3_vegetation": ["ndvi_z", "V"],
    "M4_combined": ["soil_moisture_z", "D", "burned_fraction", "F", "ndvi_z", "V", "t2m_c", "precip_mm"],
}

def require_columns(frame: pd.DataFrame, required: set[str]) -> None:
    missing = sorted(required - set(frame.columns))
    if missing:
        raise ValueError("Missing required columns: " + ", ".join(missing))

def validate_monthly_input(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate identifiers, basic bounds, uniqueness and monthly continuity."""
    require_columns(frame, REQUIRED)
    data = frame.copy()
    data["date"] = pd.to_datetime(data["date"], errors="raise").dt.to_period("M").dt.to_timestamp()
    if data["grid_id"].isna().any() or data["date"].isna().any():
        raise ValueError("grid_id and date cannot be missing.")
    if data.duplicated(["grid_id", "date"]).any():
        raise ValueError("Duplicate grid_id/date rows found.")
    if ((data["latitude"].dropna() < -90) | (data["latitude"].dropna() > 90)).any():
        raise ValueError("Latitude must be between -90 and 90.")
    if ((data["longitude"].dropna() < -180) | (data["longitude"].dropna() > 180)).any():
        raise ValueError("Longitude must be between -180 and 180.")
    for col in ["land_area_km2", "valid_land_area_km2", "burned_area_km2"]:
        if (data[col].dropna() < 0).any():
            raise ValueError(f"{col} contains negative values.")
    for col in ["ndvi_good_fraction", "fire_shortened_fraction", "ecoregion_fraction"]:
        values = data[col].dropna()
        if ((values < 0) | (values > 1)).any():
            raise ValueError(f"{col} must be between 0 and 1.")
    if (data["valid_land_area_km2"] - data["land_area_km2"] > 1e-4).any():
        raise ValueError("valid_land_area_km2 cannot exceed land_area_km2.")
    if (data["burned_area_km2"] - data["valid_land_area_km2"] > 0.05).any():
        raise ValueError("Burned area exceeds valid mapped land area.")
    for grid_id, group in data.groupby("grid_id", sort=False):
        dates = group["date"].sort_values().reset_index(drop=True)
        expected = pd.date_range(dates.iloc[0], dates.iloc[-1], freq="MS")
        if len(expected) != len(dates) or not np.array_equal(expected.values, dates.values):
            raise ValueError(f"Missing monthly row(s) for grid_id={grid_id}; retain rows and encode unavailable observations as NA.")
    return data.sort_values(["grid_id", "date"]).reset_index(drop=True)

def validate_crosswalk(crosswalk: pd.DataFrame, grid_ids: Iterable[str] | None = None) -> pd.DataFrame:
    required = {"grid_id", "ecoregion_id", "ecoregion_name", "biome_name", "realm",
                "intersection_land_area_km2", "area_fraction_of_cell_land"}
    require_columns(crosswalk, required)
    table = crosswalk.copy()
    if table.duplicated(["grid_id", "ecoregion_id"]).any():
        raise ValueError("Crosswalk contains duplicate grid_id/ecoregion_id pairs.")
    if (table["intersection_land_area_km2"].dropna() < 0).any():
        raise ValueError("Crosswalk intersection areas cannot be negative.")
    fractions = table["area_fraction_of_cell_land"].dropna()
    if ((fractions < 0) | (fractions > 1)).any():
        raise ValueError("Crosswalk fractions must be between 0 and 1.")
    sums = table.groupby("grid_id")["area_fraction_of_cell_land"].sum()
    if ((sums - 1.0).abs() > 1e-3).any():
        raise ValueError("Crosswalk area fractions must sum to 1 for every grid cell.")
    if grid_ids is not None:
        missing = set(grid_ids) - set(table["grid_id"])
        if missing:
            raise ValueError(f"Crosswalk omits {len(missing):,} grid cells.")
    return table

def reference_zscore(frame: pd.DataFrame, reference: pd.DataFrame,
                     groups: list[str], value: str, min_n: int) -> pd.Series:
    stats = (reference.groupby(groups, dropna=False)[value]
             .agg(ref_mean="mean", ref_sd="std", ref_n="count").reset_index())
    merged = frame[groups + [value]].merge(stats, on=groups, how="left", sort=False)
    valid = (merged["ref_n"] >= min_n) & merged["ref_sd"].notna() & (merged["ref_sd"] > 0)
    z = ((merged[value] - merged["ref_mean"]) / merged["ref_sd"]).where(valid)
    return pd.Series(z.to_numpy(), index=frame.index, dtype="float64")

def compound_labels(drought: pd.Series, fire: pd.Series, vegetation: pd.Series) -> tuple[pd.Series, pd.Series]:
    """Return binary Y and category; unevaluable indicator combinations stay NA."""
    values = pd.DataFrame({"D": drought, "F": fire, "V": vegetation})
    eligible = values.notna().all(axis=1)
    count = values.sum(axis=1, min_count=3)
    y = pd.Series(np.nan, index=values.index, dtype="float64")
    y.loc[eligible] = (count.loc[eligible] >= 2).astype(float)
    labels = pd.Series("NOT_EVALUABLE", index=values.index, dtype="object")
    labels.loc[eligible] = "NONE"
    conditions = {
        "DF": (values.D == 1) & (values.F == 1) & (values.V == 0),
        "DV": (values.D == 1) & (values.F == 0) & (values.V == 1),
        "FV": (values.D == 0) & (values.F == 1) & (values.V == 1),
        "DFV": (values.D == 1) & (values.F == 1) & (values.V == 1),
    }
    for code, condition in conditions.items():
        labels.loc[eligible & condition] = code
    return y, labels

def build_indicators(frame: pd.DataFrame) -> pd.DataFrame:
    data = frame.sort_values(["grid_id", "date"]).reset_index(drop=True).copy()
    data["month"], data["year"] = data["date"].dt.month, data["date"].dt.year
    data["rootzone_sm"] = 0.07*data["swvl1"] + 0.21*data["swvl2"] + 0.72*data["swvl3"]
    data["rootzone_sm_3m"] = data.groupby("grid_id", sort=False)["rootzone_sm"].transform(
        lambda values: values.rolling(3, min_periods=3).mean())
    soil_reference = data[data["date"].between("1981-01-01", "2000-12-01")]
    if soil_reference.empty:
        raise ValueError("Input must include 1981-2000 ERA5-Land data for the fixed soil-moisture reference.")
    data["soil_moisture_z"] = reference_zscore(data, soil_reference, ["grid_id", "month"], "rootzone_sm_3m", 15)
    data["D"] = np.where(data["soil_moisture_z"].notna(), (data["soil_moisture_z"] <= -1.0).astype(float), np.nan)

    # NDVI is assumed scaled and quality-decoded upstream; its good-area fraction is checked here.
    ndvi_good = data["ndvi"].notna() & (data["ndvi_good_fraction"] >= 0.80)
    data.loc[~ndvi_good, "ndvi"] = np.nan
    ndvi_reference = data[data["year"].between(TRAIN_START, TRAIN_END)]
    data["ndvi_z"] = reference_zscore(data, ndvi_reference, ["grid_id", "month"], "ndvi", 12)
    data["V"] = np.where(data["ndvi_z"].notna(), (data["ndvi_z"] <= -0.5).astype(float), np.nan)

    # Burned numerator and denominator must use the identical full-month valid land mask.
    coverage = data["valid_land_area_km2"] / data["land_area_km2"].replace(0, np.nan)
    data["burned_fraction"] = data["burned_area_km2"] / data["valid_land_area_km2"].replace(0, np.nan)
    data.loc[coverage < 0.80, "burned_fraction"] = np.nan
    fire_reference = data[data["year"].between(TRAIN_START, TRAIN_END)].copy()
    fire_reference = fire_reference[~((fire_reference["year"] == 2001) & (fire_reference["month"] == 6))]
    positive = fire_reference[fire_reference["burned_fraction"] > 0].copy()
    positive = positive[positive["burned_fraction"].notna()]
    eco = positive[positive["ecoregion_id"].notna() &
                   (positive["ecoregion_id"].astype(str).str.upper() != "MIXED")]
    eco_stats = eco.groupby(["ecoregion_id", "month"])["burned_fraction"].agg(
        eco_threshold=lambda s: s.quantile(0.90), eco_n="count").reset_index()
    biome_stats = positive.groupby(["biome_name", "month"])["burned_fraction"].agg(
        biome_threshold=lambda s: s.quantile(0.90), biome_n="count").reset_index()
    data = data.merge(eco_stats, on=["ecoregion_id", "month"], how="left", validate="many_to_one")
    data = data.merge(biome_stats, on=["biome_name", "month"], how="left", validate="many_to_one")
    use_eco = data["eco_n"].fillna(0) >= 30
    use_biome = (~use_eco) & (data["biome_n"].fillna(0) >= 30)
    data["fire_threshold"] = np.select([use_eco, use_biome],
                                       [data["eco_threshold"], data["biome_threshold"]], default=np.nan)
    data["fire_threshold_level"] = np.select([use_eco, use_biome],
                                             ["ecoregion", "biome"], default="unavailable")
    fire_ok = data["burned_fraction"].notna() & data["fire_threshold"].notna()
    data["F"] = np.where(fire_ok,
                         ((data["burned_fraction"] > 0) & (data["burned_fraction"] >= data["fire_threshold"])).astype(float),
                         np.nan)
    data.loc[(data["year"] == 2001) & (data["month"] == 6), "F"] = np.nan
    data["Y"], data["event_category"] = compound_labels(data["D"], data["F"], data["V"])
    data["event_count"] = data[["D", "F", "V"]].sum(axis=1, min_count=3)
    return data

def add_lags(frame: pd.DataFrame, columns: Iterable[str], max_lag: int = 2) -> pd.DataFrame:
    data = frame.sort_values(["grid_id", "date"]).copy()
    grouped = data.groupby("grid_id", sort=False)
    for column in columns:
        for lag in range(max_lag + 1):
            data[f"{column}_lag{lag}"] = grouped[column].shift(lag)
    return data

def make_forecast_samples(frame: pd.DataFrame, horizon: int) -> pd.DataFrame:
    """Predict the outcome in exactly t+h using predictors observed no later than t."""
    if horizon not in (1, 3):
        raise ValueError("Only exact t+1 and t+3 forecast horizons are preregistered.")
    data = frame.sort_values(["grid_id", "date"]).copy()
    grouped = data.groupby("grid_id", sort=False)
    data["target_date"] = grouped["date"].shift(-horizon)
    data["target_Y"] = grouped["Y"].shift(-horizon)
    data["target_category"] = grouped["event_category"].shift(-horizon)
    data = data[data["target_date"].between(TARGET_START, TARGET_END)].copy()
    data["target_month"] = data["target_date"].dt.month.astype(str)
    data["target_year"] = data["target_date"].dt.year
    data["horizon"] = horizon
    return data

def calibration_gap(y: np.ndarray, probability: np.ndarray, bins: int = 10,
                    weights: np.ndarray | None = None) -> float:
    if len(y) == 0:
        return float("nan")
    weights = np.ones(len(y), dtype=float) if weights is None else np.asarray(weights, dtype=float)
    order = np.argsort(probability)
    y, probability, weights = y[order], probability[order], weights[order]
    groups = np.minimum((np.arange(len(y))*bins)//max(len(y), 1), bins-1)
    total, gap = weights.sum(), 0.0
    if total <= 0:
        return float("nan")
    for index in np.unique(groups):
        mask = groups == index
        w = weights[mask]
        if w.sum():
            gap += (w.sum()/total)*abs(np.average(y[mask], weights=w)-np.average(probability[mask], weights=w))
    return float(gap)

def block_bootstrap(y: np.ndarray, probability: np.ndarray, latitude: np.ndarray,
                    longitude: np.ndarray, year: np.ndarray, reps: int = 200,
                    seed: int = 109, tile_degrees: float = 5.0) -> dict[str, float]:
    """Percentile intervals from spatial-tile x target-year blocks; a dependence-aware approximation."""
    if len(y) == 0:
        return {}
    lat = np.floor((latitude+90)/tile_degrees).astype(int)
    lon = np.floor((longitude+180)/tile_degrees).astype(int)
    labels = np.array([f"{a}:{b}:{c}" for a, b, c in zip(lat, lon, year)])
    _, inverse = np.unique(labels, return_inverse=True)
    n_blocks = int(inverse.max())+1 if len(inverse) else 0
    if n_blocks < 10:
        return {"log10_ll_ci_low": np.nan, "log10_ll_ci_high": np.nan,
                "brier_ci_low": np.nan, "brier_ci_high": np.nan}
    p = np.clip(probability, 1e-15, 1-1e-15)
    ll = y*np.log10(p) + (1-y)*np.log10(1-p)
    brier = (y-p)**2
    rng = np.random.default_rng(seed)
    ll_stats, brier_stats = [], []
    for _ in range(reps):
        sampled = rng.integers(0, n_blocks, size=n_blocks)
        multiplicity = np.bincount(sampled, minlength=n_blocks)
        weights = multiplicity[inverse]
        total = weights.sum()
        if total:
            ll_stats.append(np.sum(weights*ll)/total)
            brier_stats.append(np.sum(weights*brier)/total)
    return {
        "log10_ll_ci_low": float(np.percentile(ll_stats, 2.5)),
        "log10_ll_ci_high": float(np.percentile(ll_stats, 97.5)),
        "brier_ci_low": float(np.percentile(brier_stats, 2.5)),
        "brier_ci_high": float(np.percentile(brier_stats, 97.5)),
    }

def make_pipeline(numeric: list[str]) -> Pipeline:
    categorical = Pipeline([("impute", SimpleImputer(strategy="most_frequent")),
                            ("encode", OneHotEncoder(handle_unknown="ignore"))])
    pieces = [("context", categorical, BASE_CATEGORICAL)]
    if numeric:
        numeric_pipe = Pipeline([("impute", SimpleImputer(strategy="median", add_indicator=True)),
                                 ("scale", StandardScaler())])
        pieces.append(("numeric", numeric_pipe, numeric))
    preprocess = ColumnTransformer(pieces, remainder="drop")
    return Pipeline([("preprocess", preprocess),
                     ("model", LogisticRegression(C=1.0, solver="lbfgs", max_iter=1000))])

def regional_scores(evaluate: pd.DataFrame, y: np.ndarray, p: np.ndarray,
                    crosswalk: pd.DataFrame, model_name: str, horizon: int) -> list[dict]:
    mapped = evaluate[["grid_id"]].copy()
    mapped["y"], mapped["p"] = y, p
    mapped = mapped.merge(crosswalk, on="grid_id", how="left", validate="many_to_many")
    mapped = mapped.dropna(subset=["ecoregion_id", "intersection_land_area_km2"])
    mapped["ll"] = mapped.y*np.log10(np.clip(mapped.p, 1e-15, 1-1e-15)) + (
        1-mapped.y)*np.log10(np.clip(1-mapped.p, 1e-15, 1-1e-15))
    mapped["brier"] = (mapped.y-mapped.p)**2
    rows = []
    for eco_id, group in mapped.groupby("ecoregion_id"):
        weights = group["intersection_land_area_km2"].to_numpy(float)
        positives, negatives = int((group.y == 1).sum()), int((group.y == 0).sum())
        enough = positives >= 30 and negatives >= 30 and weights.sum() > 0
        rows.append({
            "horizon": horizon, "model": model_name, "ecoregion_id": eco_id,
            "ecoregion_name": group.ecoregion_name.iloc[0], "biome_name": group.biome_name.iloc[0],
            "realm": group.realm.iloc[0], "n_grid_cells": int(group.grid_id.nunique()),
            "n_cell_months": len(group), "n_positive": positives, "n_negative": negatives,
            "area_weighted_event_rate": float(np.average(group.y, weights=weights)) if weights.sum() else np.nan,
            "weighted_mean_log10_likelihood": float(np.average(group.ll, weights=weights)) if enough else np.nan,
            "weighted_brier_score": float(np.average(group.brier, weights=weights)) if enough else np.nan,
            "weighted_calibration_gap": calibration_gap(group.y.to_numpy(), group.p.to_numpy(), weights=weights) if enough else np.nan,
            "status": "scored" if enough else "insufficient events/non-events (30 each required)",
        })
    return rows

def score_models(train: pd.DataFrame, evaluate: pd.DataFrame, horizon: int,
                 crosswalk: pd.DataFrame | None = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    rows, regions = [], []
    train = train[train.target_Y.notna() & train.target_year.between(TRAIN_START, TRAIN_END)]
    evaluate = evaluate[evaluate.target_Y.notna()]
    for name, base_features in MODEL_INPUTS.items():
        numeric = [f"{feature}_lag{lag}" for feature in base_features for lag in range(3)]
        columns = BASE_CATEGORICAL + numeric
        if train.empty or evaluate.empty or train.target_Y.nunique() < 2 or evaluate.target_Y.nunique() < 2:
            rows.append({"horizon": horizon, "model": name, "n_train": len(train),
                         "n_evaluate": len(evaluate), "status": "not_scored: insufficient data or classes"})
            continue
        pipeline = make_pipeline(numeric)
        pipeline.fit(train[columns], train.target_Y.astype(int))
        p = np.clip(pipeline.predict_proba(evaluate[columns])[:, 1], 1e-15, 1-1e-15)
        y = evaluate.target_Y.astype(int).to_numpy()
        ll = y*np.log10(p)+(1-y)*np.log10(1-p)
        intervals = block_bootstrap(y, p, evaluate.latitude.to_numpy(),
                                    evaluate.longitude.to_numpy(), evaluate.target_year.to_numpy())
        rows.append({
            "horizon": horizon, "model": name, "n_train": len(train), "n_evaluate": len(evaluate),
            "event_rate": float(y.mean()), "mean_log10_likelihood": float(ll.mean()),
            "total_log10_likelihood": float(ll.sum()), "brier_score": float(brier_score_loss(y, p)),
            "calibration_gap": calibration_gap(y, p), **intervals, "status": "scored",
        })
        if crosswalk is not None:
            regions.extend(regional_scores(evaluate, y, p, crosswalk, name, horizon))
    return pd.DataFrame(rows), pd.DataFrame(regions)

def write_development_outputs(frame: pd.DataFrame, output: Path,
                              crosswalk: pd.DataFrame | None = None) -> None:
    output.mkdir(parents=True, exist_ok=True)
    score_tables, regional_tables, counts, validity = [], [], [], []
    for horizon in (1, 3):
        samples = make_forecast_samples(frame, horizon)
        train = samples[samples.target_year.between(TRAIN_START, TRAIN_END)]
        validation = samples[samples.target_year.between(VALID_START, VALID_END)]
        score, region = score_models(train, validation, horizon, crosswalk)
        score_tables.append(score)
        if not region.empty:
            regional_tables.append(region)
        for period, subset in [("training", train), ("validation", validation)]:
            valid = subset.target_Y.notna()
            categories = subset.loc[valid, "target_category"].value_counts()
            counts.append({
                "horizon": horizon, "period": period, "n_samples": len(subset),
                "n_evaluable": int(valid.sum()),
                "event_rate": float(subset.loc[valid, "target_Y"].mean()) if valid.any() else np.nan,
                **{f"category_{key}": int(categories.get(key, 0)) for key in ["NONE", "DF", "DV", "FV", "DFV"]},
                "not_evaluable": int((~valid).sum()),
            })
            validity.append({"horizon": horizon, "period": period, "n": len(subset),
                             "evaluable": int(valid.sum())})
    pd.concat(score_tables, ignore_index=True).to_csv(output/"validation_model_scores.csv", index=False)
    pd.DataFrame(counts).to_csv(output/"development_event_counts.csv", index=False)
    pd.DataFrame(validity).to_csv(output/"development_validity.csv", index=False)
    if regional_tables:
        pd.concat(regional_tables, ignore_index=True).to_csv(output/"validation_ecoregion_scores.csv", index=False)
    fallback = frame.groupby(["fire_threshold_level", "month"], dropna=False).size().rename("cell_months").reset_index()
    fallback.to_csv(output/"fire_threshold_fallback_counts.csv", index=False)
    lines = [
        "# Development and validation report", "",
        "Generated from the supplied input table. Verify the extraction manifest before interpretation.",
        "The locked 2021-2024 test is not included.", "",
        f"- Input rows: {len(frame):,}", f"- Grid cells: {frame.grid_id.nunique():,}",
        f"- Input range: {frame.date.min().date()} to {frame.date.max().date()}", "",
        "## Output files",
        "- development_event_counts.csv: category counts and evaluability by horizon.",
        "- development_validity.csv: forecast sample coverage.",
        "- fire_threshold_fallback_counts.csv: fire-threshold level counts.",
        "- validation_model_scores.csv: validation metrics for M0-M4.",
        "- validation_ecoregion_scores.csv: area-weighted regional metrics when a crosswalk is supplied.", "",
        "## Guardrails",
        "- These results do not establish operational warning capability.",
        "- Interpret metrics with sample sizes, data coverage and extraction QA.",
        "- Regions with fewer than 30 events or non-events are not scored.",
        "- The block bootstrap is an approximation; test tile-size sensitivity.",
        "- Do not open the locked test before the student prior and freeze are complete.",
    ]
    (output/"pilot_report.md").write_text("\n".join(lines)+"\n", encoding="utf-8")

def open_locked_test(frame: pd.DataFrame, output: Path, prior: Path, freeze: Path,
                     marker: Path, crosswalk: pd.DataFrame | None) -> None:
    if not prior.is_file() or not freeze.is_file():
        raise ValueError("Locked test blocked: supply the student's prior and completed freeze manifest.")
    prior_text = prior.read_text(encoding="utf-8").strip()
    placeholders = ["[write", "[your", "not yet completed", "intentionally left unfilled", "complete before opening"]
    if len(prior_text) < 120 or any(item in prior_text.lower() for item in placeholders):
        raise ValueError("Locked test blocked: prior prediction appears incomplete or template-only.")
    manifest = json.loads(freeze.read_text(encoding="utf-8"))
    digest = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    required = {"protocol_version", "analysis_code_sha256", "thresholds_frozen", "predictors_frozen",
                "validation_reviewed", "student_prior_completed", "freeze_date", "student_notes"}
    missing = required - set(manifest)
    if missing or manifest.get("protocol_version") != PROTOCOL_VERSION:
        raise ValueError(f"Freeze manifest incomplete or version mismatch: {sorted(missing)}.")
    if manifest.get("analysis_code_sha256") != digest:
        raise ValueError("Freeze manifest hash does not match this exact analysis script.")
    confirmations = ["thresholds_frozen", "predictors_frozen", "validation_reviewed", "student_prior_completed"]
    if not all(manifest.get(key) is True for key in confirmations):
        raise ValueError("All freeze confirmations must be true.")
    if not str(manifest.get("freeze_date", "")).strip() or not str(manifest.get("student_notes", "")).strip():
        raise ValueError("Freeze date and student notes must be completed.")
    if marker.exists() or (output/"LOCKED_TEST_OPENED.txt").exists():
        raise FileExistsError("Locked test already opened; refusing a repeat run.")

    scores, regional = [], []
    for horizon in (1, 3):
        samples = make_forecast_samples(frame, horizon)
        development = samples[samples.target_year.between(TRAIN_START, VALID_END)]
        test = samples[samples.target_year.between(TEST_START, TEST_END)]
        for name, base_features in MODEL_INPUTS.items():
            numeric = [f"{feature}_lag{lag}" for feature in base_features for lag in range(3)]
            columns = BASE_CATEGORICAL + numeric
            train = development[development.target_Y.notna()]
            evaluate = test[test.target_Y.notna()]
            if train.empty or evaluate.empty or train.target_Y.nunique() < 2 or evaluate.target_Y.nunique() < 2:
                scores.append({"horizon": horizon, "model": name, "status": "not_scored: insufficient data/classes"})
                continue
            pipeline = make_pipeline(numeric)
            pipeline.fit(train[columns], train.target_Y.astype(int))
            p = np.clip(pipeline.predict_proba(evaluate[columns])[:, 1], 1e-15, 1-1e-15)
            y = evaluate.target_Y.astype(int).to_numpy()
            ll = y*np.log10(p)+(1-y)*np.log10(1-p)
            intervals = block_bootstrap(y, p, evaluate.latitude.to_numpy(),
                                        evaluate.longitude.to_numpy(), evaluate.target_year.to_numpy())
            scores.append({
                "horizon": horizon, "model": name, "n_train": len(train), "n_test": len(evaluate),
                "test_event_rate": float(y.mean()), "mean_log10_likelihood": float(ll.mean()),
                "total_log10_likelihood": float(ll.sum()), "brier_score": float(brier_score_loss(y, p)),
                "calibration_gap": calibration_gap(y, p), **intervals, "status": "opened_once",
            })
            if crosswalk is not None:
                regional.extend(regional_scores(evaluate, y, p, crosswalk, name, horizon))
    output.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(scores).to_csv(output/"LOCKED_TEST_scores.csv", index=False)
    if regional:
        pd.DataFrame(regional).to_csv(output/"LOCKED_TEST_ecoregion_scores.csv", index=False)
    note = "Locked test opened once. Preserve outputs, hashes, code version and deviations.\n"
    (output/"LOCKED_TEST_OPENED.txt").write_text(note, encoding="utf-8")
    marker.parent.mkdir(parents=True, exist_ok=True)
    marker.write_text(note, encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="Prepared real cell_monthly.csv")
    parser.add_argument("--crosswalk", help="Optional cell_ecoregion_weights.csv")
    parser.add_argument("--output", default="pilot_outputs")
    parser.add_argument("--open-locked-test", action="store_true")
    parser.add_argument("--prior", default="PRIOR_PREDICTION.md")
    parser.add_argument("--freeze", default="analysis_freeze.json")
    parser.add_argument("--test-lock-marker", default=".locked_test_opened.txt")
    args = parser.parse_args()
    source = Path(args.input)
    if not source.is_file():
        raise FileNotFoundError(source)
    monthly = validate_monthly_input(pd.read_csv(source, low_memory=False))
    crosswalk = None
    if args.crosswalk:
        crosswalk = validate_crosswalk(pd.read_csv(args.crosswalk, low_memory=False), monthly.grid_id.unique())
        areas = crosswalk.groupby("grid_id").intersection_land_area_km2.sum()
        cells = monthly.drop_duplicates("grid_id").set_index("grid_id").land_area_km2
        compare = pd.concat([cells.rename("cell"), areas.rename("crosswalk")], axis=1).dropna()
        relative = (compare.cell-compare.crosswalk).abs()/compare.cell.replace(0, np.nan)
        if (relative > 0.01).any():
            raise ValueError("Crosswalk intersection area differs from cell land area by more than 1%.")
    indicators = build_indicators(monthly)
    indicators = add_lags(indicators, ["soil_moisture_z", "D", "burned_fraction", "F",
                                       "ndvi_z", "V", "t2m_c", "precip_mm"])
    output = Path(args.output)
    write_development_outputs(indicators, output, crosswalk)
    if args.open_locked_test:
        open_locked_test(indicators, output, Path(args.prior), Path(args.freeze),
                         Path(args.test_lock_marker), crosswalk)
    print(f"Development and validation outputs written to: {output.resolve()}")
    if args.open_locked_test:
        print("Locked test released once. Preserve all outputs and manifest hashes.")
    else:
        print("Locked test remains closed; no 2021-2024 outcome summaries or scores were written.")
    return 0

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
