# EDA Findings: Hourly Bike-Sharing Demand

**Research question:** How do time, season, weather, and other environmental factors
relate to hourly bike-sharing demand, and how useful are these variables for
predicting demand?

**Dataset:** UCI Bike Sharing Dataset — `data/raw/hour.csv`

---

## 1. Dataset Summary

| Property | Value |
|---|---|
| Rows | 17,379 |
| Columns | 17 |
| Temporal coverage | 2011–2012 (2 full years) |
| Target variable | `cnt` (total hourly rentals) |
| Usable predictors | season, yr, mnth, hr, holiday, weekday, workingday, weathersit, temp, atemp, hum, windspeed |

---

## 2. Data Quality

- **Missing values:** 0 across all 17 columns.
- **Duplicate rows:** 0.
- **Data types:** 13 integer columns, 3 float columns (`temp`, `atemp`, `hum`, `windspeed`), 1 object (`dteday`).
- `dteday` is a string date column; temporal information is fully captured by `yr`, `mnth`, and `hr`.
- `casual` and `registered` are excluded from predictor analysis — they sum to `cnt` and cause target leakage.
- `instant` is an identifier and is excluded.

---

## 3. Target Variable (cnt)

| Statistic | Value |
|---|---|
| Mean | 189.5 |
| Median | 142.0 |
| Std | 181.4 |
| Min | 1 |
| Max | 977 |
| Skewness | 1.28 |

The distribution is right-skewed (skewness = 1.28): most hours see moderate demand but
a tail of high-demand hours inflates the mean above the median. The wide standard deviation
(181) relative to the mean (189) reflects strong hour-of-day and seasonality effects.

**Figure:** `reports/figures/01_target_distribution.png`

---

## 4. Key EDA Findings

### 4.1 Hour-of-Day Bimodal Peak Pattern

Mean demand by hour shows a clear bimodal pattern consistent with commuter behaviour:

| Hour | Mean cnt |
|---|---|
| 08:00 | 359.0 (morning peak) |
| 17:00 | 461.5 (evening peak — highest of the day) |
| 04:00 | 6.4 (overnight minimum) |

The evening peak (461.5) is approximately 1.3x the morning peak (359.0). Demand falls sharply
after midnight to a minimum around 04:00, then rises steeply from 06:00 onward.

**Correlation of `hr` with `cnt`: 0.394** — the hour of day is the third strongest linear
correlate of the target.

**Figure:** `reports/figures/02_demand_by_hour.png`

### 4.2 Seasonal Variation

| Season | Mean cnt |
|---|---|
| Spring (1) | 111.1 |
| Summer (2) | 208.3 |
| Fall (3) | 236.0 |
| Winter (4) | 198.9 |

Fall has the highest average demand (236.0); Spring has the lowest (111.1), a ratio of
approximately 2.1:1. This suggests seasonal temperature/daylight effects on ridership.

**Correlation of `season` with `cnt`: 0.178.**

**Figure:** `reports/figures/03_demand_by_season.png`

### 4.3 Weather Impact

| Weather Situation | Description | Mean cnt |
|---|---|---|
| 1 | Clear / Few Clouds | 204.9 |
| 2 | Mist / Cloudy | 175.2 |
| 3 | Light Rain or Snow | 111.6 |
| 4 | Heavy Rain / Ice / Thunderstorm | 74.3 |

Demand drops monotonically as conditions worsen — from 204.9 in clear weather to 74.3
in severe conditions, a 63% reduction. Category 4 has only 3 observations, so the estimate
is unreliable.

**Correlation of `weathersit` with `cnt`: −0.142.**

**Figure:** `reports/figures/04_demand_by_weather.png`

### 4.4 Working Day vs Weekend / Holiday

| Day Type | Mean cnt |
|---|---|
| Weekend / Holiday (workingday = 0) | 181.4 |
| Working Day (workingday = 1) | 193.2 |

The difference is small (11.8 rentals). However, the within-day shape differs substantially:
working days show strong commuter peaks (see hour-of-day analysis), while weekends show a
broader midday plateau.

**Correlation of `workingday` with `cnt`: 0.030** — small linear correlation.

**Figure:** `reports/figures/06_demand_workingday_vs_weekend.png`

### 4.5 Year-on-Year Growth

| Year | Encoded | Mean cnt |
|---|---|---|
| 2011 | yr = 0 | 143.8 |
| 2012 | yr = 1 | 234.7 |

Demand grew 63% from 2011 to 2012, suggesting programme expansion or increased adoption.
**Correlation of `yr` with `cnt`: 0.250.**

### 4.6 Correlation Summary

| Feature | Pearson r with cnt |
|---|---|
| temp | +0.405 |
| atemp | +0.401 |
| hr | +0.394 |
| yr | +0.250 |
| season | +0.178 |
| mnth | +0.121 |
| windspeed | +0.093 |
| workingday | +0.030 |
| weekday | +0.027 |
| holiday | −0.031 |
| weathersit | −0.142 |
| hum | −0.323 |

Top positive correlates: `temp` (0.405), `atemp` (0.401), and `hr` (0.394).
Top negative correlates: `hum` (−0.323) and `weathersit` (−0.142).
`temp` and `atemp` are strongly collinear (r = 0.988); retaining both in a linear model
would cause multicollinearity.

**Figure:** `reports/figures/05_correlation_heatmap.png`

---

## 5. Feature Considerations

- **hr** is a cyclic variable (0–23). Encoding it as a raw integer captures linear trend
  only. Sine/cosine encoding or one-hot encoding better captures the bimodal shape.
- **temp and atemp** are highly collinear (r ≈ 0.99). Retain only one to avoid redundancy.
- **season and mnth** are correlated (r ≈ 0.83). `mnth` provides finer granularity.
- **yr** captures year-on-year programme growth and is a useful predictor despite having
  only two unique values.
- **weathersit** category 4 has only 3 observations and may not generalise.
- **workingday and holiday** interact; `workingday` already encodes the absence of holiday/
  weekend, so including all three may be redundant in some models.
- Tree-based models (e.g. Random Forest) can capture the non-linear, interaction-rich
  relationships without explicit feature engineering.

---

## 6. Limitations

- **Correlation is not causation.** All correlation coefficients describe statistical
  association in this dataset only. Causal claims require a different study design.
- **Two-year time window.** The dataset covers 2011–2012. Patterns may not generalise
  to later periods, different cities, or post-pandemic behaviour.
- **Weather category 4** has only 3 observations; statistics for severe weather are
  highly uncertain.
- **Aggregation.** The hourly granularity masks sub-hour demand fluctuations.
- **No geographic features.** Station-level or neighbourhood-level data are absent.
- **`dteday` excluded.** The string date column is not used; calendar effects are
  captured by `yr`, `mnth`, and `hr`.

---

## 7. Recommendations for Modelling

1. **Use all 12 usable predictors** as a starting point and apply feature importance
   to prune if needed.
2. **Encode `hr` cyclically** (sin/cos) or as one-hot to capture the bimodal pattern.
3. **Drop either `temp` or `atemp`** to avoid multicollinearity in linear models; both
   can be retained in tree-based models.
4. **Apply a chronological train/test split** to respect temporal ordering and prevent
   data leakage from future observations.
5. **Fit all preprocessing on training data only.**
6. **Compare at minimum:** a mean-baseline (DummyRegressor) and a Random Forest. The
   strong non-linearity (bimodal hour effect, weather interactions) suggests tree-based
   models will substantially outperform a linear baseline.
7. **Evaluate with MAE, RMSE, and R²** — the right-skewed target means RMSE penalises
   large errors more than MAE.

---

## 8. Generated Artifacts

| File | Description |
|---|---|
| `artifacts/eda/summary_statistics.csv` | `describe()` output for all numeric columns |
| `artifacts/eda/correlation_matrix.csv` | Pearson correlation matrix (predictors + cnt) |
| `artifacts/eda/demand_by_hour.csv` | Mean cnt per hour of day (24 rows) |
| `reports/figures/01_target_distribution.png` | Histogram of cnt with mean/median lines |
| `reports/figures/02_demand_by_hour.png` | Mean cnt by hour (line plot) |
| `reports/figures/03_demand_by_season.png` | Mean cnt by season (bar chart) |
| `reports/figures/04_demand_by_weather.png` | Mean cnt by weather situation (bar chart) |
| `reports/figures/05_correlation_heatmap.png` | Pearson correlation heatmap |
| `reports/figures/06_demand_workingday_vs_weekend.png` | Boxplot: working day vs weekend/holiday |
