"""Training script for the bike-sharing demand prediction models.

Trains and evaluates two models:
  - Baseline: DummyRegressor(strategy='mean')
  - Random Forest: RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)

Artifacts saved:
  modelling/artifacts/pipeline.joblib   -- fitted Random Forest pipeline
  modelling/metrics.json                 -- metrics for both models
  modelling/figures/feature_importance.png
  modelling/figures/actual_vs_predicted.png

Usage:
    uv run python src/modelling/train.py

Random seed: 42 (set via random_state on RandomForestRegressor).
"""

from __future__ import annotations

import json
import math
import sys
from pathlib import Path

# Use Agg backend before any pyplot import to avoid display requirements.
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

import joblib
import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "hour.csv"
MODELLING_DIR = PROJECT_ROOT / "modelling"
ARTIFACTS_DIR = MODELLING_DIR / "artifacts"
FIGURES_DIR = MODELLING_DIR / "figures"

ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# Add project root to path so src imports work when run directly.
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.data_pipeline.load import load_hour_csv
from src.modelling.pipeline import (
    FEATURE_COLS,
    RANDOM_SEED,
    TARGET_COL,
    chronological_split,
    make_pipeline,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def compute_metrics(y_true: pd.Series, y_pred: np.ndarray) -> dict[str, float]:
    """Compute MAE, RMSE, and R² from actual and predicted values."""
    mae = float(mean_absolute_error(y_true, y_pred))
    rmse = float(math.sqrt(mean_squared_error(y_true, y_pred)))
    r2 = float(r2_score(y_true, y_pred))
    return {"mae": mae, "rmse": rmse, "r2": r2}


# ---------------------------------------------------------------------------
# Training
# ---------------------------------------------------------------------------


def main() -> None:
    print("=" * 60)
    print("Bike-Sharing Demand — Model Training")
    print("=" * 60)

    # 1. Load data
    print(f"\nLoading data from {DATA_PATH} ...")
    df = load_hour_csv(DATA_PATH)
    print(f"  Loaded {len(df):,} rows, {df.shape[1]} columns.")

    # 2. Chronological split (no shuffle)
    X_train, X_test, y_train, y_test = chronological_split(df, test_size=0.2)
    split_index = len(X_train)
    print(f"\nChronological split (test_size=0.2):")
    print(f"  Train: {len(X_train):,} rows | Test: {len(X_test):,} rows")
    print(f"  Split at row index: {split_index}")

    # 3a. Baseline model
    print("\nTraining Baseline (DummyRegressor, strategy='mean') ...")
    baseline_pipeline = make_pipeline(DummyRegressor(strategy="mean"))
    baseline_pipeline.fit(X_train, y_train)
    y_pred_baseline = baseline_pipeline.predict(X_test)
    baseline_metrics = compute_metrics(y_test, y_pred_baseline)
    print(f"  Baseline MAE:  {baseline_metrics['mae']:.4f}")
    print(f"  Baseline RMSE: {baseline_metrics['rmse']:.4f}")
    print(f"  Baseline R²:   {baseline_metrics['r2']:.4f}")

    # 3b. Random Forest model
    print("\nTraining Random Forest (n_estimators=100, random_state=42, n_jobs=-1) ...")
    rf = RandomForestRegressor(
        n_estimators=100,
        random_state=RANDOM_SEED,
        n_jobs=-1,
    )
    rf_pipeline = make_pipeline(rf)
    rf_pipeline.fit(X_train, y_train)
    y_pred_rf = rf_pipeline.predict(X_test)
    rf_metrics = compute_metrics(y_test, y_pred_rf)
    print(f"  RF MAE:  {rf_metrics['mae']:.4f}")
    print(f"  RF RMSE: {rf_metrics['rmse']:.4f}")
    print(f"  RF R²:   {rf_metrics['r2']:.4f}")

    # 4. Save pipeline.joblib (Random Forest only)
    pipeline_path = ARTIFACTS_DIR / "pipeline.joblib"
    joblib.dump(rf_pipeline, pipeline_path)
    size_mb = pipeline_path.stat().st_size / (1024 * 1024)
    print(f"\nSaved RF pipeline: {pipeline_path}  ({size_mb:.2f} MB)")

    # 5. Save metrics.json
    metrics_dict = {
        "baseline": baseline_metrics,
        "random_forest": rf_metrics,
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "feature_cols": FEATURE_COLS,
        "target_col": TARGET_COL,
        "split_index": int(split_index),
    }
    metrics_path = MODELLING_DIR / "metrics.json"
    with open(metrics_path, "w", encoding="utf-8") as fh:
        json.dump(metrics_dict, fh, indent=2)
    print(f"Saved metrics:     {metrics_path}")

    # 6a. Feature importance plot (top 15)
    rf_model = rf_pipeline.named_steps["model"]
    importances = rf_model.feature_importances_
    indices = np.argsort(importances)[::-1][:15]
    top_features = [FEATURE_COLS[i] for i in indices]
    top_importances = importances[indices]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(top_features[::-1], top_importances[::-1], color="steelblue")
    ax.set_xlabel("Feature Importance (mean decrease in impurity)")
    ax.set_title("Random Forest — Top Feature Importances\n(not causal evidence)")
    ax.set_xlim(0, top_importances.max() * 1.15)
    for bar, val in zip(bars, top_importances[::-1]):
        ax.text(val + 0.001, bar.get_y() + bar.get_height() / 2,
                f"{val:.4f}", va="center", fontsize=8)
    plt.tight_layout()
    fi_path = FIGURES_DIR / "feature_importance.png"
    fig.savefig(fi_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved figure:      {fi_path}")

    # 6b. Actual vs predicted plot
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.scatter(y_test, y_pred_rf, alpha=0.3, s=5, color="steelblue", label="Predictions")
    lims = [
        min(y_test.min(), y_pred_rf.min()),
        max(y_test.max(), y_pred_rf.max()),
    ]
    ax.plot(lims, lims, "r--", linewidth=1.5, label="Perfect prediction (y=x)")
    ax.set_xlabel("Actual cnt")
    ax.set_ylabel("Predicted cnt")
    ax.set_title("Random Forest — Actual vs Predicted\n(test set)")
    ax.legend()
    plt.tight_layout()
    avp_path = FIGURES_DIR / "actual_vs_predicted.png"
    fig.savefig(avp_path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"Saved figure:      {avp_path}")

    # 7. Compute inference example prediction
    example_input = {
        "season": 3, "yr": 1, "mnth": 9, "hr": 17,
        "holiday": 0, "weekday": 3, "workingday": 1,
        "weathersit": 1, "temp": 0.68, "atemp": 0.63,
        "hum": 0.55, "windspeed": 0.19,
    }
    example_df = pd.DataFrame([example_input])[FEATURE_COLS]
    predicted_cnt = float(rf_pipeline.predict(example_df)[0])
    print(f"\nInference example predicted_cnt: {predicted_cnt:.4f}")

    # 8. Write inference contract
    contract = {
        "contract_version": "1.0",
        "model_name": "bike-demand-random-forest",
        "created_at": "2026-11-25",
        "pipeline_path": "modelling/artifacts/pipeline.joblib",
        "feature_names": FEATURE_COLS,
        "feature_count": len(FEATURE_COLS),
        "feature_dtypes": {
            "season": "int64",
            "yr": "int64",
            "mnth": "int64",
            "hr": "int64",
            "holiday": "int64",
            "weekday": "int64",
            "workingday": "int64",
            "weathersit": "int64",
            "temp": "float64",
            "atemp": "float64",
            "hum": "float64",
            "windspeed": "float64",
        },
        "feature_ranges": {
            "season": {"min": 1, "max": 4, "description": "1=spring, 2=summer, 3=fall, 4=winter"},
            "yr": {"min": 0, "max": 1, "description": "0=2011, 1=2012"},
            "mnth": {"min": 1, "max": 12, "description": "calendar month"},
            "hr": {"min": 0, "max": 23, "description": "hour of day"},
            "holiday": {"min": 0, "max": 1, "description": "0=no holiday, 1=holiday"},
            "weekday": {"min": 0, "max": 6, "description": "0=Sunday, 6=Saturday"},
            "workingday": {"min": 0, "max": 1, "description": "0=weekend/holiday, 1=working day"},
            "weathersit": {"min": 1, "max": 4, "description": "1=clear, 2=mist, 3=light rain/snow, 4=heavy rain/ice"},
            "temp": {"min": 0.0, "max": 1.0, "description": "normalized temperature (divide Celsius by 41)"},
            "atemp": {"min": 0.0, "max": 1.0, "description": "normalized apparent temperature (divide Celsius by 50)"},
            "hum": {"min": 0.0, "max": 1.0, "description": "normalized humidity (divide by 100)"},
            "windspeed": {"min": 0.0, "max": 1.0, "description": "normalized wind speed (divide by 67)"},
        },
        "target_col": TARGET_COL,
        "target_description": "total bike rentals per hour",
        "target_min": int(df[TARGET_COL].min()),
        "target_max": int(df[TARGET_COL].max()),
        "preprocessing": {
            "steps": "StandardScaler applied to all 12 input features",
            "fit_on": "training set only (chronological split, first 80% by row order)",
            "note": "scaling is embedded in pipeline.joblib — do not scale inputs manually",
        },
        "output_format": {
            "type": "float64",
            "description": "predicted total bike rentals per hour",
            "note": "predictions may be negative in extreme out-of-range inputs; clip to 0 if needed",
        },
        "missing_value_handling": "none — pipeline does not impute; caller must supply all 12 features",
        "train_split_cutoff_index": int(split_index),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "metrics": {
            "baseline_mae": baseline_metrics["mae"],
            "baseline_rmse": baseline_metrics["rmse"],
            "baseline_r2": baseline_metrics["r2"],
            "random_forest_mae": rf_metrics["mae"],
            "random_forest_rmse": rf_metrics["rmse"],
            "random_forest_r2": rf_metrics["r2"],
        },
        "inference_example": {
            "input": example_input,
            "predicted_cnt": round(predicted_cnt, 4),
        },
    }

    contract_path = PROJECT_ROOT / "artifacts" / "inference-contract.json"
    with open(contract_path, "w", encoding="utf-8") as fh:
        json.dump(contract, fh, indent=2)
    print(f"Saved contract:    {contract_path}")

    # 9. Validate the inference contract example
    loaded_pipeline = joblib.load(pipeline_path)
    validation_df = pd.DataFrame([example_input])[FEATURE_COLS]
    validation_pred = float(loaded_pipeline.predict(validation_df)[0])
    contract_pred = contract["inference_example"]["predicted_cnt"]
    matches = abs(validation_pred - contract_pred) < 0.01
    print(f"\nContract validation: predicted={validation_pred:.4f}, "
          f"contract={contract_pred:.4f}, match={matches}")

    # 10. Summary
    print("\n" + "=" * 60)
    print("TRAINING SUMMARY")
    print("=" * 60)
    print(f"  Train rows:        {len(X_train):,}")
    print(f"  Test rows:         {len(X_test):,}")
    print(f"  Split index:       {split_index}")
    print()
    print(f"  Baseline MAE:      {baseline_metrics['mae']:.4f}")
    print(f"  Baseline RMSE:     {baseline_metrics['rmse']:.4f}")
    print(f"  Baseline R²:       {baseline_metrics['r2']:.4f}")
    print()
    print(f"  RF MAE:            {rf_metrics['mae']:.4f}")
    print(f"  RF RMSE:           {rf_metrics['rmse']:.4f}")
    print(f"  RF R²:             {rf_metrics['r2']:.4f}")
    print()
    mae_improvement = (baseline_metrics["mae"] - rf_metrics["mae"]) / baseline_metrics["mae"] * 100
    print(f"  MAE improvement:   {mae_improvement:.1f}% (RF vs baseline)")
    print("=" * 60)


if __name__ == "__main__":
    main()
