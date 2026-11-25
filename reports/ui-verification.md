# UI Verification Report

**Agent:** inference-ui-builder  
**Date:** 2026-11-25  
**Run:** 2  

---

## App File

- Created: `app/app.py`
- Supporting module: `app/__init__.py`

---

## Features Implemented (12 sidebar inputs)

All 12 input features from the inference contract are present in the sidebar.

| # | Feature | Widget | Range / Options |
|---|---------|--------|-----------------|
| 1 | `season` | selectbox (Spring/Summer/Fall/Winter) | 1–4 |
| 2 | `yr` | selectbox (2011/2012) | 0–1 |
| 3 | `mnth` | selectbox (January…December) | 1–12 |
| 4 | `hr` | slider | 0–23 |
| 5 | `holiday` | selectbox (No/Yes) | 0–1 |
| 6 | `weekday` | selectbox (Sunday…Saturday) | 0–6 |
| 7 | `workingday` | selectbox (No/Yes) | 0–1 |
| 8 | `weathersit` | selectbox (Clear/Mist/Light Rain/Heavy Rain) | 1–4 |
| 9 | `temp` | slider (normalized, 0–1) | 0.0–1.0 |
| 10 | `atemp` | slider (normalized, 0–1) | 0.0–1.0 |
| 11 | `hum` | slider (normalized, 0–1) | 0.0–1.0 |
| 12 | `windspeed` | slider (normalized, 0–1) | 0.0–1.0 |

The excluded columns `cnt`, `casual`, `registered`, and `instant` are not exposed.

---

## Pipeline Loading

- Loaded via `@st.cache_resource` at startup.
- Path resolved relative to `app.py`: `modelling/artifacts/pipeline.joblib`.
- Inputs passed directly as a 1-row DataFrame in the contract's feature order — no manual pre-scaling.
- Missing artifact produces a clear `st.error()` message; the Predict button is disabled.

---

## Streamlit Launch Verification

**Command tested:**
```
uv run streamlit run app/app.py --server.headless true --server.port 8502
```

**Result: STARTED SUCCESSFULLY**

Evidence from stdout:
```
2026-11-25 19:40:03.171 Uvicorn server started on :::8502

  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8502
  Network URL: http://192.168.0.200:8502
  External URL: http://105.112.118.235:8502
```

Port 8502 confirmed in use via `netstat`. Process cleaned up after verification.

---

## Test Results

Command: `uv run pytest tests/ -v`

```
39 passed in 4.80s
```

### test_inference.py results (12 tests)

| Test | Result |
|------|--------|
| test_pipeline_loads | PASSED |
| test_prediction_from_contract_example | PASSED |
| test_app_file_exists | PASSED |
| test_app_imports_streamlit | PASSED |
| test_valid_inputs_pass_validation | PASSED |
| test_invalid_hour_fails_validation | PASSED |
| test_invalid_temp_fails_validation | PASSED |
| test_invalid_season_fails_validation | PASSED |
| test_feature_order_matches_contract | PASSED |
| test_prediction_output_is_float | PASSED |
| test_prediction_output_in_reasonable_range | PASSED |
| test_missing_pipeline_raises_error | PASSED |

All prior tests (test_eda.py: 5, test_load.py: 9, test_ml.py: 13) continue to pass.

---

## Known Limitations

- The model was trained on 2011–2012 Washington D.C. Capital Bikeshare data only.
- Predictions on inputs outside the training distribution are unreliable.
- Normalized temperature, humidity, and wind speed must be supplied as fractions (0–1); the UI converts display values back to this scale.
- The model assumes stable demand patterns; infrastructure changes or policy shifts are not captured.
- Feature correlations and importances are not causal evidence.
