# AirShift API Documentation

## 1. Overview

AirShift provides a FastAPI-based prediction API for the **Early Warning System for Air Quality Deterioration**.

The API receives a short sequence of recent hourly air-quality and meteorological observations, performs the same feature engineering used during model development, and uses the final trained XGBoost model to estimate the probability of future air quality deterioration.

The API returns:

* Deterioration probability
* Warning threshold
* Early-warning decision

The current warning threshold is **0.30**.

---

## 2. API Architecture

The prediction workflow is:

```text
Client
   ↓
POST /predict
   ↓
Request Validation
   ↓
Timestamp & Station Validation
   ↓
Feature Engineering
   ↓
Final XGBoost Model
   ↓
Deterioration Probability
   ↓
Threshold = 0.30
   ↓
Early Warning Decision
```

The API uses the same feature-engineering logic as the AirShift modeling pipeline to reduce inconsistencies between model development and inference.

---

## 3. Technology Stack

* Python
* FastAPI
* Uvicorn
* Pydantic
* pandas
* joblib
* XGBoost
* scikit-learn

The trained model is loaded from:

```text
models/xgboost_final.joblib
```

---

## 4. Running the API Locally

Run the following command from the project root:

```powershell
uvicorn api.main:app --reload
```

The API is then available at:

```text
http://127.0.0.1:8000
```

FastAPI's interactive documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The OpenAPI schema is available at:

```text
http://127.0.0.1:8000/openapi.json
```

---

## 5. Endpoints

### `GET /`

Basic API status endpoint.

#### Example response

```json
{
  "message": "AirShift API is running",
  "status": "ok"
}
```

---

### `GET /health`

Checks whether the API is running and whether the final model has been loaded.

#### Example response

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

---

### `POST /predict`

Generates an early-warning prediction from recent hourly observations.

This endpoint requires **at least seven hourly observations** from the same monitoring station.

The observations are used to generate the lag, rolling, change, and trend features required by the final model.

---

## 6. Request Structure

The request body has the following structure:

```json
{
  "observations": [
    {
      "datetime": "YYYY-MM-DDTHH:MM:SS",
      "PM2_5": 0.0,
      "PM10": 0.0,
      "SO2": 0.0,
      "NO2": 0.0,
      "CO": 0.0,
      "O3": 0.0,
      "TEMP": 0.0,
      "PRES": 0.0,
      "DEWP": 0.0,
      "RAIN": 0.0,
      "wd": "N",
      "WSPM": 0.0,
      "station": "Aotizhongxin"
    }
  ]
}
```

### Observation fields

| Field      | Type     | Description           |
| ---------- | -------- | --------------------- |
| `datetime` | datetime | Observation timestamp |
| `PM2_5`    | float    | PM2.5 concentration   |
| `PM10`     | float    | PM10 concentration    |
| `SO2`      | float    | SO2 concentration     |
| `NO2`      | float    | NO2 concentration     |
| `CO`       | float    | CO concentration      |
| `O3`       | float    | O3 concentration      |
| `TEMP`     | float    | Temperature           |
| `PRES`     | float    | Atmospheric pressure  |
| `DEWP`     | float    | Dew point temperature |
| `RAIN`     | float    | Rainfall              |
| `wd`       | string   | Wind direction        |
| `WSPM`     | float    | Wind speed            |
| `station`  | string   | Monitoring station    |

The API uses `PM2_5` in the JSON request because the original column name `PM2.5` contains a period. Internally, the API converts it back to `PM2.5` before feature engineering.

---

## 7. Input Validation

The API performs several validation checks before generating a prediction.

### Minimum history

At least **7 hourly observations** are required.

```text
At least 7 hourly observations are required.
```

This is necessary because the model uses historical features including 1-hour, 3-hour, and 6-hour lags and rolling statistics.

### Single monitoring station

All observations must belong to the same station.

```text
All observations must belong to the same station.
```

### Consecutive timestamps

Observations must represent consecutive hourly measurements.

```text
Observations must be consecutive hourly measurements.
```

### Duplicate timestamps

Duplicate timestamps are rejected.

```text
Duplicate datetime values are not allowed.
```

### Feature availability

If the available observations are insufficient to generate all required model features, the API returns an error describing the missing features.

---

## 8. Feature Engineering During Prediction

The API reproduces the feature-engineering logic used during AirShift model development.

From the supplied observations, it derives:

### Temporal features

* `year`
* `month`
* `day`
* `hour`
* `day_of_week`
* `is_weekend`

### Lag features

For the six pollutants:

* 1-hour lag
* 3-hour lag
* 6-hour lag

### Rolling statistics

For 3-hour and 6-hour windows:

* Rolling mean
* Rolling maximum
* Rolling standard deviation

The rolling calculations use previous observations rather than the current observation.

### Short-term changes

For the six pollutants:

* 1-hour change
* 3-hour change

### Trend features

For the six pollutants:

* 3-hour trend
* 6-hour trend

The final engineered row is checked against the feature schema expected by the trained XGBoost model.

---

## 9. Model Prediction

The final AirShift model is an XGBoost classifier trained using the selected hyperparameters from the model development stage.

The API loads the saved fitted pipeline:

```text
models/xgboost_final.joblib
```

The model receives **97 input features** after the feature-engineering and preprocessing pipeline.

The API extracts the probability associated with the positive class:

```python
predict_proba(...)[0, 1]
```

This probability represents the model's estimated probability of a deterioration event.

---

## 10. Early-Warning Threshold

The API uses:

```text
Warning threshold = 0.30
```

The decision rule is:

```text
probability >= 0.30
        ↓
Early Warning = True
```

Otherwise:

```text
probability < 0.30
        ↓
Early Warning = False
```

The threshold was selected during the early-warning analysis with emphasis on maintaining high recall and reducing missed deterioration events.

It is a model-design threshold and is not re-optimized using the final test set.

---

## 11. Response Structure

A successful `/predict` request returns:

```json
{
  "prediction_time": "YYYY-MM-DDTHH:MM:SS",
  "station": "Aotizhongxin",
  "deterioration_probability": 0.0000,
  "warning_threshold": 0.3,
  "early_warning": false
}
```

### Response fields

| Field                       | Type     | Description                                                     |
| --------------------------- | -------- | --------------------------------------------------------------- |
| `prediction_time`           | datetime | Timestamp of the latest supplied observation                    |
| `station`                   | string   | Monitoring station                                              |
| `deterioration_probability` | float    | Predicted probability of deterioration                          |
| `warning_threshold`         | float    | Threshold used for the warning decision                         |
| `early_warning`             | boolean  | Whether the predicted probability reaches the warning threshold |

---

## 12. Example Prediction

A successful API validation test using seven consecutive observations from the `Aotizhongxin` station returned:

```json
{
  "prediction_time": "2013-03-01T06:00:00",
  "station": "Aotizhongxin",
  "deterioration_probability": 0.939,
  "warning_threshold": 0.3,
  "early_warning": true
}
```

This means that, for that specific test input, the model produced a deterioration probability of **0.939**, which was above the configured warning threshold of **0.30**.

---

## 13. Error Responses

The API returns HTTP `400` for invalid prediction requests.

### Fewer than seven observations

```json
{
  "detail": "At least 7 hourly observations are required."
}
```

### Non-consecutive timestamps

```json
{
  "detail": "Observations must be consecutive hourly measurements."
}
```

### Duplicate timestamps

```json
{
  "detail": "Duplicate datetime values are not allowed."
}
```

### Multiple stations

```json
{
  "detail": "All observations must belong to the same station."
}
```

### Insufficient historical data

When feature generation produces missing values required by the model, the API returns:

```json
{
  "detail": {
    "error": "Insufficient historical data for feature generation.",
    "missing_features": []
  }
}
```

The `missing_features` list contains the actual features that could not be generated for the supplied observations.

---

## 14. Internal Server Errors

The API also validates the generated feature schema before prediction.

If the generated features do not match the model schema, the API returns HTTP `500` with information about the missing features.

If model prediction itself fails, the API returns HTTP `500` with the prediction error.

These checks are intended to make failures easier to diagnose during development.

---

## 15. API Validation Tests

The API was tested using a dedicated validation script:

```text
api/test_api.py
```

The test suite covers:

1. Valid prediction
2. Fewer than seven observations
3. Non-consecutive timestamps
4. Duplicate timestamps
5. Multiple monitoring stations

The validation results were:

| Test                       | Expected | Result |
| -------------------------- | -------- | ------ |
| Valid prediction           | HTTP 200 | Passed |
| Fewer than 7 observations  | HTTP 400 | Passed |
| Non-consecutive timestamps | HTTP 400 | Passed |
| Duplicate timestamp        | HTTP 400 | Passed |
| Multiple stations          | HTTP 400 | Passed |

The API validation test suite completed successfully.

---

## 16. API Design Notes

### Consistency with the ML pipeline

The API does not implement a separate feature-engineering strategy. It reuses the same feature definitions used during model development.

This is important because changing the feature-generation logic during inference could produce inputs that differ from those used to train the model.

### Temporal validation

The API requires consecutive hourly observations because the AirShift features depend on temporal relationships between observations.

### Station consistency

The current prediction endpoint processes observations from one monitoring station at a time. This prevents historical features from being calculated across different stations.

---

## 17. Current Limitations

The current API is a **local project inference service** and is not presented as a production deployment.

Current limitations include:

* The API currently runs locally through Uvicorn.
* The trained model is loaded from the local project directory.
* No authentication mechanism is implemented.
* No rate limiting is implemented.
* No production deployment infrastructure is configured.
* The current endpoint processes one station's observation sequence per request.
* Input observations must already contain the required air-quality and meteorological measurements.

These limitations are appropriate for the current project stage and can be addressed in a future deployment phase.

---

## 18. Project Integration

The API is integrated into the AirShift project as the inference layer:

```text
Historical Dataset
        ↓
Data Cleaning
        ↓
Feature Engineering
        ↓
Model Development
        ↓
Final XGBoost Model
        ↓
Saved Model
        ↓
FastAPI
        ↓
Prediction Endpoint
        ↓
Early Warning
```

This separates model development from model inference and provides a reusable interface for future applications.

---

## 19. Future Extensions

Potential future extensions include:

* Web-based monitoring dashboard
* Real-time sensor integration
* Batch prediction endpoint
* Multi-station prediction
* Authentication and access control
* Production deployment
* Logging and monitoring
* Automated model updates
* Integration with an alerting system

These are future possibilities and are not part of the current implementation.

---

## Conclusion

The AirShift API provides a simple inference interface around the final trained XGBoost model.

It validates incoming hourly observations, reproduces the project's feature-engineering process, generates a deterioration probability, and applies the AirShift early-warning threshold of **0.30**.

The current implementation has been validated through successful prediction and input-validation tests and provides the foundation for future integration with a user-facing monitoring or alerting application.
