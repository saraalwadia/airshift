import pandas as pd
import requests


DATA_PATH = "data/processed/airshift_labeled.csv"

TEST_START = "2016-01-01"
TEST_END = "2017-02-28 17:00:00"

TARGET = "Deterioration"

EXCLUDE_COLUMNS = [
    TARGET,
    "No",
    "datetime"
]


# Load AirShift labeled data
df = pd.read_csv(
    DATA_PATH,
    parse_dates=["datetime"]
)


# Select the same unseen test period
test_data = df[
    (df["datetime"] >= TEST_START) &
    (df["datetime"] <= TEST_END)
].copy()


# Select one real observation
# Load the final model to identify a high-probability test observation
import joblib

model = joblib.load("models/xgboost_final.joblib")

X_test = test_data.drop(
    columns=EXCLUDE_COLUMNS
)

test_probabilities = model.predict_proba(X_test)[:, 1]

high_probability_index = test_probabilities.argmax()

sample = test_data.iloc[high_probability_index]

print(
    "Selected probability:",
    test_probabilities[high_probability_index]
)


# Build request using the same 97 model features
features = sample.drop(
    labels=EXCLUDE_COLUMNS
).to_dict()


# Send request to FastAPI
response = requests.post(
    "http://127.0.0.1:8000/predict",
    json={"features": features}
)


print("HTTP status:", response.status_code)
print("API response:")
print(response.json())