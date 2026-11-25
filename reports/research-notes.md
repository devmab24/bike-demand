# Research Notes: UCI Bike Sharing Dataset

**Agent:** research-agent  
**Date:** 2026-11-25  
**Research question:** How do time, season, weather, and other environmental factors influence hourly bike-sharing demand, and can these variables be used to predict demand?

---

## 1. Dataset Provenance

**Source:** UCI Machine Learning Repository  
URL: https://archive.ics.uci.edu/dataset/275/bike-sharing-dataset

**Original data source:** Capital Bikeshare system, Washington D.C., USA  
Raw rental logs: http://capitalbikeshare.com/system-data (publicly available)  
Weather data: http://www.freemeteo.com  
Holiday schedule: http://dchr.dc.gov/page/holiday-schedule

**Collection period:** 2011-01-01 to 2012-12-31 (two full calendar years)

**Dataset preparation:** Hadi Fanaee-T, Laboratory of Artificial Intelligence and Decision Support (LIAAD), University of Porto, INESC Porto, Portugal. The original trip-level logs were aggregated to hourly counts, then joined with weather and calendar metadata.

**Required citation:**

> Fanaee-T, Hadi, and Gama, Joao, "Event labeling combining ensemble detectors and background knowledge", *Progress in Artificial Intelligence* (2013): pp. 1-15, Springer Berlin Heidelberg, doi:10.1007/s13748-013-0040-3.

BibTeX:
```
@article{
    year={2013},
    issn={2192-6352},
    journal={Progress in Artificial Intelligence},
    doi={10.1007/s13748-013-0040-3},
    title={Event labeling combining ensemble detectors and background knowledge},
    url={http://dx.doi.org/10.1007/s13748-013-0040-3},
    publisher={Springer Berlin Heidelberg},
    keywords={Event labeling; Event detection; Ensemble learning; Background knowledge},
    author={Fanaee-T, Hadi and Gama, Joao},
    pages={1-15}
}
```

---

## 2. Dataset Description

**File:** `data/raw/hour.csv`  
**Records:** 17,379 hourly observations  
**Columns:** 17  
**Missing values:** None (all 17 columns have 0 missing values, confirmed from data)

**Years covered:**
- yr=0 (2011): 8,645 records
- yr=1 (2012): 8,734 records

---

## 3. Feature Definitions

All definitions below are drawn from the official Readme.txt distributed with the dataset.

| Column | Type | Description |
|---|---|---|
| instant | int | Record index (identifier — excluded from modelling) |
| dteday | str/date | Calendar date (YYYY-MM-DD) |
| season | int | Season: 1=spring, 2=summer, 3=fall, 4=winter |
| yr | int | Year: 0=2011, 1=2012 |
| mnth | int | Month: 1–12 |
| hr | int | Hour of day: 0–23 |
| holiday | int | 1 if the day is a public holiday, 0 otherwise |
| weekday | int | Day of week: 0=Sunday, 1=Monday, …, 6=Saturday |
| workingday | int | 1 if neither weekend nor holiday, 0 otherwise |
| weathersit | int | Weather situation (see encoding below) |
| temp | float | Normalized temperature in Celsius, divided by 41 (the observed maximum) |
| atemp | float | Normalized feeling (apparent) temperature in Celsius, divided by 50 |
| hum | float | Normalized relative humidity, divided by 100 |
| windspeed | float | Normalized wind speed, divided by 67 |
| casual | int | Count of non-registered (casual) rental users — EXCLUDED (causes target leakage) |
| registered | int | Count of registered rental users — EXCLUDED (causes target leakage) |
| cnt | int | Total count of rental bikes (casual + registered) — the prediction target |

**Weather situation encoding:**
- 1: Clear, few clouds, partly cloudy
- 2: Mist + cloudy, mist + broken clouds, mist + few clouds, mist
- 3: Light snow, light rain + thunderstorm + scattered clouds, light rain + scattered clouds
- 4: Heavy rain + ice pellets + thunderstorm + mist, snow + fog

**Normalization reference values (from Readme.txt):**
- temp: divided by 41 (max observed Celsius)
- atemp: divided by 50 (max observed feeling temperature)
- hum: divided by 100
- windspeed: divided by 67

**Actual temperature range in the data:**
- temp: 0.02–1.00 (approximately 0.8–41.0 °C)
- atemp: 0.00–1.00
- hum: 0.00–1.00
- windspeed: 0.00–0.8507 (maximum ~57 km/h)

---

## 4. Target Variable: cnt

Summary statistics derived from `data/raw/hour.csv`:

| Statistic | Value |
|---|---|
| Count | 17,379 |
| Mean | 189.5 |
| Standard deviation | 181.4 |
| Minimum | 1 |
| 25th percentile | 40 |
| Median (50th percentile) | 142 |
| 75th percentile | 281 |
| Maximum | 977 |

The distribution is right-skewed (mean 189.5 >> median 142). Many hours have low demand (overnight, adverse weather), while peak hours can exceed 900 rentals. The minimum is 1, so there are no zero-rental hours recorded in this dataset — however this is likely an artifact of the data collection or aggregation method rather than a guarantee of continuous demand.

**Demand grew from 2011 to 2012:** Mean cnt in 2011 was 143.8; in 2012 it was 234.7 — a 63% increase. This growth reflects Capital Bikeshare's network expansion, not a purely seasonal or weather effect.

---

## 5. Key Domain Constraints

### 5.1 Target Leakage: casual and registered

`cnt = casual + registered` by construction. If either `casual` or `registered` is included as a predictor, the model learns a trivial identity and will appear near-perfect on any evaluation split. These two columns must be excluded from all feature matrices used for training and prediction.

Similarly, `instant` is merely a row index with no predictive meaning and must be excluded.

### 5.2 Chronological Train/Test Split

The dataset spans two calendar years with a growth trend. Because consecutive hours are temporally autocorrelated (demand at hour t is related to demand at t-1, t+1, and the same hour on adjacent days), a random split would cause information from future hours to appear in the training set. This would inflate performance metrics and produce a model that cannot generalize to truly unseen future data.

The correct approach is a chronological split: train on the earlier period (e.g., the first ~80% of records ordered by date) and evaluate on the later period.

### 5.3 Preprocessing Fit on Training Data Only

Any normalization, scaling, or encoding fit on the full dataset before the split constitutes data leakage. All preprocessing transformers (e.g., StandardScaler) must be fit on training data only and applied to the test set using the fitted parameters.

---

## 6. Actual Summary Statistics by Group

**Mean cnt by season:**
- Spring (1): 111.1
- Summer (2): 208.3
- Fall (3): 236.0
- Winter (4): 198.9

**Mean cnt by weather situation:**
- Clear (1): 204.9
- Mist (2): 175.2
- Light snow/rain (3): 111.6
- Heavy rain/snow (4): 74.3

**Mean cnt by workingday:**
- Weekend/holiday (0): 181.4
- Working day (1): 193.2

**Season distribution (record counts):**
- Spring: 4,242
- Summer: 4,409
- Fall: 4,496
- Winter: 4,232

**Weather situation distribution:**
- Clear (1): 11,413 (65.7%)
- Mist (2): 4,544 (26.1%)
- Light snow/rain (3): 1,419 (8.2%)
- Heavy rain/snow (4): 3 (0.02%)

**Mean cnt by hour of day (selected):**
- Peak AM: 07:00=212.1, 08:00=359.0
- Midday: 12:00=253.3, 13:00=253.7
- Peak PM: 17:00=461.5, 18:00=425.5
- Overnight low: 04:00=6.4

---

## 7. Correlations with cnt (predictors only)

Pearson correlations computed from `data/raw/hour.csv` on predictor columns only:

| Predictor | Correlation with cnt |
|---|---|
| temp | +0.405 |
| atemp | +0.401 |
| hr | +0.394 |
| hum | -0.323 |
| yr | +0.250 |
| season | +0.178 |
| weathersit | -0.142 |
| mnth | +0.121 |
| windspeed | +0.093 |
| holiday | -0.031 |
| workingday | +0.030 |
| weekday | +0.027 |

**Important caveat:** Pearson correlation captures only linear monotonic relationships. The relationship between `hr` and `cnt` is strongly non-linear (bimodal peaks at commute hours). The correlation coefficient of 0.394 substantially understates `hr`'s actual predictive value. Correlation does not imply causation; these figures describe statistical associations within this dataset.

---

## 8. Research Limitations

1. **Historical data, not current:** This dataset covers 2011–2012. Capital Bikeshare has expanded significantly since then. The learned model reflects demand patterns from that historical period and should not be presented as characterising current demand.

2. **Normalized features obscure absolute values:** Because temperature, humidity, and wind speed are normalized, the model works with relative values, not physical units. Users of the inference application must supply normalized inputs.

3. **Weather situation is categorical and coarse:** Four categories compress a wide range of meteorological conditions. The same code 1 (clear) covers both a mild spring morning and an extreme summer heat day.

4. **No spatial resolution:** The dataset records total system-wide demand per hour. Station-level imbalances (which drive operational rebalancing decisions) are not represented.

5. **Sparse extreme weather:** weathersit=4 (heavy rain/snow) appears only 3 times in 17,379 records, so models will not reliably learn behaviour under extreme conditions.

6. **External events not captured:** The Readme notes that some anomalies correspond to major events (Hurricane Sandy, October 2012). These are not explicitly labelled as features, so the model may not generalise well to similar disruptions.

7. **Demand growth trend:** The 63% mean-demand increase from 2011 to 2012 reflects network expansion. A chronological split places 2012 data in the test set, meaning the model is asked to generalise to a period of higher baseline demand than the training period.

8. **Correlation does not imply causation:** The relationships observed between weather, time, and demand are associative. The dataset cannot establish whether temperature causes higher demand or whether higher-demand seasons tend to have higher temperatures.

---

## 9. Implications for This Project

- Use only: `season`, `yr`, `mnth`, `hr`, `holiday`, `weekday`, `workingday`, `weathersit`, `temp`, `atemp`, `hum`, `windspeed` as predictors.
- Exclude: `instant`, `dteday`, `casual`, `registered`, `cnt` (the target) from the feature matrix.
- Split chronologically (not randomly) to simulate real-world future prediction.
- Fit all preprocessing on training data only.
- Report MAE, RMSE, and R² as evaluation metrics.
- Present feature importances as association measures, not causal effects.
- Cite Fanaee-T & Gama (2013) in all outputs.
