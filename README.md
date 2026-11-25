# Bike Demand Investigation

How do time, season, weather, and environmental factors influence hourly
bike-sharing demand, and can we predict demand?

- Target: `cnt` (total hourly rentals)
- Excluded predictors (target leakage): `cnt`, `casual`, `registered`, `instant`
- Dataset: UCI Bike Sharing Dataset, hourly file `hour.csv`

## Environment setup

Python 3.12 managed with `uv` only (no pip, Conda, or Poetry).

```powershell
uv python pin 3.12
uv sync --extra ui --group dev
```

- Runtime dependencies: numpy, pandas, scikit-learn, matplotlib, seaborn, joblib
- Optional UI group (`ui`): streamlit
- Development group (`dev`): pytest

Run all project commands through `uv run`, for example `uv run pytest`.

## Dataset

- Location: `data/raw/hour.csv` (raw file, never modified)
- Source: https://archive.ics.uci.edu/dataset/275/bike-sharing-dataset
- Rows: 17,379 hourly records (plus header), 17 columns

## Project layout

```
src/data_pipeline/   dataset loading and structural validation
src/data_analysis/   exploratory analysis
src/models/          model training and inference
src/evaluation/      evaluation metrics
tests/               pytest suite
```

## Using the data pipeline

```python
from src.data_pipeline.load_data import load_hour_csv

df = load_hour_csv()  # defaults to data/raw/hour.csv
```

`load_hour_csv` raises `FileNotFoundError` when the file is missing and
`ValueError` when required columns are absent or `cnt` has nulls or negative
values.

## Running tests

```powershell
uv run pytest
```

## Notes

- Feature importance and correlations are not causal evidence.
- Models are CPU-based scikit-learn; no GPU acceleration is claimed.
