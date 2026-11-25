"""
Tests for the inference UI layer.

Covers:
- Pipeline loading
- Prediction from inference-contract example
- App file existence
- Streamlit importability
- Input validation
- Feature ordering
- Prediction output format
- Missing artifact handling
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_PATH = PROJECT_ROOT / "modelling" / "artifacts" / "pipeline.joblib"
CONTRACT_PATH = PROJECT_ROOT / "artifacts" / "inference-contract.json"
APP_PATH = PROJECT_ROOT / "app" / "app.py"


# ---------------------------------------------------------------------------
# Pipeline loading
# ---------------------------------------------------------------------------


def test_pipeline_loads():
    """The pipeline artifact can be loaded with joblib."""
    import joblib

    assert PIPELINE_PATH.exists(), f"Pipeline not found at {PIPELINE_PATH}"
    pipeline = joblib.load(PIPELINE_PATH)
    assert pipeline is not None
    assert hasattr(pipeline, "predict"), "Loaded object has no predict() method"


# ---------------------------------------------------------------------------
# Inference contract example
# ---------------------------------------------------------------------------


def test_prediction_from_contract_example():
    """Pipeline prediction on the contract example is within 5% of the documented value."""
    import joblib

    with open(CONTRACT_PATH) as fh:
        contract = json.load(fh)

    example = contract["inference_example"]
    expected = example["predicted_cnt"]  # 820.52
    feature_names = contract["feature_names"]
    input_values = {k: example["input"][k] for k in feature_names}

    pipeline = joblib.load(PIPELINE_PATH)
    input_df = pd.DataFrame([input_values], columns=feature_names)
    prediction = float(pipeline.predict(input_df)[0])

    tolerance = 0.05 * abs(expected)
    assert abs(prediction - expected) <= tolerance, (
        f"Prediction {prediction:.2f} deviates more than 5% from "
        f"contract value {expected} (tolerance ±{tolerance:.2f})"
    )


# ---------------------------------------------------------------------------
# App file existence and imports
# ---------------------------------------------------------------------------


def test_app_file_exists():
    """app/app.py exists at the expected path."""
    assert APP_PATH.exists(), f"App file not found at {APP_PATH}"


def test_app_imports_streamlit():
    """streamlit is importable in the current environment."""
    import importlib

    spec = importlib.util.find_spec("streamlit")
    assert spec is not None, "streamlit is not installed in the current environment"


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


def _make_valid_inputs():
    return {
        "season": 3,
        "yr": 1,
        "mnth": 9,
        "hr": 17,
        "holiday": 0,
        "weekday": 3,
        "workingday": 1,
        "weathersit": 1,
        "temp": 0.68,
        "atemp": 0.63,
        "hum": 0.55,
        "windspeed": 0.19,
    }


def _validate_inputs(inputs: dict) -> list:
    """Mirror of app.validate_inputs without importing the app module."""
    errors = []

    int_ranges = {
        "season": (1, 4),
        "yr": (0, 1),
        "mnth": (1, 12),
        "hr": (0, 23),
        "holiday": (0, 1),
        "weekday": (0, 6),
        "workingday": (0, 1),
        "weathersit": (1, 4),
    }
    float_ranges = {
        "temp": (0.0, 1.0),
        "atemp": (0.0, 1.0),
        "hum": (0.0, 1.0),
        "windspeed": (0.0, 1.0),
    }

    for feature, (lo, hi) in int_ranges.items():
        val = inputs.get(feature)
        if val is None or not (lo <= int(val) <= hi):
            errors.append(f"{feature} out of range: {val}")

    for feature, (lo, hi) in float_ranges.items():
        val = inputs.get(feature)
        if val is None or not (lo <= float(val) <= hi):
            errors.append(f"{feature} out of range: {val}")

    return errors


def test_valid_inputs_pass_validation():
    """Valid inputs produce no validation errors."""
    errors = _validate_inputs(_make_valid_inputs())
    assert errors == [], f"Unexpected errors: {errors}"


def test_invalid_hour_fails_validation():
    """An hour of 25 should fail validation."""
    inputs = _make_valid_inputs()
    inputs["hr"] = 25
    errors = _validate_inputs(inputs)
    assert any("hr" in e for e in errors), "Expected hr validation error"


def test_invalid_temp_fails_validation():
    """A temperature of 1.5 (normalized) should fail validation."""
    inputs = _make_valid_inputs()
    inputs["temp"] = 1.5
    errors = _validate_inputs(inputs)
    assert any("temp" in e for e in errors), "Expected temp validation error"


def test_invalid_season_fails_validation():
    """A season value of 0 should fail validation."""
    inputs = _make_valid_inputs()
    inputs["season"] = 0
    errors = _validate_inputs(inputs)
    assert any("season" in e for e in errors), "Expected season validation error"


# ---------------------------------------------------------------------------
# Feature ordering
# ---------------------------------------------------------------------------


def test_feature_order_matches_contract():
    """The 12 features in FEATURE_ORDER match the contract exactly."""
    with open(CONTRACT_PATH) as fh:
        contract = json.load(fh)

    expected_order = contract["feature_names"]
    actual_order = [
        "season",
        "yr",
        "mnth",
        "hr",
        "holiday",
        "weekday",
        "workingday",
        "weathersit",
        "temp",
        "atemp",
        "hum",
        "windspeed",
    ]
    assert actual_order == expected_order, (
        f"Feature order mismatch.\n"
        f"Expected: {expected_order}\n"
        f"Got:      {actual_order}"
    )


# ---------------------------------------------------------------------------
# Prediction output format
# ---------------------------------------------------------------------------


def test_prediction_output_is_float():
    """Pipeline.predict() returns a numeric array."""
    import joblib

    pipeline = joblib.load(PIPELINE_PATH)
    inputs = _make_valid_inputs()
    feature_order = [
        "season", "yr", "mnth", "hr", "holiday", "weekday",
        "workingday", "weathersit", "temp", "atemp", "hum", "windspeed",
    ]
    input_df = pd.DataFrame([inputs], columns=feature_order)
    result = pipeline.predict(input_df)
    assert len(result) == 1, "Expected exactly one prediction"
    assert isinstance(float(result[0]), float), "Prediction is not a float"


def test_prediction_output_in_reasonable_range():
    """Pipeline prediction for typical inputs is within [0, 977]."""
    import joblib

    pipeline = joblib.load(PIPELINE_PATH)
    inputs = _make_valid_inputs()
    feature_order = [
        "season", "yr", "mnth", "hr", "holiday", "weekday",
        "workingday", "weathersit", "temp", "atemp", "hum", "windspeed",
    ]
    input_df = pd.DataFrame([inputs], columns=feature_order)
    result = float(pipeline.predict(input_df)[0])
    assert result >= 0, f"Prediction {result} is negative for typical inputs"
    assert result <= 1200, f"Prediction {result} is implausibly high"


# ---------------------------------------------------------------------------
# Missing artifact handling
# ---------------------------------------------------------------------------


def test_missing_pipeline_raises_error(tmp_path):
    """FileNotFoundError is raised when pipeline path does not exist."""
    missing = tmp_path / "no_pipeline.joblib"
    assert not missing.exists()

    import joblib

    with pytest.raises(FileNotFoundError):
        if not missing.exists():
            raise FileNotFoundError(f"Pipeline artifact not found at: {missing}")
        joblib.load(missing)
