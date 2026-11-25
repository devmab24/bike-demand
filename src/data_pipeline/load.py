"""Reusable loader for the UCI Bike Sharing hourly dataset (hour.csv).

This module only loads and structurally validates the raw file. It does not
drop, transform, or impute columns; leakage exclusion and preprocessing belong
to the modelling pipeline.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

DEFAULT_PATH = "data/raw/hour.csv"

EXPECTED_ROWS = 17379
EXPECTED_COLUMNS = 17

REQUIRED_COLUMNS: tuple[str, ...] = (
    "instant",
    "dteday",
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
    "casual",
    "registered",
    "cnt",
)


def validate_hour_frame(df: pd.DataFrame) -> pd.DataFrame:
    """Check the structure of a loaded hour.csv frame.

    Raises:
        ValueError: if the row count, column count, or required columns differ
            from the UCI Bike Sharing hourly dataset.
    """
    if len(df) != EXPECTED_ROWS:
        raise ValueError(
            f"hour.csv must have {EXPECTED_ROWS} rows, found {len(df)}."
        )
    if df.shape[1] != EXPECTED_COLUMNS:
        raise ValueError(
            f"hour.csv must have {EXPECTED_COLUMNS} columns, found {df.shape[1]}."
        )
    missing = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing:
        raise ValueError(f"hour.csv is missing required columns: {missing}.")
    return df


def load_hour_csv(path: str | Path = DEFAULT_PATH) -> pd.DataFrame:
    """Read hour.csv and validate its structure.

    The file is read only; it is never modified. Columns are returned exactly
    as stored in the file.

    Args:
        path: Location of the raw hour.csv file. Relative paths resolve against
            the current working directory.

    Returns:
        A pandas DataFrame with 17,379 rows and 17 columns.

    Raises:
        FileNotFoundError: if the file does not exist.
        ValueError: if the file cannot be parsed or fails structural validation.
    """
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(
            f"Dataset not found at '{file_path}'. Stage the UCI hour.csv file "
            f"at '{DEFAULT_PATH}' (see README.md)."
        )
    try:
        df = pd.read_csv(file_path)
    except (pd.errors.ParserError, pd.errors.EmptyDataError, UnicodeDecodeError) as exc:
        raise ValueError(f"Could not parse '{file_path}' as CSV: {exc}") from exc
    return validate_hour_frame(df)
