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
src/modelling/       model pipeline and training/evaluation
tests/               pytest suite
```

## Using the data pipeline

```python
from src.data_pipeline.load import load_hour_csv

df = load_hour_csv()  # defaults to data/raw/hour.csv
```

`load_hour_csv` raises `FileNotFoundError` when the file is missing and
`ValueError` when the file cannot be parsed or its row count, column count,
or required columns do not match the UCI hourly dataset.

## Running tests

```powershell
uv run pytest
```

## Running the inference app

**Prerequisites:**

- Environment installed with the `ui` extra (see [Environment setup](#environment-setup)).
- Model artifact present at `modelling/artifacts/pipeline.joblib` (produced by the ML training step).

**Launch:**

```powershell
uv run streamlit run app/app.py
```

The app opens at **http://localhost:8501** in your browser.

**What it does:**

Adjust the sidebar inputs — hour, season, weather conditions, and normalized environmental readings — then click **Predict Demand**. The app runs the trained Random Forest pipeline and displays the predicted hourly rental count.

| Input group | Features |
|---|---|
| Time | Hour of day, year, month, day of week, holiday, working day |
| Season & weather | Season, weather situation |
| Environment | Temperature, apparent temperature, humidity, wind speed (all normalized 0–1) |

Temperature, apparent temperature, humidity, and wind speed must be supplied pre-normalized (divide by 41, 50, 100, and 67 respectively).

**Stop the server:** `Ctrl+C` in the terminal where it is running.

## Agents

| Agent | Responsibility |
|---|---|
| repository-architect | Repository structure and boundaries |
| project-setup | Python environment, dependencies, dataset, data loading |
| research-agent | Dataset/domain research |
| documentation-researcher | Context7 documentation evidence |
| data-scientist | Exploratory data analysis |
| ml-engineer | Model training, evaluation, artifacts, inference contract |
| colab-notebook-engineer | Google Colab notebook |
| inference-ui-builder | Streamlit application |
| qa-auditor | Independent quality audit |
| git-supervisor | Version control hygiene, pre-commit checks, PR coordination |
| ui-launcher | Launch the inference web app after qa-auditor PASS; verify and report URL |

Agent definitions live in `.claude/agents/`. The Lead Agent coordinates; specialist agents own their implementation boundaries and must not modify files owned by another agent without explicit authorization.

Invocation order: `repository-architect → project-setup → research-agent → documentation-researcher → data-scientist → ml-engineer → colab-notebook-engineer → inference-ui-builder → qa-auditor → ui-launcher`. `git-supervisor` runs before every commit.

## Notes

- Feature importance and correlations are not causal evidence.
- Models are CPU-based scikit-learn; no GPU acceleration is claimed.
