# Post-Run 2 Evidence Review

**Date:** 2026-11-25  
**Reviewer:** Lead Agent (independent verification)  
**Run 2 verdict (from QA Auditor):** PASS WITH LIMITATIONS  
**Purpose:** Strengthen experimental credibility — not to manufacture a perfect result.

---

## Classification Key

| Label | Meaning |
|---|---|
| **Verified** | Independently confirmed in this review session |
| **Partially verified** | Evidence exists but is incomplete or indirect |
| **Not verified** | Cannot be confirmed without external access or a live test not performed |
| **Blocked** | Environment constraint prevents verification |

---

## 1. Streamlit Verification

### What was tested

The UI builder (port 8502) and QA auditor (port 8503) each launched the app independently:

```
# UI builder test (reports/ui-verification.md):
uv run streamlit run app/app.py --server.headless true --server.port 8502

# QA auditor test (reports/qa-report.md):
uv run streamlit run app/app.py --server.headless true --server.port 8503
```

Both tests were performed in separate background processes during their respective phases.

### Evidence available

| Evidence item | Classification | Detail |
|---|---|---|
| `app/app.py` is a genuine Streamlit app | **Verified** | Code inspection: `import streamlit as st`, `st.set_page_config`, `st.title`, `st.sidebar`, `st.button`, `@st.cache_resource`, `st.metric` — 388 lines, all Streamlit idioms, no mock or stub code |
| Uvicorn server started | **Verified** | UI builder stdout: `2026-11-25 19:40:03.171 Uvicorn server started on :::8502` and `You can now view your Streamlit app in your browser.` Streamlit exclusively uses Uvicorn; this message is emitted only after the HTTP server accepts connections |
| Port confirmed in use during test | **Verified** | UI builder: `netstat -ano` showed port 8502 LISTENING. QA auditor: `netstat -ano` showed `TCP 0.0.0.0:8503 LISTENING`. Port 8503 is free now (confirmed in this session), consistent with the process being killed after each test |
| Two independent launches | **Verified** | UI builder used port 8502; QA auditor used port 8503 without prior knowledge of the UI builder's port choice — both succeeded |
| HTTP response body verified | **Not verified** | No `curl http://localhost:850x/` or equivalent request was made during either test. Uvicorn started = HTTP server is accepting connections, but no HTTP response body was captured to confirm the Streamlit page loaded |
| Prediction produced through UI | **Not verified** | No browser-based test was performed. The browser extension was not connected during Run 2. The predict pathway exists in code and passes all automated tests, but end-to-end browser interaction is unconfirmed |

### Confidence level

The Streamlit process starts and the HTTP server binds correctly. What remains unverified is the response body and browser-side rendering. The automated tests (`test_inference.py`) confirm the prediction logic independently of the UI.

### Steps to close the gap

A human with the project cloned can complete the browser verification:
```
cd c:\Users\M.Faisal\Desktop\bike-demand-test\demo
uv run streamlit run app/app.py
# Open http://localhost:8501 in a browser
# Set any input values, click Predict, confirm a prediction appears
```

---

## 2. Inference Contract

### Feature ordering consistency

All three sources define the same 12 features in identical order:

```
Contract (artifacts/inference-contract.json)   → feature_names
Pipeline module (src/modelling/pipeline.py)    → FEATURE_COLS
App (app/app.py)                               → FEATURE_ORDER

Result: ALL MATCH (verified programmatically in this session)
Order: season, yr, mnth, hr, holiday, weekday, workingday, weathersit,
       temp, atemp, hum, windspeed
```

### Contract field-by-field verification

| Field | Classification | Detail |
|---|---|---|
| `contract_version` | **Verified** | "1.0" |
| `feature_names` (12 entries) | **Verified** | Exact match with pipeline and app |
| `feature_count` | **Verified** | 12 |
| `feature_dtypes` | **Verified** | int64 for 8 categorical/ordinal features; float64 for temp, atemp, hum, windspeed |
| `feature_ranges` | **Verified** | All 12 entries populated with min, max, description |
| Normalization descriptions | **Verified** | temp ÷41, atemp ÷50, hum ÷100, windspeed ÷67 — consistent with Readme.txt |
| `preprocessing.note` | **Verified** | "scaling is embedded in pipeline.joblib — do not scale inputs manually" — correct; ColumnTransformer + StandardScaler is step 1 of the pipeline |
| `train_split_cutoff_index` | **Verified** | 13903 — matches train.py output (13,903 / 3,476 split) |
| `metrics.*` | **Verified** | Retraining produces identical values: MAE=45.0211, RMSE=69.6241, R²=0.9003 |
| `inference_example.predicted_cnt` | **Verified** | 820.52 — confirmed by live pipeline.predict() in Phase 5, Phase 7, and during this session's retrain (contract rewritten by train.py with same value) |
| Leakage exclusion | **Verified** | `casual`, `registered`, `instant` absent from `feature_names` |
| Null fields | **Verified** | 0 null top-level fields (confirmed in Phase 5 and Phase 7) |

### Preprocessing consistency

The app passes a 1-row DataFrame in `FEATURE_ORDER` to `pipeline.predict()` without any manual scaling. The pipeline's first step is `ColumnTransformer(StandardScaler on all 12 features)`. This is consistent with the contract's preprocessing note and the pipeline module's `make_preprocessor()` definition.

No inconsistency found.

---

## 3. Reproducibility Evidence

### Dataset

| Item | Value | Classification |
|---|---|---|
| File | `data/raw/hour.csv` | **Verified** |
| SHA-256 | `e03de4ee4ef4dc376ac6e04bf829673c6269e8eba5c60fa121640fa2f829504f` | **Verified** |
| Size | 1,156,736 bytes | **Verified** |
| Rows × Cols | 17,379 × 17 | **Verified** |
| Missing values | 0 | **Verified** |
| `cnt == casual + registered` | True on all rows | **Verified** (Phase 2 test, Phase 7 audit) |

The dataset SHA-256 is internally consistent across this session and the Phase 2 project-setup report (`e03de4ee4ef...`). No published checksum from UCI is available to compare against.

### Environment

| Item | Value | Classification |
|---|---|---|
| Python | 3.12.16 | **Verified** |
| uv | 0.13.7 | **Verified** |
| `uv lock --check` | Resolved 53 packages | **Verified** |
| uv.lock SHA-256 | `8f44ee516a29139eff9448dbe3c67566cbd87512199b1c90fb3e276c4d6db7fe` | **Verified** |
| numpy | 2.4.6 | **Verified** |
| pandas | 2.3.3 | **Verified** |
| scikit-learn | 1.8.0 | **Verified** |
| streamlit | 1.67.0 | **Verified** |
| joblib | 1.6.0 | **Verified** |

### Training configuration

| Item | Value | Classification |
|---|---|---|
| Random seed | `random_state=42` (via `RANDOM_SEED` constant in `pipeline.py`, passed explicitly in `train.py`) | **Verified** |
| Algorithm | `RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1)` | **Verified** |
| Split | Chronological, sort by `instant`, no shuffle, test_size=0.2 | **Verified** |
| Preprocessing | `StandardScaler` on all 12 features, fitted on training data only | **Verified** |

### Deterministic retraining

Retraining was executed in this review session (`uv run python src/modelling/train.py`).

| Metric | Original (Phase 5) | Retrain (this session) | Match |
|---|---|---|---|
| Baseline MAE | 174.9846 | 174.9846 | ✅ |
| RF MAE | 45.0211 | 45.0211 | ✅ |
| RF RMSE | 69.6241 | 69.6241 | ✅ |
| RF R² | 0.9003 | 0.9003 | ✅ |
| Inference example output | 820.52 | 820.52 | ✅ |

**pipeline.joblib SHA-256 before retrain:** `73ad7db16e4e5a4c473d145a5a2bdd35068fdf6389e7caad120fecdf9872a834`  
**pipeline.joblib SHA-256 after retrain:** `73ad7db16e4e5a4c473d145a5a2bdd35068fdf6389e7caad120fecdf9872a834`

**Verdict: byte-for-byte deterministic.** The same code, data, and seed produce an identical binary artifact.

### Code vs artifact reproducibility

| Type | Status |
|---|---|
| Code reproducibility (same metrics each run) | **Verified** — metrics match to 4 decimal places |
| Byte-for-byte artifact reproducibility | **Verified** — identical SHA-256 on retrain |

Note: byte-for-byte reproducibility is not guaranteed in general for scikit-learn Random Forests (it depends on joblib serialization format, numpy version, and platform). It holds here because the environment is locked (`uv.lock`) and the platform is the same machine.

---

## 4. Colab Limitation

### Exact reason execution was blocked

Google Colab requires an interactive browser-based OAuth 2.0 flow to authenticate a Google account before a runtime can be allocated. This flow cannot be initiated from a non-interactive CLI environment (no browser, no interactive stdin). No Colab API or CLI alternative was available in this session.

This is an environment constraint, not a defect in the notebook.

### What was verified without Colab access

| Item | Classification | Detail |
|---|---|---|
| Notebook parses as valid JSON | **Verified** | Python `json.load()` succeeded |
| nbformat version | **Verified** | 4.5 |
| Total cells | **Verified** | 37 (19 code, 18 markdown) |
| No local file paths | **Verified** | No `c:\Users`, `Desktop`, or other machine-specific paths in any cell source |
| No fabricated execution outputs | **Verified** | All code cells have `outputs: []` and `execution_count: null` |
| UCI download URL present | **Verified** | `uci.edu` URL found in cell source |
| Metrics match verified values | **Verified** | Hardcoded metrics in markdown cells (MAE=45.02, R²=0.90, etc.) match `modelling/metrics.json` |
| `np.sqrt(mean_squared_error(...))` used for RMSE | **Verified** | Avoids `root_mean_squared_error` (sklearn ≥1.4 only) for Colab compatibility |
| `%matplotlib inline` used (not `Agg`) | **Verified** | Correct for Colab's interactive environment |

### Steps for a human to complete notebook verification in Colab

1. Open Google Colab: https://colab.research.google.com
2. Upload `notebooks/bike_demand_investigation.ipynb` via File → Upload notebook
3. Click Runtime → Run all (or Ctrl+F9)
4. The setup cell will download `Bike-Sharing-Dataset.zip` from UCI and extract `hour.csv` automatically
5. If the UCI URL is unavailable, uncomment the `google.colab.files.upload()` fallback and upload `data/raw/hour.csv` manually
6. Verify: all cells execute without error, visualizations render, the model metrics table shows MAE≈45, R²≈0.90, and the comparison table prints

---

## 5. Summary Table — All Items

| # | Item | Classification |
|---|---|---|
| S1 | Streamlit app.py is a genuine Streamlit application | **Verified** |
| S2 | Uvicorn server started on port 8502 (UI builder) | **Verified** |
| S3 | Uvicorn server started on port 8503 (QA auditor) | **Verified** |
| S4 | Port confirmed in use during each test via netstat | **Verified** |
| S5 | HTTP response body from Streamlit page | **Not verified** |
| S6 | End-to-end prediction through browser UI | **Not verified** |
| I1 | Feature order: contract == pipeline == app | **Verified** |
| I2 | Normalization descriptions correct (÷41, ÷50, ÷100, ÷67) | **Verified** |
| I3 | Preprocessing note accurate (scaling in pipeline, no manual scaling needed) | **Verified** |
| I4 | Leakage exclusions in contract (no casual/registered/instant) | **Verified** |
| I5 | Inference example (820.52) live-validated | **Verified** |
| I6 | All contract fields non-null | **Verified** |
| R1 | Dataset SHA-256 | **Verified** |
| R2 | uv.lock SHA-256 and consistency | **Verified** |
| R3 | Python and all library versions | **Verified** |
| R4 | Training random seed documented and used | **Verified** |
| R5 | Training configuration (n_estimators, split method) | **Verified** |
| R6 | Deterministic retraining (metrics match) | **Verified** |
| R7 | Byte-for-byte artifact reproducibility (SHA-256 match after retrain) | **Verified** |
| R8 | Dataset integrity vs published UCI checksum | **Not verified** (UCI does not publish a checksum) |
| C1 | Colab block reason documented | **Verified** |
| C2 | Notebook structural validity (JSON, nbformat 4.5) | **Verified** |
| C3 | No local paths in notebook | **Verified** |
| C4 | No fabricated outputs | **Verified** |
| C5 | Metrics in notebook match computed artifacts | **Verified** |
| C6 | Notebook executed in Colab top-to-bottom | **Blocked** |

---

## 6. Items Requiring Disclosure in Run 2 Verdict

The following items are not defects but should be disclosed when reporting results:

1. **Streamlit browser test not performed.** The app starts and the HTTP server binds, but no browser-based smoke test was run. Automated tests confirm prediction logic.

2. **Colab notebook unexecuted.** The notebook is structurally complete and ready to run, but no execution evidence (cell outputs) was captured in this environment.

3. **Dataset SHA-256 not cross-validated against UCI.** The UCI dataset page does not publish an official checksum. The internal SHA-256 is consistent across all sessions but cannot be compared to an external reference.

4. **Byte-for-byte reproducibility is platform-specific.** The identical pipeline artifact checksum holds on the same machine with the same locked environment. A different machine, OS, or even a different joblib version may produce a different binary while producing the same numeric predictions.

---

*This review was conducted without modifying any implementation files, altering Git history, or changing the Run 2 verdict. The existing verdict of PASS WITH LIMITATIONS remains appropriate given items S5, S6, and C6.*
