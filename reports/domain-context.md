# Domain Context: Bike-Sharing Demand Prediction

**Agent:** research-agent  
**Date:** 2026-11-25

---

## 1. What Is Capital Bikeshare

Capital Bikeshare is a station-based bicycle rental system operating in Washington D.C. and surrounding jurisdictions. Users rent a bicycle from any docked station and return it to any station in the network. Membership options include single-use passes (casual users) and annual subscriptions (registered users).

The dataset used in this project was drawn from Capital Bikeshare's publicly released trip logs (http://capitalbikeshare.com/system-data), covering the years 2011 and 2012. During that period the network was in an early growth phase; mean hourly demand rose from approximately 144 rentals per hour in 2011 to 235 in 2012, reflecting fleet and station expansion.

Bike-sharing systems of this kind have proliferated globally. The UCI Readme notes that by the time of the dataset's publication there were over 500 programmes worldwide comprising over 500,000 bicycles. The fundamental operational structure — automated check-out and return, GPS-tracked docks — makes such systems unusually well-suited to quantitative demand analysis compared with other public transport modes, where departure and arrival records are rarely captured at the individual trip level.

---

## 2. Why Hourly Demand Prediction Matters

Knowing how many bicycles will be rented in a given hour at the system level provides operational value across several dimensions.

**Fleet rebalancing.** Station-based systems suffer from spatial imbalances: popular destination stations fill up while origin stations run empty. Anticipating demand peaks allows operators to pre-position trucks to redistribute bicycles before shortages develop, reducing the frequency of "no bikes available" and "no docks available" failures.

**Staffing and maintenance scheduling.** Maintenance crews and customer-service staff can be deployed in line with expected demand rather than on fixed rotas, improving both coverage and cost efficiency.

**Capacity planning.** Infrastructure decisions — adding docks, relocating stations, sizing a new service area — require forecasts of expected utilisation at the hourly level.

**Demand-responsive pricing.** Some operators use dynamic pricing during peak periods. Accurate demand forecasts support pricing decisions.

**Integration with wider transport planning.** City authorities use bike-sharing demand data as an input to broader mobility models. Accurate hourly forecasts improve these models' ability to represent cycling as a mode choice.

For this project, the prediction task is therefore practically motivated: a deployed model could feed real-time operational decisions or planning dashboards.

---

## 3. Key Factors Known to Influence Demand

The following factors are established in the dataset and confirmed by descriptive statistics derived from the data.

### 3.1 Hour of Day

Demand shows a pronounced bimodal pattern on working days, with peaks at 08:00 (mean 359.0 rentals) and 17:00–18:00 (mean 461.5 and 425.5). Overnight hours have very low demand (04:00 mean: 6.4). This reflects commuter behaviour: registered (subscription) users dominate working-day demand. On non-working days the pattern flattens to a single midday plateau, reflecting leisure use.

Hour of day (`hr`) is the strongest single time-based predictor in the dataset (Pearson r = 0.394 with `cnt`), though the relationship is non-linear and therefore the linear correlation understates its true predictive value.

### 3.2 Weather Conditions

Temperature (`temp`) and apparent temperature (`atemp`) show the strongest linear correlations with `cnt` (r = +0.405 and +0.401 respectively). Warmer conditions are associated with higher demand. Humidity is negatively associated (r = -0.323): higher humidity — particularly in conjunction with precipitation — coincides with lower demand. Wind speed shows a modest negative association (r = +0.093 is positive but small).

The categorical weather situation variable (`weathersit`) confirms this pattern: mean demand drops from 204.9 (clear) to 175.2 (mist) to 111.6 (light snow/rain). The four heavy-rain/snow observations (weathersit=4) show a mean of 74.3, though this is based on only 3 records and should not be treated as a reliable estimate.

### 3.3 Season

Demand varies substantially by season. Fall produces the highest mean demand (236.0 rentals/hour), summer is next (208.3), winter is relatively high (198.9), and spring has the lowest mean (111.1). The relatively low spring figure is partly an artefact of the 2011 period when the network was smaller; the cross-seasonal signal is confounded with the year-on-year growth trend.

### 3.4 Working Day vs. Weekend/Holiday

Working days (mean 193.2) show slightly higher total system demand than non-working days (mean 181.4). However, the within-day pattern differs substantially: working days have concentrated commute peaks while non-working days have a broader leisure-use distribution.

Holidays (500 records) show slightly lower mean demand than non-holidays (r = -0.031 with `cnt`), consistent with reduced commuting.

### 3.5 Year-on-Year Growth

The year indicator (`yr`) has a Pearson correlation of +0.250 with `cnt`. Mean hourly demand in 2012 was 63% higher than in 2011. Including `yr` as a feature allows the model to account for this structural growth, but it also means that generalisation beyond the training period requires caution: the model learns one year-on-year step and cannot extrapolate to further growth.

---

## 4. Why This Is a Regression Problem

The target variable `cnt` is a non-negative integer count with a wide range (1 to 977 in this dataset) and a mean of 189.5. It is treated as a continuous regression target rather than a classification target because:

- The count range is wide and the specific predicted value matters for operational use.
- Classification would require arbitrary binning that discards information.
- Standard regression metrics (MAE, RMSE, R²) are well-suited to evaluating predictions of counts at this scale.

Count-specific regression methods (Poisson or negative binomial regression) are theoretically appropriate for count data. However, for this project the simpler approaches of linear regression (baseline) and Random Forest regression provide a practical comparison on this scale of data, and their outputs are interpretable without specialist distributional assumptions.

---

## 5. Limitations of This Domain Context

- This context is based on the 2011–2012 dataset. Capital Bikeshare's network, pricing, membership base, and service area have changed substantially since then.
- The observations in this document describe associations present in the data. They do not establish causal mechanisms; for example, the association between temperature and demand could partly reflect confounding with season and day type.
- Station-level dynamics (imbalances, local events, micro-weather) are not visible in the system-aggregated hourly data used here.

---

## 6. References

Fanaee-T, Hadi, and Gama, Joao. "Event labeling combining ensemble detectors and background knowledge." *Progress in Artificial Intelligence* (2013): pp. 1-15. Springer Berlin Heidelberg. doi:10.1007/s13748-013-0040-3.

UCI Machine Learning Repository — Bike Sharing Dataset: https://archive.ics.uci.edu/dataset/275/bike-sharing-dataset

Capital Bikeshare system data: http://capitalbikeshare.com/system-data

DC Holiday Schedule (source for `holiday` column): http://dchr.dc.gov/page/holiday-schedule
