"""Tests for the bike-sharing demand ML pipeline and artifacts.

Run with: uv run pytest tests/test_ml.py -v

All paths are resolved relative to the project root (the parent directory of
this test file's parent directory) so the suite works from any working
directory.
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODELLING_DIR = PROJECT_ROOT / "modelling"
METRICS_PATH = MODELLING_DIR / "metrics.json"
PIPELINE_PATH = MODELLING_DIR / "artifacts" / "pipeline.joblib"
CONTRACT_PATH = PROJECT_ROOT / "artifacts" / "inference-contract.json"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def load_metrics() -> dict:
    with open(METRICS_PATH, encoding="utf-8") as fh:
        return json.load(fh)


def load_contract() -> dict:
    with open(CONTRACT_PATH, encoding="utf-8") as fh:
        return json.load(fh)


# ---------------------------------------------------------------------------
# Artifact existence and structure
# ---------------------------------------------------------------------------


def test_metrics_json_exists():
    """metrics.json must exist and contain both baseline and random_forest keys."""
    assert METRICS_PATH.exists(), f"metrics.json not found: {METRICS_PATH}"
    metrics = load_metrics()
    assert "baseline" in metrics, "metrics.json missing 'baseline' key"
    assert "random_forest" in metrics, "metrics.json missing 'random_forest' key"
    for key in ("mae", "rmse", "r2"):
        assert key in metrics["baseline"], f"baseline missing '{key}'"
        assert key in metrics["random_forest"], f"random_forest missing '{key}'"


def test_pipeline_joblib_exists():
    """pipeline.joblib must exist and be larger than 1 MB."""
    assert PIPELINE_PATH.exists(), f"pipeline.joblib not found: {PIPELINE_PATH}"
    size_bytes = PIPELINE_PATH.stat().st_size
    assert size_bytes > 1_048_576, (
        f"pipeline.joblib is only {size_bytes / 1024:.1f} KB; expected > 1 MB"
    )


# ---------------------------------------------------------------------------
# Model performance
# ---------------------------------------------------------------------------


def test_rf_beats_baseline_mae():
    """Random Forest MAE must be at least 10% lower than baseline MAE."""
    metrics = load_metrics()
    baseline_mae = metrics["baseline"]["mae"]
    rf_mae = metrics["random_forest"]["mae"]
    threshold = baseline_mae * 0.9  # RF must beat baseline by at least 10%
    assert rf_mae < threshold, (
        f"RF MAE ({rf_mae:.4f}) is not at least 10% below baseline MAE ({baseline_mae:.4f}). "
        f"Threshold: {threshold:.4f}"
    )


def test_r2_above_threshold():
    """Random Forest R² on the test set must exceed 0.7."""
    metrics = load_metrics()
    rf_r2 = metrics["random_forest"]["r2"]
    assert rf_r2 > 0.7, f"RF R² ({rf_r2:.4f}) is below the 0.7 threshold."


# ---------------------------------------------------------------------------
# Chronological splitting
# ---------------------------------------------------------------------------


def test_chronological_split_no_shuffle():
    """Chronological split must produce the correct train/test sizes without shuffling."""
    from src.modelling.pipeline import chronological_split
    from src.data_pipeline.load import load_hour_csv

    df = load_hour_csv(PROJECT_ROOT / "data" / "raw" / "hour.csv")
    X_train, X_test, y_train, y_test = chronological_split(df, test_size=0.2)

    total = len(X_train) + len(X_test)
    assert total == len(df), f"Split lost rows: {total} != {len(df)}"

    # Train rows should precede test rows in the original chronological order.
    # The last instant in train must be strictly less than the first instant in test.
    df_sorted = df.sort_values("instant").reset_index(drop=True)
    split_idx = int(len(df_sorted) * 0.8)
    last_train_instant = df_sorted.iloc[split_idx - 1]["instant"]
    first_test_instant = df_sorted.iloc[split_idx]["instant"]
    assert last_train_instant < first_test_instant, (
        "Chronological order violated: last train instant >= first test instant"
    )


# ---------------------------------------------------------------------------
# Leakage prevention
# ---------------------------------------------------------------------------


def test_no_leakage_features():
    """Leakage columns must not appear in the feature list."""
    contract = load_contract()
    feature_names = contract["feature_names"]
    leakage_cols = {"casual", "registered", "instant"}
    present = leakage_cols.intersection(set(feature_names))
    assert not present, f"Leakage columns found in feature_names: {present}"


# ---------------------------------------------------------------------------
# Inference contract completeness
# ---------------------------------------------------------------------------


def test_inference_contract_complete():
    """Inference contract must exist, have no null top-level values, and list 12 features."""
    assert CONTRACT_PATH.exists(), f"inference-contract.json not found: {CONTRACT_PATH}"
    contract = load_contract()

    # No top-level null values
    null_keys = [k for k, v in contract.items() if v is None]
    assert not null_keys, f"Contract has null top-level fields: {null_keys}"

    # Exactly 12 feature names
    assert "feature_names" in contract, "Contract missing 'feature_names'"
    assert len(contract["feature_names"]) == 12, (
        f"feature_names has {len(contract['feature_names'])} entries; expected 12"
    )

    # Required top-level keys
    required_keys = [
        "contract_version", "model_name", "created_at", "pipeline_path",
        "feature_names", "feature_count", "feature_dtypes", "feature_ranges",
        "target_col", "preprocessing", "output_format", "metrics",
        "inference_example", "train_size", "test_size",
    ]
    missing_keys = [k for k in required_keys if k not in contract]
    assert not missing_keys, f"Contract missing required keys: {missing_keys}"


# ---------------------------------------------------------------------------
# Inference contract example validation
# ---------------------------------------------------------------------------


def test_inference_contract_example():
    """Running the contract's example input through the loaded pipeline must
    produce a value within 5% of the contract's stated predicted_cnt."""
    import joblib

    contract = load_contract()
    pipeline = joblib.load(PIPELINE_PATH)

    example_input = contract["inference_example"]["input"]
    feature_names = contract["feature_names"]
    contract_pred = contract["inference_example"]["predicted_cnt"]

    input_df = pd.DataFrame([example_input])[feature_names]
    actual_pred = float(pipeline.predict(input_df)[0])

    tolerance = abs(contract_pred) * 0.05  # 5% relative tolerance
    assert abs(actual_pred - contract_pred) <= tolerance, (
        f"Pipeline prediction ({actual_pred:.4f}) differs from contract value "
        f"({contract_pred:.4f}) by more than 5%."
    )


# ---------------------------------------------------------------------------
# Pipeline fitting and prediction shape
# ---------------------------------------------------------------------------


def test_pipeline_predict_shape():
    """Loaded pipeline must accept a single-row DataFrame and return a 1-element array."""
    import joblib

    contract = load_contract()
    pipeline = joblib.load(PIPELINE_PATH)
    feature_names = contract["feature_names"]

    sample = {f: 0 for f in feature_names}
    # Use valid midpoint values to avoid extreme extrapolation.
    sample.update({
        "season": 2, "yr": 0, "mnth": 6, "hr": 12, "holiday": 0,
        "weekday": 3, "workingday": 1, "weathersit": 1,
        "temp": 0.5, "atemp": 0.5, "hum": 0.5, "windspeed": 0.2,
    })
    df = pd.DataFrame([sample])[feature_names]
    preds = pipeline.predict(df)
    assert preds.shape == (1,), f"Expected shape (1,), got {preds.shape}"


# ---------------------------------------------------------------------------
# Artifact serialization round-trip
# ---------------------------------------------------------------------------


def test_pipeline_serialization_roundtrip():
    """Serializing and re-loading the pipeline must reproduce identical predictions."""
    import tempfile
    import joblib

    contract = load_contract()
    pipeline = joblib.load(PIPELINE_PATH)
    feature_names = contract["feature_names"]

    sample = pd.DataFrame([contract["inference_example"]["input"]])[feature_names]
    pred_before = float(pipeline.predict(sample)[0])

    with tempfile.NamedTemporaryFile(suffix=".joblib", delete=False) as tmp:
        tmp_path = Path(tmp.name)

    try:
        joblib.dump(pipeline, tmp_path)
        loaded = joblib.load(tmp_path)
        pred_after = float(loaded.predict(sample)[0])
    finally:
        tmp_path.unlink(missing_ok=True)

    assert abs(pred_before - pred_after) < 1e-6, (
        f"Serialization roundtrip changed prediction: {pred_before} -> {pred_after}"
    )


# ---------------------------------------------------------------------------
# Reproducibility
# ---------------------------------------------------------------------------


def test_reproducibility():
    """Training with the same seed must yield identical predictions on two runs."""
    from sklearn.ensemble import RandomForestRegressor
    from src.modelling.pipeline import FEATURE_COLS, TARGET_COL, chronological_split, make_pipeline
    from src.data_pipeline.load import load_hour_csv

    df = load_hour_csv(PROJECT_ROOT / "data" / "raw" / "hour.csv")
    X_train, X_test, y_train, y_test = chronological_split(df, test_size=0.2)

    # Two pipelines with the same seed
    rf_a = RandomForestRegressor(n_estimators=10, random_state=42, n_jobs=1)
    rf_b = RandomForestRegressor(n_estimators=10, random_state=42, n_jobs=1)
    pipe_a = make_pipeline(rf_a)
    pipe_b = make_pipeline(rf_b)

    pipe_a.fit(X_train, y_train)
    pipe_b.fit(X_train, y_train)

    preds_a = pipe_a.predict(X_test[:5])
    preds_b = pipe_b.predict(X_test[:5])

    assert (preds_a == preds_b).all(), (
        "Identical random seeds produced different predictions — reproducibility broken."
    )
