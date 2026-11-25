"""Exploratory data analysis for the UCI Bike Sharing hourly dataset.

Produces CSV artifacts and PNG figures summarising the relationship between
time, season, weather, and hourly bike-sharing demand.

Run with:
    uv run python src/data_analysis/eda.py

Outputs:
    artifacts/eda/summary_statistics.csv
    artifacts/eda/correlation_matrix.csv
    artifacts/eda/demand_by_hour.csv
    reports/figures/01_target_distribution.png
    reports/figures/02_demand_by_hour.png
    reports/figures/03_demand_by_season.png
    reports/figures/04_demand_by_weather.png
    reports/figures/05_correlation_heatmap.png
    reports/figures/06_demand_workingday_vs_weekend.png
"""

from __future__ import annotations

import matplotlib
matplotlib.use("Agg")  # non-interactive backend — must precede pyplot import

import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = PROJECT_ROOT / "data" / "raw" / "hour.csv"
ARTIFACTS_EDA = PROJECT_ROOT / "artifacts" / "eda"
FIGURES = PROJECT_ROOT / "reports" / "figures"

ARTIFACTS_EDA.mkdir(parents=True, exist_ok=True)
FIGURES.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Predictor columns (excludes target, leakage, and identifier columns)
# ---------------------------------------------------------------------------

PREDICTORS = [
    "season", "yr", "mnth", "hr", "holiday", "weekday", "workingday",
    "weathersit", "temp", "atemp", "hum", "windspeed",
]

TARGET = "cnt"

# Columns excluded from predictor analysis
EXCLUDED = {"instant", "dteday", "casual", "registered"}

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------

sys.path.insert(0, str(PROJECT_ROOT))
from src.data_pipeline.load import load_hour_csv

print("Loading dataset ...")
df = load_hour_csv(DATA_PATH)
print(f"  Shape: {df.shape}")
print(f"  Columns: {list(df.columns)}")

# ---------------------------------------------------------------------------
# 1. Data quality checks
# ---------------------------------------------------------------------------

print("\n--- Data Quality ---")
missing = df.isnull().sum()
print(f"Missing values per column:\n{missing[missing > 0] if missing.any() else '  None'}")

dupes = df.duplicated().sum()
print(f"Duplicate rows: {dupes}")

print(f"\nData types:\n{df.dtypes}")

# ---------------------------------------------------------------------------
# 2. Summary statistics
# ---------------------------------------------------------------------------

print("\n--- Summary Statistics ---")
numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
summary = df[numeric_cols].describe()
print(summary)
summary.to_csv(ARTIFACTS_EDA / "summary_statistics.csv")
print(f"  Saved: {ARTIFACTS_EDA / 'summary_statistics.csv'}")

# ---------------------------------------------------------------------------
# 3. Target distribution
# ---------------------------------------------------------------------------

print("\n--- Target (cnt) Distribution ---")
cnt_desc = df[TARGET].describe()
skewness = df[TARGET].skew()
print(cnt_desc)
print(f"  Skewness: {skewness:.4f}")

# ---------------------------------------------------------------------------
# 4. Demand by hour
# ---------------------------------------------------------------------------

demand_by_hour = df.groupby("hr")[TARGET].mean().reset_index()
demand_by_hour.columns = ["hr", "mean_cnt"]
demand_by_hour.to_csv(ARTIFACTS_EDA / "demand_by_hour.csv", index=False)
print(f"\nDemand by hour (mean cnt):\n{demand_by_hour.to_string(index=False)}")
print(f"  Saved: {ARTIFACTS_EDA / 'demand_by_hour.csv'}")

# ---------------------------------------------------------------------------
# 5. Demand by season
# ---------------------------------------------------------------------------

demand_by_season = df.groupby("season")[TARGET].mean().reset_index()
demand_by_season.columns = ["season", "mean_cnt"]
print(f"\nDemand by season (mean cnt):\n{demand_by_season.to_string(index=False)}")

# ---------------------------------------------------------------------------
# 6. Demand by weather situation
# ---------------------------------------------------------------------------

demand_by_weather = df.groupby("weathersit")[TARGET].mean().reset_index()
demand_by_weather.columns = ["weathersit", "mean_cnt"]
print(f"\nDemand by weathersit (mean cnt):\n{demand_by_weather.to_string(index=False)}")

# ---------------------------------------------------------------------------
# 7. Demand by working day vs weekend/holiday
# ---------------------------------------------------------------------------

demand_by_workingday = df.groupby("workingday")[TARGET].mean().reset_index()
demand_by_workingday.columns = ["workingday", "mean_cnt"]
print(f"\nDemand by workingday (mean cnt):\n{demand_by_workingday.to_string(index=False)}")

# ---------------------------------------------------------------------------
# 8. Demand by year
# ---------------------------------------------------------------------------

demand_by_yr = df.groupby("yr")[TARGET].mean().reset_index()
demand_by_yr.columns = ["yr", "mean_cnt"]
print(f"\nDemand by year (mean cnt):\n{demand_by_yr.to_string(index=False)}")

# ---------------------------------------------------------------------------
# 9. Correlation matrix
# ---------------------------------------------------------------------------

corr_cols = PREDICTORS + [TARGET]
corr_matrix = df[corr_cols].corr()
corr_matrix.to_csv(ARTIFACTS_EDA / "correlation_matrix.csv")
print(f"\nCorrelations with cnt:\n{corr_matrix[TARGET].sort_values(ascending=False)}")
print(f"  Saved: {ARTIFACTS_EDA / 'correlation_matrix.csv'}")

# ---------------------------------------------------------------------------
# Figures
# ---------------------------------------------------------------------------

# Figure style — no seaborn despine
plt.rcParams.update({
    "figure.dpi": 100,
    "axes.spines.top": False,
    "axes.spines.right": False,
})

# -- Figure 1: Target distribution ------------------------------------------
fig, ax = plt.subplots(figsize=(8, 5))
ax.hist(df[TARGET], bins=50, color="#4472C4", edgecolor="white", linewidth=0.4)
ax.set_title("Distribution of Hourly Bike-Sharing Demand (cnt)", fontsize=13)
ax.set_xlabel("Hourly Rentals (cnt)")
ax.set_ylabel("Frequency")
mean_val = df[TARGET].mean()
median_val = df[TARGET].median()
ax.axvline(mean_val, color="crimson", linestyle="--", linewidth=1.2,
           label=f"Mean: {mean_val:.1f}")
ax.axvline(median_val, color="darkorange", linestyle=":", linewidth=1.2,
           label=f"Median: {median_val:.1f}")
ax.legend(fontsize=10)
fig.tight_layout()
fig.savefig(FIGURES / "01_target_distribution.png", dpi=100, bbox_inches="tight")
plt.close(fig)
print(f"\nSaved: {FIGURES / '01_target_distribution.png'}")

# -- Figure 2: Demand by hour of day ----------------------------------------
fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(demand_by_hour["hr"], demand_by_hour["mean_cnt"],
        marker="o", markersize=5, color="#4472C4", linewidth=2)
ax.fill_between(demand_by_hour["hr"], demand_by_hour["mean_cnt"],
                alpha=0.15, color="#4472C4")
ax.set_title("Mean Hourly Bike Demand by Hour of Day", fontsize=13)
ax.set_xlabel("Hour of Day (0–23)")
ax.set_ylabel("Mean Rentals (cnt)")
ax.set_xticks(range(0, 24))
ax.set_xticklabels(range(0, 24), fontsize=8)
fig.tight_layout()
fig.savefig(FIGURES / "02_demand_by_hour.png", dpi=100, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {FIGURES / '02_demand_by_hour.png'}")

# -- Figure 3: Demand by season ---------------------------------------------
season_labels = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
demand_by_season["label"] = demand_by_season["season"].map(season_labels)
colors_season = ["#4472C4", "#ED7D31", "#A9D18E", "#FF0000"]
fig, ax = plt.subplots(figsize=(7, 5))
bars = ax.bar(demand_by_season["label"], demand_by_season["mean_cnt"],
              color=colors_season, edgecolor="white")
ax.set_title("Mean Hourly Bike Demand by Season", fontsize=13)
ax.set_xlabel("Season")
ax.set_ylabel("Mean Rentals (cnt)")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
            f"{bar.get_height():.0f}", ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(FIGURES / "03_demand_by_season.png", dpi=100, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {FIGURES / '03_demand_by_season.png'}")

# -- Figure 4: Demand by weather situation -----------------------------------
weather_labels = {
    1: "Clear/\nFew Clouds",
    2: "Mist/\nCloudy",
    3: "Light\nRain/Snow",
    4: "Heavy\nRain/Snow",
}
demand_by_weather["label"] = demand_by_weather["weathersit"].map(weather_labels)
colors_weather = ["#4472C4", "#70AD47", "#FFC000", "#FF0000"]
n_w = len(demand_by_weather)
fig, ax = plt.subplots(figsize=(8, 5))
bars = ax.bar(demand_by_weather["label"], demand_by_weather["mean_cnt"],
              color=colors_weather[:n_w], edgecolor="white")
ax.set_title("Mean Hourly Bike Demand by Weather Situation", fontsize=13)
ax.set_xlabel("Weather Situation")
ax.set_ylabel("Mean Rentals (cnt)")
for bar in bars:
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
            f"{bar.get_height():.0f}", ha="center", va="bottom", fontsize=9)
fig.tight_layout()
fig.savefig(FIGURES / "04_demand_by_weather.png", dpi=100, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {FIGURES / '04_demand_by_weather.png'}")

# -- Figure 5: Correlation heatmap ------------------------------------------
fig, ax = plt.subplots(figsize=(10, 8))
mask = np.zeros_like(corr_matrix, dtype=bool)
mask[np.triu_indices_from(mask, k=1)] = True
sns.heatmap(
    corr_matrix,
    annot=True,
    fmt=".2f",
    cmap="coolwarm",
    center=0,
    vmin=-1,
    vmax=1,
    ax=ax,
    linewidths=0.4,
    annot_kws={"size": 7},
)
ax.set_title("Pearson Correlation Matrix (Predictors + cnt)", fontsize=13)
plt.xticks(rotation=45, ha="right", fontsize=9)
plt.yticks(rotation=0, fontsize=9)
fig.tight_layout()
fig.savefig(FIGURES / "05_correlation_heatmap.png", dpi=100, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {FIGURES / '05_correlation_heatmap.png'}")

# -- Figure 6: Demand by workingday vs weekend/holiday ----------------------
workingday_labels = {0: "Weekend/Holiday", 1: "Working Day"}
fig, ax = plt.subplots(figsize=(7, 5))
workingday_data = [
    df.loc[df["workingday"] == k, TARGET].values
    for k in [0, 1]
]
bp = ax.boxplot(
    workingday_data,
    patch_artist=True,
    medianprops={"color": "white", "linewidth": 2},
    whiskerprops={"linewidth": 1.2},
    capprops={"linewidth": 1.2},
    flierprops={"marker": "o", "markersize": 2, "alpha": 0.3},
)
ax.set_xticks([1, 2])
ax.set_xticklabels([workingday_labels[0], workingday_labels[1]])
colors_wd = ["#ED7D31", "#4472C4"]
for patch, color in zip(bp["boxes"], colors_wd):
    patch.set_facecolor(color)
ax.set_title("Hourly Bike Demand: Working Day vs Weekend/Holiday", fontsize=13)
ax.set_xlabel("Day Type")
ax.set_ylabel("Hourly Rentals (cnt)")
fig.tight_layout()
fig.savefig(FIGURES / "06_demand_workingday_vs_weekend.png", dpi=100, bbox_inches="tight")
plt.close(fig)
print(f"Saved: {FIGURES / '06_demand_workingday_vs_weekend.png'}")

print("\n--- EDA complete ---")
print(f"Artifacts saved to: {ARTIFACTS_EDA}")
print(f"Figures saved to: {FIGURES}")
