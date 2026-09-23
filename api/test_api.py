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
# Raw input columns
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


# --------------------------------------------------
# Helper function
# --------------------------------------------------

def prepare_sample(sample):
    """Prepare raw observations for the API."""

    sample = sample[RAW_COLUMNS].copy()

    sample = sample.rename(
        columns={
            "PM2.5": "PM2_5",
        }
    )

    sample["datetime"] = (
        sample["datetime"]
        .dt.strftime("%Y-%m-%dT%H:%M:%S")
    )

    return {
        "observations": sample.to_dict(
            orient="records"
        )
    }


# --------------------------------------------------
# Helper function for displaying results
# --------------------------------------------------

def print_result(test_name, response):
    """Print an API test result."""

    print()
    print("=" * 60)
    print(test_name)
    print("=" * 60)
    print("Status:", response.status_code)

    try:
        print(
            json.dumps(
                response.json(),
                indent=2,
            )
        )

    except Exception:
        print(response.text)


# --------------------------------------------------
# Prepare valid 7-hour sample
# --------------------------------------------------

valid_sample = (
    df[
        df["station"] == "Aotizhongxin"
    ]
    .sort_values("datetime")
    .head(7)
    .copy()
)


# --------------------------------------------------
# Test 1 — Valid prediction
# --------------------------------------------------

response = requests.post(
    API_URL,
    json=prepare_sample(valid_sample),
    timeout=30,
)

print_result(
    "TEST 1 — Valid Prediction",
    response,
)


# --------------------------------------------------
# Test 2 — Fewer than 7 observations
# --------------------------------------------------

short_sample = valid_sample.head(6)

response = requests.post(
    API_URL,
    json=prepare_sample(short_sample),
    timeout=30,
)

print_result(
    "TEST 2 — Fewer Than 7 Observations",
    response,
)


# --------------------------------------------------
# Test 3 — Non-consecutive timestamps
# --------------------------------------------------

gap_sample = (
    df[
        df["station"] == "Aotizhongxin"
    ]
    .sort_values("datetime")
    .head(8)
    .copy()
)

gap_sample = gap_sample.drop(
    index=gap_sample.index[3]
)

response = requests.post(
    API_URL,
    json=prepare_sample(gap_sample),
    timeout=30,
)

print_result(
    "TEST 3 — Non-Consecutive Timestamps",
    response,
)


# --------------------------------------------------
# Test 4 — Duplicate timestamp
# --------------------------------------------------

duplicate_sample = valid_sample.copy()

duplicate_sample.iloc[
    1,
    duplicate_sample.columns.get_loc("datetime"),
] = duplicate_sample.iloc[0]["datetime"]

response = requests.post(
    API_URL,
    json=prepare_sample(duplicate_sample),
    timeout=30,
)

print_result(
    "TEST 4 — Duplicate Timestamp",
    response,
)


# --------------------------------------------------
# Test 5 — Multiple stations
# --------------------------------------------------

multi_station_sample = valid_sample.copy()

multi_station_sample.loc[
    multi_station_sample.index[-1],
    "station",
] = "Dingling"

response = requests.post(
    API_URL,
    json=prepare_sample(multi_station_sample),
    timeout=30,
)

print_result(
    "TEST 5 — Multiple Stations",
    response,
)


# --------------------------------------------------
# Completion message
# --------------------------------------------------

print()
print("=" * 60)
print("API validation tests completed.")
print("=" * 60)
