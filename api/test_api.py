import json

import pandas as pd
import requests


# --------------------------------------------------
# API configuration
# --------------------------------------------------

API_URL = "http://127.0.0.1:8000/predict"

DATA_PATH = "data/processed/airshift_feature_engineered.csv"


# --------------------------------------------------
# Load dataset
# --------------------------------------------------

df = pd.read_csv(
    DATA_PATH,
    parse_dates=["datetime"],
)


# --------------------------------------------------
# Select one station and 7 consecutive observations
# --------------------------------------------------

sample = (
    df[
        df["station"] == "Aotizhongxin"
    ]
    .sort_values("datetime")
    .head(7)
    .copy()
)


# --------------------------------------------------
# Select only raw input columns
# --------------------------------------------------

RAW_COLUMNS = [
    "datetime",
    "PM2.5",
    "PM10",
    "SO2",
    "NO2",
    "CO",
    "O3",
    "TEMP",
    "PRES",
    "DEWP",
    "RAIN",
    "wd",
    "WSPM",
    "station",
]


sample = sample[RAW_COLUMNS]


# --------------------------------------------------
# Rename PM2.5 for API schema
# --------------------------------------------------

sample = sample.rename(
    columns={
        "PM2.5": "PM2_5",
    }
)


# --------------------------------------------------
# Convert datetime to JSON-compatible format
# --------------------------------------------------

sample["datetime"] = (
    sample["datetime"]
    .dt.strftime("%Y-%m-%dT%H:%M:%S")
)


# --------------------------------------------------
# Create request payload
# --------------------------------------------------

payload = {
    "observations": sample.to_dict(
        orient="records"
    )
}


print("Sending prediction request...")
print(
    "Station:",
    sample["station"].iloc[0],
)
print(
    "Observations:",
    len(sample),
)
print(
    "Time range:",
    sample["datetime"].iloc[0],
    "→",
    sample["datetime"].iloc[-1],
)


# --------------------------------------------------
# Send request
# --------------------------------------------------

response = requests.post(
    API_URL,
    json=payload,
    timeout=30,
)


# --------------------------------------------------
# Display response
# --------------------------------------------------

print()
print("HTTP status:", response.status_code)

try:
    print(
        json.dumps(
            response.json(),
            indent=2,
        )
    )

except Exception:
    print(response.text)
