"""Shared pipeline components for the bike-sharing demand model.

Defines feature constants, preprocessor factory, pipeline factory, and
chronological data splitting. All preprocessing is fitted on training data
only to prevent data leakage.

Random seed: 42 (documented here; passed explicitly to RandomForestRegressor
in train.py).
"""

from __future__ import annotations

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

# ---------------------------------------------------------------------------
# Feature configuration
# ---------------------------------------------------------------------------

FEATURE_COLS: list[str] = [
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

TARGET_COL: str = "cnt"

# Columns explicitly excluded from features to prevent leakage.
EXCLUDED_COLS: tuple[str, ...] = ("cnt", "casual", "registered", "instant", "dteday")

RANDOM_SEED: int = 42


# ---------------------------------------------------------------------------
# Factories
# ---------------------------------------------------------------------------


def make_preprocessor() -> ColumnTransformer:
    """Return a ColumnTransformer that applies StandardScaler to all 12 features.

    The transformer must be fitted on training data only. remainder='drop'
    discards any columns not listed in FEATURE_COLS.

    Returns:
        An unfitted ColumnTransformer.
    """
    return ColumnTransformer(
        transformers=[
            ("scaler", StandardScaler(), FEATURE_COLS),
        ],
        remainder="drop",
    )


def make_pipeline(model) -> Pipeline:
    """Wrap a scikit-learn estimator in a preprocessing pipeline.

    The pipeline applies StandardScaler to all 12 features and then passes
    the scaled array to ``model``.

    Args:
        model: Any scikit-learn-compatible regressor.

    Returns:
        An unfitted Pipeline with steps ('preprocessor', 'model').
    """
    return Pipeline(
        steps=[
            ("preprocessor", make_preprocessor()),
            ("model", model),
        ]
    )


# ---------------------------------------------------------------------------
# Chronological split
# ---------------------------------------------------------------------------


def chronological_split(
    df: pd.DataFrame,
    test_size: float = 0.2,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series, pd.Series]:
    """Split the dataset chronologically without shuffling.

    Rows are ordered by the ``instant`` column (ascending row index in the UCI
    dataset). The last ``test_size`` fraction of rows becomes the test set.
    No random shuffling is performed.

    Args:
        df: The full hour.csv DataFrame (17,379 rows).
        test_size: Fraction of rows to hold out as the test set (default 0.2).

    Returns:
        Tuple of (X_train, X_test, y_train, y_test) as DataFrames/Series.
    """
    if not 0.0 < test_size < 1.0:
        raise ValueError(f"test_size must be in (0, 1), got {test_size}.")

    df_sorted = df.sort_values("instant").reset_index(drop=True)
    split_index = int(len(df_sorted) * (1.0 - test_size))

    train = df_sorted.iloc[:split_index]
    test = df_sorted.iloc[split_index:]

    X_train = train[FEATURE_COLS]
    X_test = test[FEATURE_COLS]
    y_train = train[TARGET_COL]
    y_test = test[TARGET_COL]

    return X_train, X_test, y_train, y_test
