# Project: Agentic Engineering — Bike Demand Investigation

## Purpose

Build a reproducible data science project demonstrating how multiple AI agents collaborate through an engineering workflow.

**Research question:** How do time, season, weather, and environmental factors influence hourly bike-sharing demand, and can we predict demand?

**Dataset:** UCI Bike Sharing Dataset, `hour.csv`.

**Target:** `cnt`.

The project includes data analysis, machine learning, a Google Colab notebook, and a local Streamlit inference application.

---

## Engineering Rules

1. Inspect the repository before modifying it.
2. Follow the assigned agent's ownership boundaries.
3. Use Context7-verified documentation before implementation.
4. Do not fabricate data, metrics, test results, sources, or completion.
5. Keep implementation simple, reproducible, and demonstrable.
6. Never modify raw datasets.
7. Do not introduce unnecessary infrastructure or dependencies.
8. Do not mark a task complete without verifying it.
9. Report blockers immediately rather than silently bypassing requirements.
10. The Lead Agent coordinates; specialist agents own implementation.

## Python Environment

Use `uv` exclusively.

Prohibited:

- `pip`
- `python -m pip`
- `uv pip`
- Conda
- Poetry

Use `uv run` for Python execution and testing.

Python version: 3.12.

Required dependencies:

- numpy
- pandas
- scikit-learn
- matplotlib
- seaborn
- joblib

Development dependency:

- pytest

Optional UI dependency:

- streamlit

Do not add TensorFlow, PyTorch, CUDA, Jupyter, or unnecessary packages.

Google Colab is used for the notebook.

## Shared Environment Ownership

The `.venv` is a shared project resource. Only the project-setup agent creates it and runs `uv sync` or `uv lock`.

All other agents use `uv run` to execute commands within the existing environment. No specialist agent may independently run `uv sync`, `uv lock`, or `uv add` without explicit Lead Agent authorization.

**Cache and environment protection — the following operations are prohibited without explicit Lead Agent authorization and a documented technical reason:**

- `uv sync --no-cache`
- `uv lock --no-cache`
- `--reinstall` flags
- Deleting `.venv`
- Clearing the UV wheel cache
- Deleting cache lock files without first confirming the holding process has exited

**UI extra installation (Phase 6 only):** When the inference-ui-builder is ready to test the Streamlit application, the Lead Agent authorizes project-setup to run `uv sync --extra ui --group dev` once. The inference-ui-builder must not install dependencies independently.

**Additional dependencies:** Any new dependency must be declared in `pyproject.toml`, approved by the Lead Agent, and installed by running `uv sync` once. No agent may `uv add` packages without Lead Agent approval.

## Dataset

The dataset must be staged at:

`data/raw/hour.csv`

Official source:

https://archive.ics.uci.edu/dataset/275/bike-sharing-dataset

Raw data is immutable.

Do not silently replace missing data with another dataset.

## ML Safeguards

Target:

`cnt`

Exclude these predictors:

- `cnt`
- `casual`
- `registered`
- `instant`

`casual` and `registered` directly contribute to `cnt` and cause target leakage.

Use a chronological train/test split.

Fit preprocessing on training data only.

Compare:

- Baseline regression.
- Random Forest regression.

Evaluate using:

- MAE
- RMSE
- R²

Feature importance and correlations must not be presented as causal evidence.

The primary models are CPU-based scikit-learn models. Do not claim GPU acceleration.

## Context7 Documentation Gate

Before implementation code is written:

1. The Documentation Researcher must verify relevant official documentation using Context7.
2. Documentation evidence must be recorded in `artifacts/context7-docs-evidence.json`.
3. Required documentation must be verified.
4. The Lead Agent must confirm the gate is satisfied.

The PreToolUse hook in `.claude/settings.json` must enforce the gate for Write/Edit operations where applicable.

The hook is a workflow safeguard, not a complete security boundary. Do not claim that every possible write mechanism is blocked.

If Context7 is unavailable, report the blocker. Do not fabricate evidence or bypass the gate.

## Repository Structure

Follow the approved structure documented in:

`reports/repository-architecture.md`

Do not create unnecessary directories or duplicate existing files.

## Agent Ownership

| Agent | Primary responsibility |
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

Specialist agents must not modify files owned by another agent without explicit authorization.

## Deliverables

- Reproducible Python environment.
- Verified dataset.
- Reusable data loading.
- Exploratory analysis.
- Baseline and Random Forest models.
- Evaluation metrics and visualizations.
- Saved inference pipeline.
- Google Colab notebook.
- Local Streamlit dashboard.
- Tests.
- Research documentation.
- QA report.
- README.

## Completion

The Lead Agent must verify the deliverables, run applicable tests, resolve QA findings, and produce a final status report.

A task is complete only when the implementation exists and its verification evidence is available.
