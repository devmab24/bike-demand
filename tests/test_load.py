"""Tests for the hour.csv loader.

Run with: uv run pytest tests/test_load.py -v
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from src.data_pipeline.load import (
    EXPECTED_COLUMNS,
    EXPECTED_ROWS,
    REQUIRED_COLUMNS,
    load_hour_csv,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATASET_PATH = PROJECT_ROOT / "data" / "raw" / "hour.csv"


@pytest.fixture(scope="module")
def hour_df() -> pd.DataFrame:
    return load_hour_csv(DATASET_PATH)


def test_load_returns_dataframe(hour_df: pd.DataFrame) -> None:
    assert isinstance(hour_df, pd.DataFrame)


def test_load_row_count(hour_df: pd.DataFrame) -> None:
    assert len(hour_df) == 17379 == EXPECTED_ROWS


def test_load_column_count(hour_df: pd.DataFrame) -> None:
    assert hour_df.shape[1] == 17 == EXPECTED_COLUMNS


def test_load_required_columns(hour_df: pd.DataFrame) -> None:
    assert len(REQUIRED_COLUMNS) == 17
    assert list(hour_df.columns) == list(REQUIRED_COLUMNS)


def test_target_column_nonnegative(hour_df: pd.DataFrame) -> None:
    assert hour_df["cnt"].ge(0).all()


def test_no_leaked_columns_excluded(hour_df: pd.DataFrame) -> None:
    # Loading is neutral: leakage columns must still be present here.
    # Exclusion of casual/registered/instant is the ML pipeline's job.
    for col in ("instant", "casual", "registered", "cnt"):
        assert col in hour_df.columns


def test_no_missing_values(hour_df: pd.DataFrame) -> None:
    assert int(hour_df.isna().sum().sum()) == 0


def test_cnt_equals_casual_plus_registered(hour_df: pd.DataFrame) -> None:
    assert (hour_df["cnt"] == hour_df["casual"] + hour_df["registered"]).all()


def test_missing_path_raises_file_not_found(tmp_path: Path) -> None:
    with pytest.raises(FileNotFoundError, match="Dataset not found"):
        load_hour_csv(tmp_path / "does_not_exist.csv")


def test_wrong_structure_raises_value_error(tmp_path: Path) -> None:
    bad = tmp_path / "hour.csv"
    bad.write_text("instant,cnt\n1,5\n2,7\n", encoding="utf-8")
    with pytest.raises(ValueError, match="must have 17379 rows"):
        load_hour_csv(bad)


def test_missing_required_column_raises_value_error(tmp_path: Path, hour_df: pd.DataFrame) -> None:
    broken = hour_df.drop(columns=["temp"]).copy()
    # Add a column back under a different name so the column count stays at 17
    # and the required-column check is what fails.
    broken["temp_x"] = 0.0
    path = tmp_path / "hour.csv"
    broken.to_csv(path, index=False)
    with pytest.raises(ValueError, match="missing required columns"):
        load_hour_csv(path)
