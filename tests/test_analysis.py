import numpy as np
import pandas as pd
import pytest

from analysis.feasibility_pilot import (
    add_lags, calibration_gap, compound_labels, make_forecast_samples,
    validate_crosswalk, validate_monthly_input,
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
        "fire_shortened_fraction": [0, 0],
    })
    with pytest.raises(ValueError, match="Missing monthly"):
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
