import numpy as np
import pandas as pd
import pytest

from analysis.feasibility_pilot import (
    add_lags,
    build_indicators,
    calibration_gap,
    compound_labels,
    make_forecast_samples,
    validate_crosswalk,
    validate_monthly_input,
    write_development_outputs,
)


def test_compound_labels_distinguish_all_categories_and_missing():
    d = pd.Series([1, 1, 0, 1, 0, np.nan])
    f = pd.Series([1, 0, 1, 1, 0, 1])
    v = pd.Series([0, 1, 1, 1, 0, 1])
    y, category = compound_labels(d, f, v)
    assert category.tolist() == ["DF", "DV", "FV", "DFV", "NONE", "NOT_EVALUABLE"]
    assert y.iloc[:4].tolist() == [1.0, 1.0, 1.0, 1.0]
    assert y.iloc[4] == 0.0
    assert np.isnan(y.iloc[5])


def test_monthly_input_rejects_missing_months():
    frame = pd.DataFrame({
        "grid_id": ["g1", "g1"], "date": ["2001-01-01", "2001-03-01"],
        "latitude": [0, 0], "longitude": [0, 0], "land_area_km2": [100, 100],
        "ecoregion_id": ["e1", "e1"], "ecoregion_name": ["eco", "eco"],
        "biome_name": ["forest", "forest"], "realm": ["x", "x"],
        "ecoregion_fraction": [1, 1], "swvl1": [.2, .2], "swvl2": [.2, .2],
        "swvl3": [.2, .2], "t2m_c": [20, 20], "precip_mm": [10, 10],
        "ndvi": [.5, .5], "ndvi_good_fraction": [1, 1],
        "burned_area_km2": [0, 0], "valid_land_area_km2": [100, 100],
        "fire_shortened_fraction": [0, 0], "fire_unburned_special_fraction": [0, 0],
    })
    with pytest.raises(ValueError, match="Missing monthly"):
        validate_monthly_input(frame)


def test_monthly_input_rejects_grid_metadata_changing_within_cell():
    frame = _synthetic_monthly().iloc[:4].copy()
    frame.loc[frame.index[-1], "latitude"] += 1
    with pytest.raises(ValueError, match="latitude changes"):
        validate_monthly_input(frame)


def test_forecast_uses_exact_future_month_and_current_information():
    dates = pd.date_range("2001-05-01", periods=5, freq="MS")
    frame = pd.DataFrame({
        "grid_id": ["g1"] * 5, "date": dates,
        "Y": [0, 1, 0, 1, 0],
        "event_category": ["NONE", "DF", "NONE", "DV", "NONE"],
        "feature": [10, 20, 30, 40, 50],
    })
    lagged = add_lags(frame, ["feature"], max_lag=2)
    one = make_forecast_samples(lagged, 1)
    three = make_forecast_samples(lagged, 3)
    assert one.iloc[0].target_Y == 1
    assert one.iloc[0].feature_lag0 == 10
    assert one.iloc[0].target_date == pd.Timestamp("2001-06-01")
    assert three.iloc[0].target_Y == 1
    assert three.iloc[0].target_date == pd.Timestamp("2001-08-01")


def test_crosswalk_requires_area_fractions_to_sum_to_one():
    frame = pd.DataFrame({
        "grid_id": ["g1", "g1"], "ecoregion_id": ["e1", "e2"],
        "ecoregion_name": ["one", "two"], "biome_name": ["forest", "forest"],
        "realm": ["x", "x"], "intersection_land_area_km2": [60, 40],
        "area_fraction_of_cell_land": [.6, .4],
    })
    assert len(validate_crosswalk(frame)) == 2
    bad = frame.copy()
    bad.loc[0, "area_fraction_of_cell_land"] = .5
    with pytest.raises(ValueError, match="sum to 1"):
        validate_crosswalk(bad)


def test_calibration_gap_is_zero_for_perfect_binary_predictions():
    y = np.array([0, 0, 1, 1])
    p = np.array([0, 0, 1, 1])
    assert calibration_gap(y, p, bins=2) == 0


def _synthetic_monthly():
    """Clearly synthetic rows used only to exercise software; never empirical data."""
    dates = pd.date_range("1980-10-01", "2024-12-01", freq="MS")
    rows = []
    for cell in range(3):
        grid_id = f"synthetic-{cell}"
        for date in dates:
            year, month = date.year, date.month
            phase = (year * 7 + month * 11 + cell * 13) % 29
            soil = 0.24 + 0.012 * phase + 0.008 * np.sin(month * np.pi / 6)
            ndvi = 0.25 + 0.018 * ((year * 5 + month * 3 + cell * 7) % 31)
            fire_code = (year * 3 + month * 7 + cell * 5) % 19
            burned_fraction = 0.0 if fire_code in (0, 1) else 0.005 + 0.006 * fire_code
            rows.append({
                "grid_id": grid_id,
                "date": date,
                "latitude": -12.0 + cell * 12.0,
                "longitude": 20.0 + cell * 40.0,
                "land_area_km2": 1000.0,
                "ecoregion_id": "eco-synthetic",
                "ecoregion_name": "Synthetic test ecoregion",
                "biome_name": "Tropical and Subtropical Moist Broadleaf Forests",
                "realm": "Afrotropical",
                "ecoregion_fraction": 1.0,
                "swvl1": soil,
                "swvl2": soil * 0.95,
                "swvl3": soil * 0.90,
                "t2m_c": 20.0 + (month / 12) + cell,
                "precip_mm": 40.0 + (phase * 2),
                "ndvi": ndvi,
                "ndvi_good_fraction": 1.0,
                "burned_area_km2": burned_fraction * 900.0,
                "valid_land_area_km2": 900.0,
                "fire_shortened_fraction": 0.0,
                "fire_unburned_special_fraction": 0.0,
            })
    return pd.DataFrame(rows)


def test_end_to_end_synthetic_software_pipeline_writes_only_development_outputs(tmp_path):
    """Synthetic fixture validates code paths; it is not evidence about any ecosystem."""
    monthly = validate_monthly_input(_synthetic_monthly())
    indicators = build_indicators(monthly)
    assert {"D", "F", "V", "Y", "event_category"}.issubset(indicators.columns)
    indicators = add_lags(indicators, [
        "soil_moisture_z", "D", "burned_fraction", "F", "ndvi_z", "V", "t2m_c", "precip_mm"
    ])
    output = tmp_path / "synthetic-test-only"
    write_development_outputs(indicators, output)
    assert (output / "validation_model_scores.csv").is_file()
    assert (output / "development_event_counts.csv").is_file()
    assert (output / "pilot_report.md").is_file()
    assert not (output / "LOCKED_TEST_scores.csv").exists()
    assert not (output / "LOCKED_TEST_OPENED.txt").exists()
