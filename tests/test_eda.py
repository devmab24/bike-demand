"""Tests for EDA artifacts produced by src/data_analysis/eda.py."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_EDA = PROJECT_ROOT / "artifacts" / "eda"
FIGURES = PROJECT_ROOT / "reports" / "figures"


def test_summary_statistics_csv_exists():
    """summary_statistics.csv must exist and contain at least one data row."""
    path = ARTIFACTS_EDA / "summary_statistics.csv"
    assert path.exists(), f"File not found: {path}"
    df = pd.read_csv(path, index_col=0)
    assert len(df) > 0, "summary_statistics.csv is empty"


def test_correlation_matrix_csv_exists():
    """correlation_matrix.csv must exist, contain a cnt column, and have all values in [-1, 1]."""
    path = ARTIFACTS_EDA / "correlation_matrix.csv"
    assert path.exists(), f"File not found: {path}"
    df = pd.read_csv(path, index_col=0)
    assert "cnt" in df.columns, "correlation_matrix.csv must contain a 'cnt' column"
    numeric_vals = df.select_dtypes(include="number").values
    assert (numeric_vals >= -1.0).all() and (numeric_vals <= 1.0).all(), (
        "All correlation values must be in [-1, 1]"
    )


def test_demand_by_hour_csv_exists():
    """demand_by_hour.csv must exist and have exactly 24 rows (one per hour)."""
    path = ARTIFACTS_EDA / "demand_by_hour.csv"
    assert path.exists(), f"File not found: {path}"
    df = pd.read_csv(path)
    assert len(df) == 24, f"demand_by_hour.csv must have 24 rows, found {len(df)}"


def test_no_leakage_in_correlation_csv():
    """casual and registered must NOT appear in the correlation matrix columns (target leakage)."""
    path = ARTIFACTS_EDA / "correlation_matrix.csv"
    assert path.exists(), f"File not found: {path}"
    df = pd.read_csv(path, index_col=0)
    leakage_cols = {"casual", "registered"}
    present = leakage_cols.intersection(set(df.columns))
    assert not present, (
        f"Leakage columns found in correlation matrix: {present}. "
        "casual and registered must be excluded."
    )


def test_figures_exist():
    """All 6 required PNG figures must exist."""
    expected_figures = [
        "01_target_distribution.png",
        "02_demand_by_hour.png",
        "03_demand_by_season.png",
        "04_demand_by_weather.png",
        "05_correlation_heatmap.png",
        "06_demand_workingday_vs_weekend.png",
    ]
    missing = []
    for fname in expected_figures:
        path = FIGURES / fname
        if not path.exists():
            missing.append(str(path))
    assert not missing, f"Missing figure files:\n" + "\n".join(missing)
