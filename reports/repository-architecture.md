# Repository Architecture

**Project:** Agentic Engineering — Bike Demand Investigation
**Owner:** repository-architect
**Run:** 2
**Date:** 2026-11-25

---

## 1. Intended Directory Tree

The tree below shows the full intended state of the repository once all agents have completed their deliverables. Directories and files marked `[exists]` are already present in the Phase 0 baseline. All others are created by the owning agent during their phase.

```
demo/
├── .claude/                                    [exists — do not modify]
│   ├── agents/                                 [exists — 9 agent definitions]
│   ├── hooks/
│   │   └── require-context7.py                 [exists]
│   └── settings.json                           [exists]
│
├── .gitignore                                  [exists]
├── .python-version                             [exists]
├── .venv/                                      [exists — project-setup owns; all agents use uv run]
├── CLAUDE.md                                   [exists — do not modify]
├── pyproject.toml                              [exists — Lead Agent authorizes changes]
├── README.md                                   [exists — repository-architect + project-setup]
├── uv.lock                                     [exists — project-setup owns]
│
├── artifacts/                                  [exists]
│   ├── context7-docs-evidence.json             [exists — documentation-researcher; do not modify]
│   ├── inference-contract.json                 [ml-engineer — must be fully populated in Run 2]
│   └── eda/                                    [data-scientist creates]
│       ├── summary_statistics.csv
│       ├── correlation_matrix.csv
│       └── demand_by_hour.csv
│
├── data/
│   ├── raw/                                    [exists — immutable; never modified]
│   │   ├── hour.csv                            [exists — 17379 rows, 17 cols; primary dataset]
│   │   ├── day.csv                             [exists — reference only]
│   │   └── Readme.txt                          [exists]
│   └── processed/                              [exists — reserved; not used in primary workflow]
│
├── app/                                        [inference-ui-builder creates]
│   ├── dashboard.py                            [inference-ui-builder — Streamlit entry point]
│   └── utils.py                                [inference-ui-builder — optional helper functions]
│
├── modelling/                                  [ml-engineer creates]
│   ├── artifacts/
│   │   └── pipeline.joblib                     [ml-engineer — serialized inference pipeline]
│   ├── figures/
│   │   ├── feature_importance.png              [ml-engineer]
│   │   └── actual_vs_predicted.png             [ml-engineer]
│   └── metrics.json                            [ml-engineer — MAE, RMSE, R² for both models]
│
├── notebooks/                                  [colab-notebook-engineer creates]
│   └── bike_demand_investigation.ipynb         [colab-notebook-engineer — Google Colab notebook]
│
├── reports/                                    [exists — repository-architect created]
│   ├── repository-architecture.md              [exists — this document; repository-architect]
│   ├── research-findings.md                    [research-agent]
│   ├── eda-findings.md                         [data-scientist]
│   └── qa-report.md                            [qa-auditor]
│
├── src/                                        [project-setup creates the package skeleton]
│   ├── data_pipeline/                          [project-setup owns]
│   │   ├── __init__.py
│   │   └── load.py                             [project-setup — reusable data loader]
│   ├── data_analysis/                          [data-scientist owns]
│   │   ├── __init__.py
│   │   └── eda.py                              [data-scientist — EDA functions]
│   ├── models/                                 [ml-engineer owns]
│   │   ├── __init__.py
│   │   └── train.py                            [ml-engineer — training script]
│   └── evaluation/                             [ml-engineer owns]
│       ├── __init__.py
│       └── evaluate.py                         [ml-engineer — metric computation]
│
└── tests/                                      [owners create their own test files]
    ├── __init__.py                             [project-setup]
    ├── test_load.py                            [project-setup — data loader tests]
    ├── test_eda.py                             [data-scientist — EDA function tests]
    └── test_models.py                          [ml-engineer — pipeline and metric tests]
```

---

## 2. Agent Ownership Table

| Agent | Owns | May Read | Must Not Modify |
|---|---|---|---|
| repository-architect | `reports/repository-architecture.md`, `README.md` (initial) | Entire repository | Everything else |
| project-setup | `.venv/`, `pyproject.toml`, `uv.lock`, `src/data_pipeline/`, `tests/__init__.py`, `tests/test_load.py`, `README.md` (environment section) | Entire repository | `data/raw/`, `.claude/`, `artifacts/context7-docs-evidence.json` |
| research-agent | `reports/research-findings.md` | `data/raw/Readme.txt`, `CLAUDE.md` | All source code, all artifacts |
| documentation-researcher | `artifacts/context7-docs-evidence.json` | Entire repository | All source code, models, data |
| data-scientist | `src/data_analysis/`, `tests/test_eda.py`, `artifacts/eda/`, `reports/eda-findings.md` | `data/raw/`, `src/data_pipeline/` | `data/raw/`, models, app, notebooks |
| ml-engineer | `src/models/`, `src/evaluation/`, `tests/test_models.py`, `modelling/`, `artifacts/inference-contract.json` | `data/raw/`, `src/data_pipeline/`, `artifacts/eda/` | `data/raw/`, app, notebooks, EDA outputs |
| colab-notebook-engineer | `notebooks/bike_demand_investigation.ipynb` | `src/`, `modelling/`, `artifacts/`, `data/raw/` | All Python source, model artifacts, data |
| inference-ui-builder | `app/` | `modelling/artifacts/pipeline.joblib`, `artifacts/inference-contract.json`, `src/data_pipeline/` | `data/raw/`, models, notebooks, tests |
| qa-auditor | `reports/qa-report.md` | Entire repository | Entire repository (read-only audit) |

---

## 3. File-Level Deliverables

### project-setup
- `src/data_pipeline/__init__.py` — package marker
- `src/data_pipeline/load.py` — `load_hour_data()` function; returns cleaned DataFrame with correct dtypes; excludes `instant`, `casual`, `registered` from modelling columns; validates row count (17379)
- `tests/__init__.py` — package marker
- `tests/test_load.py` — asserts row count, expected columns, no nulls, correct dtypes
- `.venv/` — created by `uv sync --group dev`; not committed
- `pyproject.toml`, `uv.lock` — environment lockfile

### research-agent
- `reports/research-findings.md` — dataset provenance, domain context (bike-sharing systems), column semantics, known limitations, data quality notes

### documentation-researcher
- `artifacts/context7-docs-evidence.json` — already verified for pandas, numpy, scikit-learn, matplotlib, seaborn; must not be regenerated unless a new library is added

### data-scientist
- `src/data_analysis/__init__.py` — package marker
- `src/data_analysis/eda.py` — functions for summary statistics, correlation matrix, demand-by-hour aggregation, and figure generation
- `artifacts/eda/summary_statistics.csv` — `df.describe()` output
- `artifacts/eda/correlation_matrix.csv` — Pearson correlation of numeric features
- `artifacts/eda/demand_by_hour.csv` — mean `cnt` grouped by `hr`
- `modelling/figures/eda_correlation_heatmap.png` — seaborn heatmap (saved here so ml-engineer and colab can reference figures from one location)
- `modelling/figures/eda_demand_by_hour.png` — bar/line chart of hourly demand profile
- `modelling/figures/eda_demand_by_season.png` — boxplot of `cnt` by `season`
- `reports/eda-findings.md` — written narrative of findings; references figures and CSVs; states correlations as associations, not causes
- `tests/test_eda.py` — tests for EDA functions (output shape, no empty DataFrames)

### ml-engineer
- `src/models/__init__.py` — package marker
- `src/models/train.py` — chronological train/test split; baseline LinearRegression and RandomForestRegressor pipelines; fit preprocessing on training data only; saves `pipeline.joblib`; excludes `cnt`, `casual`, `registered`, `instant` from features
- `src/evaluation/__init__.py` — package marker
- `src/evaluation/evaluate.py` — `evaluate_pipeline()` returning dict with `mae`, `rmse`, `r2`; uses `mean_absolute_error`, `root_mean_squared_error`, `r2_score`
- `modelling/artifacts/pipeline.joblib` — serialized scikit-learn Pipeline (best model) via joblib
- `modelling/metrics.json` — MAE, RMSE, R² for both baseline and Random Forest on the test split
- `modelling/figures/feature_importance.png` — bar chart of top-N feature importances from Random Forest
- `modelling/figures/actual_vs_predicted.png` — scatter plot of actual vs. predicted `cnt` on test set
- `artifacts/inference-contract.json` — fully populated; specifies input feature names and types, expected value ranges, output field (`predicted_cnt`), model name, pipeline path, evaluation metrics; Run 2 requirement: no null or placeholder values
- `tests/test_models.py` — tests that pipeline loads, predicts correct output shape, metrics meet minimum thresholds

### colab-notebook-engineer
- `notebooks/bike_demand_investigation.ipynb` — self-contained Google Colab notebook; installs dependencies via `!pip install`; loads `hour.csv` from Google Drive or direct URL; reproduces EDA, training, and evaluation cells; references findings from `reports/`; suitable for public sharing

### inference-ui-builder
- `app/dashboard.py` — Streamlit entry point; loads `modelling/artifacts/pipeline.joblib`; reads `artifacts/inference-contract.json` for input schema; exposes sliders/selectors for all model features; displays predicted demand
- `app/utils.py` — optional; input validation helpers if needed; must not duplicate `src/data_pipeline/load.py`

### qa-auditor
- `reports/qa-report.md` — independent audit findings; checks for target leakage, chronological split, preprocessing fit scope, metric completeness, test coverage, file presence, notebook reproducibility, inference-contract completeness

---

## 4. Data Flow

```
data/raw/hour.csv  (immutable)
        |
        v
src/data_pipeline/load.py         [project-setup]
        |
        +-----> src/data_analysis/eda.py -----> artifacts/eda/*.csv
        |                                  \--> modelling/figures/eda_*.png
        |                                  \--> reports/eda-findings.md
        |
        +-----> src/models/train.py
                     |
                     +-----> src/evaluation/evaluate.py
                     |               |
                     |               v
                     |       modelling/metrics.json
                     |
                     +-----> modelling/artifacts/pipeline.joblib
                     |
                     +-----> modelling/figures/feature_importance.png
                     +-----> modelling/figures/actual_vs_predicted.png
                     |
                     v
             artifacts/inference-contract.json
                     |
                     v
              app/dashboard.py  [inference-ui-builder]
                     |
                     v
           Streamlit local web UI


notebooks/bike_demand_investigation.ipynb  [colab-notebook-engineer]
  reads from: data/raw/hour.csv, modelling/, artifacts/, reports/
  reproduces: EDA + training + evaluation inline
```

---

## 5. Naming Conventions

| Concern | Convention | Example |
|---|---|---|
| Python modules | `snake_case` | `load.py`, `train.py`, `evaluate.py` |
| Python packages | `snake_case` | `data_pipeline`, `data_analysis` |
| Test files | `test_<module>.py` | `test_load.py` |
| Figure files | `<phase>_<description>.png` | `eda_correlation_heatmap.png`, `feature_importance.png` |
| Artifact files | `<name>.json` | `inference-contract.json` |
| Model files | `pipeline.joblib` | (fixed name; inference contract references it) |
| Metrics file | `metrics.json` | (single file; both models' metrics inside) |
| Report files | `<topic>-findings.md`, `<topic>-report.md` | `eda-findings.md`, `qa-report.md` |
| Notebook | `bike_demand_investigation.ipynb` | (single notebook; fixed name) |

---

## 6. Boundaries

### What agents MUST NOT do

- **Any agent:** modify `data/raw/` contents.
- **Any agent:** modify `artifacts/context7-docs-evidence.json` unless explicitly authorized to add a new library entry.
- **Any agent:** modify `.claude/` configuration.
- **Any agent:** modify `pyproject.toml` or run `uv sync`/`uv lock` without Lead Agent authorization.
- **Any agent:** create directories without a deliverable file inside them.
- **Any agent:** create duplicate implementations (e.g., a second data loader in `app/`).
- **Any agent:** pre-fabricate metrics, test results, or model outputs.
- **Any agent except project-setup:** run `uv sync`, `uv lock`, `uv add`.
- **ml-engineer:** include `cnt`, `casual`, `registered`, or `instant` as model features.
- **ml-engineer:** shuffle data before splitting (chronological split required).
- **ml-engineer:** fit any preprocessor on the full dataset before splitting.
- **ml-engineer in Run 2:** leave `artifacts/inference-contract.json` with null or placeholder values.
- **colab-notebook-engineer:** import from `src/` directly (Colab installs dependencies independently; it must be self-contained).
- **inference-ui-builder:** install dependencies independently (Lead Agent authorizes `uv sync --extra ui --group dev` via project-setup).
- **qa-auditor:** modify any file (read-only audit).

### What agents MAY do without additional authorization

- **Any agent:** read any file in the repository.
- **Any agent:** create files within their owned directories.
- **Any agent:** create `__init__.py` files within their owned package directories.
- **data-scientist:** write figures to `modelling/figures/` (EDA figures go there for colocation with model figures).
- **ml-engineer:** write figures to `modelling/figures/`.
- **Any agent:** run `uv run pytest tests/` to verify tests pass.

---

## 7. Run 2 Specific Requirements

The following items were gaps in Run 1 and must be fully resolved in Run 2:

1. **`artifacts/inference-contract.json`** must be completely populated by ml-engineer with:
   - `model_name` — string identifier of the best model
   - `pipeline_path` — relative path to `modelling/artifacts/pipeline.joblib`
   - `feature_names` — list of all input feature column names (in order)
   - `feature_dtypes` — dict mapping feature name to dtype string
   - `feature_ranges` — dict mapping feature name to `{min, max}` values from training data
   - `target` — `"cnt"`
   - `metrics` — MAE, RMSE, R² on the test split
   - `train_split_cutoff_index` — integer row index where train ends and test begins
   - `created_at` — ISO 8601 timestamp

2. **All tests must pass** under `uv run pytest tests/` before the qa-auditor runs.

3. **EDA findings** must reference actual computed statistics from `artifacts/eda/*.csv`, not invented values.

---

## 8. Component Dependencies

| Component | Depends On |
|---|---|
| `src/data_analysis/eda.py` | `src/data_pipeline/load.py` |
| `src/models/train.py` | `src/data_pipeline/load.py` |
| `src/evaluation/evaluate.py` | (standalone; called from `train.py`) |
| `modelling/artifacts/pipeline.joblib` | `src/models/train.py` |
| `modelling/metrics.json` | `src/evaluation/evaluate.py` |
| `artifacts/inference-contract.json` | `modelling/artifacts/pipeline.joblib`, `modelling/metrics.json` |
| `app/dashboard.py` | `modelling/artifacts/pipeline.joblib`, `artifacts/inference-contract.json` |
| `notebooks/bike_demand_investigation.ipynb` | `data/raw/hour.csv`, `modelling/`, `artifacts/`, `reports/` |
| `reports/qa-report.md` | All deliverables above |

---

## 9. Minimal Implementation Approach

This project is intentionally lightweight. The following abstractions are excluded:

- No backend services, databases, Docker, or cloud infrastructure.
- No feature store or data versioning system.
- No model registry beyond `modelling/artifacts/`.
- No logging framework (print statements are acceptable for scripts).
- No configuration management beyond `pyproject.toml`.
- No async or streaming inference.
- `data/processed/` exists in the baseline but is not used; agents do not write to it.

The `src/` layout uses flat modules (one file per concern) rather than deep package hierarchies. This keeps imports readable and the codebase navigable by all agents.
