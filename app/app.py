"""
Bike-Sharing Demand Predictor
Streamlit application for hourly bike-sharing demand prediction.

Inference contract: artifacts/inference-contract.json
Pipeline: modelling/artifacts/pipeline.joblib
"""

from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

PIPELINE_PATH = Path(__file__).resolve().parent.parent / "modelling" / "artifacts" / "pipeline.joblib"

FEATURE_ORDER = [
    "season",
    "yr",
    "mnth",
    "hr",
    "holiday",
    "weekday",
    "workingday",
    "weathersit",
    "temp",
    "atemp",
    "hum",
    "windspeed",
]

SEASON_LABELS = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
WEATHERSIT_LABELS = {
    1: "Clear / Partly Cloudy",
    2: "Mist / Cloudy",
    3: "Light Rain or Snow",
    4: "Heavy Rain / Ice / Fog",
}
WEEKDAY_LABELS = {
    0: "Sunday",
    1: "Monday",
    2: "Tuesday",
    3: "Wednesday",
    4: "Thursday",
    5: "Friday",
    6: "Saturday",
}
MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


# ---------------------------------------------------------------------------
# Model loading
# ---------------------------------------------------------------------------


@st.cache_resource
def load_pipeline():
    """Load the trained scikit-learn pipeline from disk.

    Returns the pipeline object, or raises an informative error if
    the artifact is missing or incompatible.
    """
    import joblib

    if not PIPELINE_PATH.exists():
        raise FileNotFoundError(
            f"Pipeline artifact not found at: {PIPELINE_PATH}\n"
            "Run the ML training step before launching the app."
        )
    return joblib.load(PIPELINE_PATH)


# ---------------------------------------------------------------------------
# Input validation
# ---------------------------------------------------------------------------


def validate_inputs(inputs: dict) -> list[str]:
    """Return a list of validation error messages (empty = valid)."""
    errors = []

    int_ranges = {
        "season": (1, 4),
        "yr": (0, 1),
        "mnth": (1, 12),
        "hr": (0, 23),
        "holiday": (0, 1),
        "weekday": (0, 6),
        "workingday": (0, 1),
        "weathersit": (1, 4),
    }
    float_ranges = {
        "temp": (0.0, 1.0),
        "atemp": (0.0, 1.0),
        "hum": (0.0, 1.0),
        "windspeed": (0.0, 1.0),
    }

    for feature, (lo, hi) in int_ranges.items():
        val = inputs.get(feature)
        if val is None or not (lo <= int(val) <= hi):
            errors.append(f"{feature} must be between {lo} and {hi}; got {val}.")

    for feature, (lo, hi) in float_ranges.items():
        val = inputs.get(feature)
        if val is None or not (lo <= float(val) <= hi):
            errors.append(f"{feature} must be between {lo:.1f} and {hi:.1f}; got {val}.")

    return errors


# ---------------------------------------------------------------------------
# Page configuration
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Bike-Sharing Demand Predictor",
    page_icon="bicycle",
    layout="wide",
)

st.title("Bike-Sharing Demand Predictor")
st.markdown(
    "**Random Forest model** — R² = 0.90, 100 trees "
    "| Trained on UCI Bike Sharing Dataset (Washington D.C., 2011–2012)"
)

# ---------------------------------------------------------------------------
# Pipeline loading with error display
# ---------------------------------------------------------------------------

try:
    pipeline = load_pipeline()
    pipeline_ok = True
except FileNotFoundError as exc:
    st.error(str(exc))
    pipeline_ok = False
except Exception as exc:
    st.error(
        f"Failed to load the prediction pipeline: {exc}\n\n"
        "Ensure the pipeline artifact is a valid scikit-learn pipeline saved with joblib."
    )
    pipeline_ok = False

# ---------------------------------------------------------------------------
# Sidebar — inputs
# ---------------------------------------------------------------------------

with st.sidebar:
    st.header("Input Features")
    st.markdown("Adjust the sliders and dropdowns, then click **Predict**.")

    # --- Temporal ---
    st.subheader("Time")

    hr_val = st.slider(
        "Hour of Day (0 = midnight, 23 = 11 pm)",
        min_value=0,
        max_value=23,
        value=17,
        step=1,
        help="Hour of day (0–23)",
    )

    yr_val = st.selectbox(
        "Year",
        options=[0, 1],
        index=1,
        format_func=lambda x: "2011" if x == 0 else "2012",
        help="0 = 2011, 1 = 2012",
    )

    mnth_val = st.selectbox(
        "Month",
        options=list(MONTH_NAMES.keys()),
        index=8,  # September
        format_func=lambda x: MONTH_NAMES[x],
        help="Calendar month (1–12)",
    )

    weekday_val = st.selectbox(
        "Day of Week",
        options=list(WEEKDAY_LABELS.keys()),
        index=3,  # Wednesday
        format_func=lambda x: WEEKDAY_LABELS[x],
        help="0 = Sunday, 6 = Saturday",
    )

    holiday_val = st.selectbox(
        "Public Holiday?",
        options=[0, 1],
        index=0,
        format_func=lambda x: "No" if x == 0 else "Yes",
        help="Whether the day is a public holiday",
    )

    workingday_val = st.selectbox(
        "Working Day?",
        options=[0, 1],
        index=1,
        format_func=lambda x: "No (weekend / holiday)" if x == 0 else "Yes",
        help="1 if the day is neither a weekend nor a holiday",
    )

    # --- Season / Weather ---
    st.subheader("Season and Weather")

    season_val = st.selectbox(
        "Season",
        options=list(SEASON_LABELS.keys()),
        index=2,  # Fall
        format_func=lambda x: SEASON_LABELS[x],
        help="1 = Spring, 2 = Summer, 3 = Fall, 4 = Winter",
    )

    weathersit_val = st.selectbox(
        "Weather Situation",
        options=list(WEATHERSIT_LABELS.keys()),
        index=0,  # Clear
        format_func=lambda x: WEATHERSIT_LABELS[x],
        help=(
            "1 = Clear/Partly Cloudy, 2 = Mist/Cloudy, "
            "3 = Light Rain or Snow, 4 = Heavy Rain/Ice/Fog"
        ),
    )

    # --- Environmental ---
    st.subheader("Environmental Conditions")

    temp_val = st.slider(
        "Temperature (normalized, 0 = 0 °C, 1 = 41 °C)",
        min_value=0.0,
        max_value=1.0,
        value=0.68,
        step=0.01,
        format="%.2f",
        help="Actual temperature divided by 41. E.g. 0.68 ≈ 27.9 °C",
    )

    atemp_val = st.slider(
        "Apparent Temperature (normalized, 0 = 0 °C, 1 = 50 °C)",
        min_value=0.0,
        max_value=1.0,
        value=0.63,
        step=0.01,
        format="%.2f",
        help="Feels-like temperature divided by 50. E.g. 0.63 ≈ 31.5 °C",
    )

    hum_val = st.slider(
        "Humidity (normalized, 0 = 0%, 1 = 100%)",
        min_value=0.0,
        max_value=1.0,
        value=0.55,
        step=0.01,
        format="%.2f",
        help="Relative humidity divided by 100.",
    )

    windspeed_val = st.slider(
        "Wind Speed (normalized, 0 = 0 km/h, 1 = 67 km/h)",
        min_value=0.0,
        max_value=1.0,
        value=0.19,
        step=0.01,
        format="%.2f",
        help="Wind speed divided by 67.",
    )

# ---------------------------------------------------------------------------
# Main area — prediction
# ---------------------------------------------------------------------------

inputs = {
    "season": int(season_val),
    "yr": int(yr_val),
    "mnth": int(mnth_val),
    "hr": int(hr_val),
    "holiday": int(holiday_val),
    "weekday": int(weekday_val),
    "workingday": int(workingday_val),
    "weathersit": int(weathersit_val),
    "temp": float(temp_val),
    "atemp": float(atemp_val),
    "hum": float(hum_val),
    "windspeed": float(windspeed_val),
}

col1, col2 = st.columns([2, 3])

with col1:
    predict_clicked = st.button(
        "Predict Demand",
        type="primary",
        disabled=not pipeline_ok,
        use_container_width=True,
    )

with col2:
    st.caption(
        "Click Predict to run the Random Forest model on the selected inputs."
    )

if predict_clicked:
    validation_errors = validate_inputs(inputs)

    if validation_errors:
        st.error("Input validation failed:\n" + "\n".join(f"- {e}" for e in validation_errors))
    else:
        input_df = pd.DataFrame([inputs], columns=FEATURE_ORDER)
        raw_prediction = float(pipeline.predict(input_df)[0])
        predicted_demand = max(0, int(round(raw_prediction)))

        st.metric(
            label="Predicted Demand",
            value=f"{predicted_demand} rentals / hour",
        )

        st.info(
            "This prediction is an **estimate**, not a guarantee. "
            "Actual demand depends on real-time conditions not captured in this model."
        )

# ---------------------------------------------------------------------------
# Input summary
# ---------------------------------------------------------------------------

with st.expander("Current Input Values", expanded=False):
    summary = {
        "Hour": f"{hr_val}:00",
        "Year": "2012" if yr_val == 1 else "2011",
        "Month": MONTH_NAMES[mnth_val],
        "Day of Week": WEEKDAY_LABELS[weekday_val],
        "Public Holiday": "Yes" if holiday_val == 1 else "No",
        "Working Day": "Yes" if workingday_val == 1 else "No",
        "Season": SEASON_LABELS[season_val],
        "Weather": WEATHERSIT_LABELS[weathersit_val],
        "Temperature (normalized)": f"{temp_val:.2f}  (~{temp_val * 41:.1f} °C)",
        "Apparent Temp (normalized)": f"{atemp_val:.2f}  (~{atemp_val * 50:.1f} °C)",
        "Humidity (normalized)": f"{hum_val:.2f}  (~{hum_val * 100:.0f}%)",
        "Wind Speed (normalized)": f"{windspeed_val:.2f}  (~{windspeed_val * 67:.1f} km/h)",
    }
    st.table(pd.DataFrame(summary.items(), columns=["Feature", "Value"]))

# ---------------------------------------------------------------------------
# Model information
# ---------------------------------------------------------------------------

st.divider()
st.subheader("About this Model")
st.markdown(
    """
Predictions are from a **Random Forest Regressor** (100 trees) trained on the
[UCI Bike Sharing Dataset](https://archive.ics.uci.edu/dataset/275/bike-sharing-dataset)
covering 2011–2012 hourly ridership for the **Capital Bikeshare** system in Washington D.C.

**Model performance on the held-out test set (last 20% by time):**
| Metric | Baseline (mean) | Random Forest |
|--------|-----------------|---------------|
| MAE    | 174.98          | 45.02         |
| RMSE   | 232.61          | 69.62         |
| R²    | -0.11           | **0.90**      |

**Known limitations:**
- Trained only on 2011–2012 data; may not reflect recent demand patterns.
- Cannot account for special events, infrastructure changes, or extreme weather.
- Normalized features (temp, atemp, hum, windspeed) must be supplied pre-normalized.
- Feature importances and correlations are **not** causal evidence.
- Out-of-range inputs may produce unreliable predictions.
"""
)
