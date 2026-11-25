# Setup Verification (Project Setup Agent)

Project root: `c:\Users\M.Faisal\Desktop\bike-demand-test\demo`
Git baseline: `fb7bad8`

## 1. Environment

| Check | Command | Result |
|---|---|---|
| uv version | `uv --version` | uv 0.13.7 |
| Lock validity | `uv lock --check` | PASS (Resolved 53 packages, exit 0) |
| Python version | `uv run python -c "import sys; print(sys.version)"` | 3.12.16 (`.venv\Scripts\python.exe`) |
| Pinned Python | `.python-version` | `3.12` |

Imports and versions, from `uv run python`:

| Library | Version |
|---|---|
| numpy | 2.4.6 |
| pandas | 2.3.3 |
| scikit-learn | 1.8.0 |
| matplotlib | 3.11.2 |
| seaborn | 0.13.2 |
| joblib | 1.6.0 |
| streamlit | 1.67.0 |

All seven imports succeeded. The existing `.venv` was not recreated, and no `uv sync`, `uv add`, `uv lock`, or cache-clearing command was run. `pyproject.toml` and `uv.lock` were not modified.

## 2. Dataset Integrity

File: `data/raw/hour.csv`

| Check | Result |
|---|---|
| Shape | 17,379 rows x 17 columns (PASS) |
| Missing values | 0 (PASS) |
| Duplicate `instant` | 0 (PASS) |
| `instant` range | 1 to 17,379 |
| `dteday` range | 2011-01-01 to 2012-12-31 |
| `cnt` range | 1 to 977 (all non-negative) |
| Sum of `cnt` | 3,292,679 |
| `cnt == casual + registered` | True for all rows |
| SHA-256 | `e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f` |

The SHA-256 is recorded for reproducibility. It was not compared against a published checksum, because none was checked in this run. The file was only read and never modified. `git status` shows no change under `data/raw/`.

## 3. Code Delivered

- `src/__init__.py`, `src/data_pipeline/__init__.py`, `tests/__init__.py` (empty package markers)
- `src/data_pipeline/load.py`: `load_hour_csv(path="data/raw/hour.csv") -> pd.DataFrame`, `validate_hour_frame(df)`, plus the `REQUIRED_COLUMNS`, `EXPECTED_ROWS`, and `EXPECTED_COLUMNS` constants. Missing paths raise `FileNotFoundError`. Structural failures (row count, column count, missing required columns, unparseable CSV) raise `ValueError`. Columns are not dropped or altered.
- `tests/test_load.py`

## 4. Test Run

Command: `uv run pytest tests/test_load.py -v`

```
collected 11 items
tests/test_load.py::test_load_returns_dataframe PASSED
tests/test_load.py::test_load_row_count PASSED
tests/test_load.py::test_load_column_count PASSED
tests/test_load.py::test_load_required_columns PASSED
tests/test_load.py::test_target_column_nonnegative PASSED
tests/test_load.py::test_no_leaked_columns_excluded PASSED
tests/test_load.py::test_no_missing_values PASSED
tests/test_load.py::test_cnt_equals_casual_plus_registered PASSED
tests/test_load.py::test_missing_path_raises_file_not_found PASSED
tests/test_load.py::test_wrong_structure_raises_value_error PASSED
tests/test_load.py::test_missing_required_column_raises_value_error PASSED
11 passed in 0.82s
```

Result: 11 passed, 0 failed.

## 5. Context7 Gate

`artifacts/context7-docs-evidence.json` was read and not modified. It records pandas `read_csv` and `DataFrame` usage as verified, which covers the APIs used in `load.py`.

## 6. Issues and Notes

- The task named `tests/test_load.py`, while the project role file lists `tests/test_data_loading.py` as the owned test path. This run followed the task's `tests/test_load.py`. The Lead Agent should confirm the name.
- `README.md` and `.gitignore` are in the project-setup ownership list but were not part of this task and were not changed.
- The default path `data/raw/hour.csv` is relative to the working directory. Run commands from the project root, or pass an absolute path. The tests resolve the path from the test file location.
