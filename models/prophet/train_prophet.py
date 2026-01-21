import pandas as pd
from prophet import Prophet
import joblib
from pathlib import Path
import re

def safe_name(text):
    return re.sub(r'[^A-Za-z0-9_]', '_', text)

# -----------------------------
# Paths
# -----------------------------

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_PATH = BASE_DIR / "data" / "processed" / "cleaned" / "enrolment_clean.csv"


MODEL_DIR = Path("models/prophet/saved_models")
MODEL_DIR.mkdir(parents=True, exist_ok=True)

# -----------------------------
# Load & prepare data
# -----------------------------
df = pd.read_csv(DATA_PATH)
df["date"] = pd.to_datetime(df["date"])

# Create total demand
df["total_demand"] = (
    df["age_0_5"] + df["age_5_17"] + df["age_17_plus"]
)

# -----------------------------
# Train Prophet per district
# -----------------------------
for district, ddf in df.groupby("district"):

    ddf = (
        ddf.groupby("date", as_index=False)["total_demand"]
        .sum()
        .rename(columns={"date": "ds", "total_demand": "y"})
        .sort_values("ds")
    )

    # Skip very small districts
    if len(ddf) < 30:
        continue

    model = Prophet(
        yearly_seasonality=True,
        weekly_seasonality=True,
        interval_width=0.95
    )
    model.add_country_holidays(country_name="IN")

    model.fit(ddf)

    model_path = MODEL_DIR / f"prophet_{district.replace(' ', '_')}.pkl"
    joblib.dump(model, model_path)

    print(f"✅ Trained model for {district}")

print("\n🎯 All district Prophet models trained & saved")
