# ML Results and Inference Contract

**Contract version:** 1.0  
**Model:** bike-demand-random-forest  
**Created:** 2026-11-25

---

## 1. Model Summary

Two models were trained and compared on a chronological hold-out test set.

| Model | MAE | RMSE | R² |
|---|---|---|---|
| Baseline (DummyRegressor, strategy=mean) | 174.98 | 232.61 | -0.113 |
| Random Forest (n_estimators=100, seed=42) | 45.02 | 69.62 | 0.900 |

The Random Forest reduces MAE by 74.3% relative to the baseline.

---

## 2. Data Split

- **Method:** Chronological (sort by `instant`, no shuffle)
- **Train rows:** 13,903 (first 80%)
- **Test rows:** 3,476 (last 20%)
- **Split index:** 13,903

Preprocessing (StandardScaler) was fitted on training data only.

---

## 3. Inference Contract

The UI Engineer must follow this contract exactly when calling the saved pipeline.

### 3.1 Artifact Location

```
modelling/artifacts/pipeline.joblib
```

Load with `joblib.load("modelling/artifacts/pipeline.joblib")`.

### 3.2 Input Features

Supply a pandas DataFrame (or dict converted to DataFrame) with **exactly these 12 columns in this order:**

| # | Column | dtype | Valid range | Description |
|---|---|---|---|---|
| 1 | `season` | int64 | 1–4 | 1=spring, 2=summer, 3=fall, 4=winter |
| 2 | `yr` | int64 | 0–1 | 0=2011, 1=2012 |
| 3 | `mnth` | int64 | 1–12 | Calendar month |
| 4 | `hr` | int64 | 0–23 | Hour of day |
| 5 | `holiday` | int64 | 0–1 | 0=no holiday, 1=holiday |
| 6 | `weekday` | int64 | 0–6 | 0=Sunday, 6=Saturday |
| 7 | `workingday` | int64 | 0–1 | 0=weekend/holiday, 1=working day |
| 8 | `weathersit` | int64 | 1–4 | 1=clear, 2=mist, 3=light rain/snow, 4=heavy rain/ice |
| 9 | `temp` | float64 | 0.0–1.0 | Normalized temperature (Celsius / 41) |
| 10 | `atemp` | float64 | 0.0–1.0 | Normalized apparent temperature (Celsius / 50) |
| 11 | `hum` | float64 | 0.0–1.0 | Normalized humidity (value / 100) |
| 12 | `windspeed` | float64 | 0.0–1.0 | Normalized wind speed (value / 67) |

**Do not include** `cnt`, `casual`, `registered`, `instant`, or `dteday`.

### 3.3 Preprocessing

StandardScaler is applied to all 12 features inside the pipeline.
**Do not scale inputs manually.** The pipeline handles all preprocessing.

### 3.4 Missing Values

The pipeline does not impute. All 12 features must be supplied for every row.

### 3.5 Output

| Field | Value |
|---|---|
| Type | float64 numpy array, shape (n_samples,) |
| Meaning | Predicted total bike rentals per hour (`cnt`) |
| Observed range (training data) | 1–977 |
| Note | Clip to 0 if needed for extreme out-of-range inputs |

### 3.6 Inference Example

```python
import joblib, pandas as pd

pipeline = joblib.load("modelling/artifacts/pipeline.joblib")

example = pd.DataFrame([{
    "season": 3, "yr": 1, "mnth": 9, "hr": 17,
    "holiday": 0, "weekday": 3, "workingday": 1,
    "weathersit": 1, "temp": 0.68, "atemp": 0.63,
    "hum": 0.55, "windspeed": 0.19
}])

predicted_cnt = pipeline.predict(example)[0]
# Expected: approximately 820.52
```

**Expected output:** `820.52` (predicted total rentals for that hour)

---

## 4. Figures

| Figure | Path |
|---|---|
| Feature importance (top 15) | `modelling/figures/feature_importance.png` |
| Actual vs predicted (test set) | `modelling/figures/actual_vs_predicted.png` |

Feature importances reflect the mean decrease in impurity and are **not causal evidence**.

---

## 5. Limitations

- The model was trained on 2011–2012 data from Washington D.C. It may not generalize to other cities or years.
- `yr` appears as a predictor; the model implicitly learns year-level growth trends that cannot extrapolate.
- Extreme weather conditions (weathersit=4) are rare in the training set; predictions there carry higher uncertainty.
- Predictions may be negative for inputs far outside training ranges; clip to 0 before display.
- Feature importances are not causal. High importance for `hr` reflects strong correlation with demand patterns, not a causal mechanism.

---

## 6. Reproducibility

Re-run training with:

```
uv run python src/modelling/train.py
```

Random seed 42 is set on `RandomForestRegressor`. The chronological split uses no randomness.
