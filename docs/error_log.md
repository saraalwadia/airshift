# AirShift — Development Issues & Resolutions

This document records the main technical issues encountered during the development of AirShift and the resolutions used to address them.

The purpose of this log is not only to record errors, but also to document how development problems were diagnosed, corrected, and verified.

---

## 1. Raw Data Path Issue

### Problem

During the initial data profiling stage, the notebook did not find the expected raw dataset files.

The file search returned zero files even though the station CSV files were present in the project.

### Cause

The notebook was being executed from the `notebooks` directory, while the raw dataset was stored under:

```text
data/raw/
```

The relative path therefore needed to be resolved from the notebook's working directory.

### Resolution

The project data path was defined relative to the notebook location:

```text
../data/raw
```

The station files were then correctly discovered and loaded.

### Verification

All **12 monitoring station datasets** were successfully loaded and profiled.

---

## 2. Long Missing-Data Gaps

### Problem

Several pollutant variables contained prolonged missing-data periods.

Some gaps extended for hundreds of consecutive hours.

### Cause

The dataset contains genuine missing observations, and treating all missing values with simple interpolation could create artificial pollution patterns across long periods.

### Resolution

Missing numerical values were handled according to gap duration:

* Short gaps of up to **6 hours** were interpolated within each station.
* Prolonged gaps were retained as `NaN`.

Wind-direction gaps were handled separately using forward filling within each station.

### Verification

After cleaning:

* Short pollutant gaps were interpolated.
* Long pollutant gaps remained missing.
* The temporal structure of the station data remained intact.

---

## 3. Potential Treatment of Extreme Pollution Values

### Problem

The dataset contains observations with high pollutant concentrations.

These observations could initially appear to be potential outliers.

### Cause

AirShift is specifically designed to detect air-quality deterioration. Extremely high pollution observations can therefore represent meaningful environmental events rather than measurement errors.

### Resolution

High pollutant observations were not automatically removed as statistical outliers.

Instead, their validity was considered in the context of the project's objective.

### Verification

The cleaning process focused on clearly invalid values rather than removing high pollution observations solely because they were extreme.

---

## 4. Future-Data Leakage Risk During Feature Engineering

### Problem

The project predicts a future deterioration event, creating a potential risk of accidentally using future information in model features.

### Cause

Rolling statistics, trends, and lag features can introduce leakage if they include observations after the prediction timestamp.

### Resolution

Historical features were constructed using shifted observations.

For example, rolling statistics use previous observations rather than including future values.

The feature-engineering process follows the rule:

> Every model feature must be computable using information available at or before the prediction time.

### Verification

The engineered feature set was reviewed to ensure that lag, rolling, change, and trend features were based on historical observations.

The API feature-engineering implementation was also tested against the final model feature schema.

---

## 5. Deterioration Event Definition Clarification

### Problem

The initial interpretation of the six-hour event definition needed clarification.

A `shift(-6)` operation by itself would represent the value exactly six hours later, not whether deterioration occurs at any point during the next six hours.

### Cause

There is an important distinction between:

```text
Value exactly 6 hours later
```

and:

```text
Maximum value occurring anywhere within the next 1–6 hours
```

### Resolution

The final event definition uses the maximum PM2.5 value across the following six hourly observations.

The event occurs when:

```text
Future maximum PM2.5 ≥ Current PM2.5 × 1.30
```

### Verification

The labeling notebook was implemented using the future six-hour maximum, with the complete six-hour window required for a valid target.

---

## 6. Final XGBoost Model Not Fully Fitted

### Problem

The first saved version of:

```text
models/xgboost_final.joblib
```

contained a fitted preprocessing component but an XGBoost estimator that had not been fitted correctly.

When the final evaluation notebook attempted to use the model, a `NotFittedError` occurred.

### Cause

The final model-saving stage had not correctly completed the final training of the XGBoost estimator before the pipeline was saved.

### Resolution

The final XGBoost pipeline was retrained using the combined:

* 2013–2014 training data
* 2015 validation data

The tuned hyperparameters were retained:

```text
n_estimators = 400
learning_rate = 0.1
max_depth = 6
min_child_weight = 3
subsample = 0.7
colsample_bytree = 1.0
```

The corrected pipeline was then saved again.

### Verification

The final model was loaded successfully and verified:

```text
XGBoost fitted: True
File exists: True
```

The saved model was approximately **1.74 MB**.

---

## 7. API Feature Schema Mismatch

### Problem

The first `/predict` API test returned:

```text
HTTP 500
```

with the error:

```text
Generated features do not match the model schema.
Missing features:
['year', 'day']
```

### Cause

The API request accepts `datetime` as the temporal input, but the trained model expects the original temporal model features:

```text
year
month
day
hour
```

The API initially did not derive all of these fields from `datetime`.

### Resolution

The API was updated to derive:

```python
year
month
day
hour
```

from the supplied `datetime` values before feature engineering.

### Verification

After the correction:

* API import succeeded.
* Model loaded successfully.
* `/health` returned HTTP 200.
* `/predict` returned a valid prediction.

---

## 8. API Indentation Error

### Problem

While updating `api/main.py`, a malformed indentation caused:

```text
IndentationError: unexpected indent
```

### Cause

A code block had inconsistent indentation during manual editing.

### Resolution

The complete `api/main.py` file was replaced with the corrected version rather than attempting to repair isolated lines.

### Verification

The file passed Python compilation:

```text
python -m py_compile api/main.py
```

The FastAPI server subsequently started successfully.

---

## 9. API Minimum-History Requirement

### Problem

AirShift requires historical observations to calculate lag, rolling, change, and trend features.

A prediction cannot be generated from a single observation.

### Cause

The feature-engineering pipeline requires multiple consecutive observations.

### Resolution

The `/predict` endpoint requires at least **7 hourly observations**.

This provides sufficient history for the model's longest six-hour lag/trend calculations while allowing the final observation to be used as the prediction timestamp.

### Verification

A six-observation request correctly returned:

```text
HTTP 400
```

with:

```text
At least 7 hourly observations are required.
```

A valid seven-observation request successfully generated a prediction.

---

## 10. API Temporal Continuity Validation

### Problem

Feature engineering assumes that the supplied observations represent consecutive hourly measurements.

A request containing a missing hour could otherwise produce misleading lag and rolling features.

### Resolution

The API checks the difference between consecutive timestamps and requires every interval to equal:

```text
1 hour
```

### Verification

A test request with one missing timestamp correctly returned:

```text
HTTP 400
```

with:

```text
Observations must be consecutive hourly measurements.
```

---

## 11. Duplicate Timestamp Validation

### Problem

Duplicate timestamps could produce ambiguous historical sequences and incorrect temporal features.

### Resolution

The API explicitly checks for duplicate `datetime` values before feature generation.

### Verification

A test request containing a duplicate timestamp correctly returned:

```text
HTTP 400
```

with:

```text
Duplicate datetime values are not allowed.
```

---

## 12. Multiple-Station Validation

### Problem

The feature-engineering process is performed within each monitoring station.

Combining observations from different stations in one prediction request would therefore create an invalid temporal sequence.

### Resolution

The API requires all observations in a prediction request to belong to the same station.

### Verification

A request containing observations from both:

```text
Aotizhongxin
Dingling
```

correctly returned:

```text
HTTP 400
```

with:

```text
All observations must belong to the same station.
```

---

## 13. API Feature-Engineering Consistency

### Problem

The API must reproduce the same feature structure expected by the trained model.

Even small differences between notebook feature engineering and API feature engineering could cause incorrect predictions or model errors.

### Resolution

The API feature-engineering logic was implemented using the same feature definitions used during the project feature-engineering stage.

The generated features are compared against the final model's expected feature names.

### Verification

The dedicated feature-engineering test produced:

```text
Engineered shape: (7, 99)

Missing model features: 0
Extra engineered features: 0

Final row shape: (97,)
Missing values in final row: 0

Model expects 97 features: OK

Feature names match the final model: OK
```

---

# 14. API Validation Test Suite

After resolving the API issues, a complete validation script was used to test both successful and invalid requests.

The final test suite covered:

| Test                       | HTTP Result | Status |
| -------------------------- | ----------: | ------ |
| Valid prediction           |         200 | Passed |
| Fewer than 7 observations  |         400 | Passed |
| Non-consecutive timestamps |         400 | Passed |
| Duplicate timestamp        |         400 | Passed |
| Multiple stations          |         400 | Passed |

The valid test request returned:

```json
{
  "prediction_time": "2013-03-01T06:00:00",
  "station": "Aotizhongxin",
  "deterioration_probability": 0.939,
  "warning_threshold": 0.3,
  "early_warning": true
}
```

---

# 15. Development Lessons

The development process highlighted several important engineering considerations for AirShift.

### Preserve temporal structure

Time-series projects require chronological validation and careful handling of historical features.

### Separate short and long missing gaps

Short gaps can sometimes be reasonably interpolated, while long gaps can introduce artificial patterns if filled without sufficient evidence.

### Treat leakage prevention as a design requirement

Feature engineering must be designed around the information available at prediction time.

### Keep model training and API feature engineering consistent

The deployed system must reproduce the feature schema expected by the trained model.

### Validate APIs with both valid and invalid inputs

A successful prediction alone is not sufficient to validate an API. Input validation and failure behavior should also be tested.

### Verify saved models independently

A model file existing on disk does not guarantee that every component of the saved pipeline has been fitted correctly. Explicit loading and prediction tests are therefore important.

---

# 16. Current Status

All documented issues in this log were resolved and verified during development.

The final AirShift pipeline currently includes:

* Completed data profiling
* Completed data cleaning
* Completed feature engineering
* Defined deterioration event
* Completed target labeling
* Developed and optimized XGBoost model
* Completed final test evaluation
* Completed model interpretation
* Completed early-warning evaluation
* Completed lead-time analysis
* Working FastAPI prediction service
* API validation test suite

This document records the development issues that materially affected the implementation and the corresponding resolutions.
