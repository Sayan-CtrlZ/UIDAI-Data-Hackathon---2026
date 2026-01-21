from pathlib import Path
import joblib
import pandas as pd

# -----------------------------
# Base directory
# -----------------------------
BASE_DIR = Path(__file__).resolve().parents[2]

MODEL_DIR = BASE_DIR / "models" / "prophet" / "models" / "prophet" / "saved_models"
OUTPUT_DIR = BASE_DIR / "data" / "processed" / "forecasts"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

FORECAST_DAYS = 30
CAPACITY_THRESHOLD = 5000

all_forecasts = []

# -----------------------------
# Forecast from each model
# -----------------------------
for model_file in MODEL_DIR.glob("*.pkl"):
    district = model_file.stem.replace("prophet_", "")
    model = joblib.load(model_file)

    future = model.make_future_dataframe(periods=FORECAST_DAYS)
    forecast = model.predict(future)

    fc = forecast.tail(FORECAST_DAYS)[
        ["ds", "yhat", "yhat_lower", "yhat_upper"]
    ].copy()

    fc["district"] = district

    fc["risk_level"] = "Normal"
    fc.loc[fc["yhat"] > CAPACITY_THRESHOLD, "risk_level"] = "High Risk"
    fc.loc[
        (fc["yhat"] > 0.8 * CAPACITY_THRESHOLD) &
        (fc["yhat"] <= CAPACITY_THRESHOLD),
        "risk_level"
    ] = "Watch"

    all_forecasts.append(fc)

# -----------------------------
# Save output
# -----------------------------
final_forecast = pd.concat(all_forecasts, ignore_index=True)
output_file = OUTPUT_DIR / "district_demand_forecast.csv"
final_forecast.to_csv(output_file, index=False)

print(f"✅ Forecast CSV created at: {output_file}")
