# AirShift — Decisions and Notes

This document records the main methodological and engineering decisions made during the development of AirShift, including the reasoning behind them and important project boundaries.

It complements the detailed methodology and error log by focusing specifically on **why key decisions were made**.

---

## 1. Project Scope

AirShift was designed as an early warning system rather than a conventional pollutant forecasting system.

The objective is to identify whether current and recent environmental conditions indicate that air quality is likely to deteriorate within the following several hours.

The project focuses on a binary classification problem:

* `0` — No deterioration event
* `1` — Deterioration event

The system uses historical air quality and meteorological observations to estimate the probability of a future deterioration event.

---

## 2. Automated Raw Data Download

A dedicated `scripts/download_data.py` script was added to make raw dataset acquisition reproducible.

The script downloads the original Beijing Multi-Site Air Quality Dataset and extracts the station CSV files into `data/raw/`.

The script also checks whether the expected station files already exist and skips the download when the dataset is already available.

This separates raw data acquisition from the analysis notebooks and allows the project dataset to be obtained consistently without requiring manual download and file placement.

The script only handles raw data acquisition and does not modify processed data, trained models, or analysis outputs.

---

## 3. Deterioration Event Definition

### 3.1 Why PM2.5?

PM2.5 was selected as the primary pollutant for defining the deterioration event because it is a major air-quality indicator and is consistently available across the monitoring stations.

The project therefore focuses on short-term deterioration in PM2.5 rather than attempting to combine multiple pollutants into a single target.

### 3.2 Why a Relative Increase?

The deterioration event was defined using a relative increase rather than a fixed concentration threshold.

The final definition is:

> PM2.5 increases by at least 30% within the following six hours.

A relative threshold allows the event definition to represent a meaningful deterioration from the current pollution level rather than applying the same absolute increase to all environmental conditions.

### 3.3 Why Six Hours?

A six-hour horizon was selected because the project focuses on **short-term early warning** rather than long-term forecasting.

The horizon is long enough to capture developing deterioration patterns while remaining focused on near-term warning.

### 3.4 Why the Maximum Future PM2.5?

The target considers the maximum PM2.5 value observed during the following six hours.

This allows an event to be detected if the required increase occurs at any point within the defined future window rather than only at exactly six hours later.

### 3.5 Clarification of `shift(-6)`

During development, it was clarified that `shift(-6)` represents the value exactly six hours ahead.

It does not by itself represent an event occurring at any point within the next six hours.

The final labeling logic therefore evaluates the future six-hour window explicitly.

---

## 4. Missing Data Decisions

### 4.1 Short Numerical Gaps

Short numerical gaps of up to six hours were interpolated within each monitoring station.

The decision was based on the assumption that short gaps can reasonably be estimated from nearby observations while avoiding unnecessary loss of data.

### 4.2 Long Numerical Gaps

Long pollutant gaps greater than six hours were retained as `NaN`.

They were not filled artificially because long interpolation periods could create values that are not supported by the observed data.

### 4.3 Wind Direction

Missing wind-direction values were handled using forward filling within each station.

Wind direction is categorical, so numerical interpolation was not appropriate.

### 4.4 Extreme Pollution Values

High pollutant concentrations were not automatically treated as outliers.

Extreme pollution episodes are relevant to the project's objective because the system is specifically intended to identify deterioration events.

Removing extreme observations could therefore remove meaningful examples of the target phenomenon.

---

## 5. Feature Engineering Decisions

### 5.1 Historical Features

The feature engineering process focuses heavily on recent environmental history.

The final feature set includes:

* Pollutant lag features
* Rolling means
* Rolling maximums
* Rolling standard deviations
* Short-term changes
* Short-term trend features
* Temporal features
* Meteorological variables
* Station and wind-direction information

These features were selected to represent both current environmental conditions and recent changes.

### 5.2 Avoiding Future-Data Leakage

All historical and rolling features were constructed using information available at or before the prediction time.

For example, rolling statistics use shifted observations rather than including the current future information.

This was necessary because the project is intended to simulate an early-warning setting in which the model cannot access future observations.

---

## 6. Temporal Validation Strategy

A chronological train-validation-test structure was used instead of random splitting.

The periods were defined as:

| Dataset    | Period    |
| ---------- | --------- |
| Training   | 2013–2014 |
| Validation | 2015      |
| Final Test | 2016–2017 |

This decision prevents future observations from being used during model development and provides a more realistic evaluation of performance on later periods.

The final test period was kept separate from model selection, hyperparameter tuning, and threshold selection.

---

## 7. Model Development Decisions

Three classification models were evaluated:

1. Logistic Regression
2. Random Forest
3. XGBoost

The purpose was to establish multiple model baselines using different modeling approaches.

XGBoost was selected for further optimization based on its validation performance.

The selection was made using validation results rather than the final test set.

---

## 8. XGBoost Optimization Decisions

### 8.1 Why XGBoost?

XGBoost was selected for further development because it provided strong validation performance while supporting nonlinear relationships between environmental variables and deterioration events.

### 8.2 TimeSeriesSplit

`TimeSeriesSplit` with three splits was used during hyperparameter optimization.

This preserved temporal ordering within the cross-validation process.

### 8.3 Optimization Metric

`average_precision` was used as the scoring metric during randomized hyperparameter search.

This metric was selected because the project is a binary classification problem and the positive deterioration class is the primary class of interest.

### 8.4 Search Strategy

`RandomizedSearchCV` was used with:

* 15 parameter configurations
* 3 temporal folds
* 45 total model fits

The search was performed only on the development data and did not use the final test period.

### 8.5 Final Hyperparameters

The selected XGBoost configuration was:

```text
n_estimators = 400
learning_rate = 0.1
max_depth = 6
min_child_weight = 3
subsample = 0.7
colsample_bytree = 1.0
```

---

## 9. Final Model Training Decision

After model and hyperparameter selection, the final XGBoost model was retrained using the combined training and validation data.

This included:

* 2013–2014 training data
* 2015 validation data

The final training dataset contained:

```text
296,481 observations
97 model features
```

The final test period remained completely unseen.

This approach allows the final model to use all available development-period information while preserving an independent test set for final evaluation.

---

## 10. Final Test Evaluation

The final model was evaluated on the 2016–2017 test period.

The final test set contained:

```text
121,900 observations
```

The evaluation included:

* Accuracy
* Precision
* Recall
* F1 Score
* ROC-AUC
* PR-AUC
* Confusion matrix
* ROC curve
* Precision-recall curve

The final test metrics were:

| Metric    | Result |
| --------- | -----: |
| Accuracy  | 0.7368 |
| Precision | 0.7244 |
| Recall    | 0.7315 |
| F1 Score  | 0.7279 |
| ROC-AUC   | 0.8215 |
| PR-AUC    | 0.8186 |

The final test set was not used for model selection or tuning.

---

## 11. Feature Importance

Built-in XGBoost feature importance was used as an initial model interpretation method.

The purpose was to identify which processed features were most frequently relied upon by the learned decision trees.

The most important features included:

* Recent PM2.5 values
* Wind-direction categories
* PM10 historical features
* Rain
* Hour
* Short-term pollutant changes
* Wind speed
* Station information

Feature importance was treated as an interpretation of model usage rather than evidence of causality.

---

## 12. SHAP Analysis

SHAP was used to provide a more detailed interpretation of the final XGBoost model.

The analysis was performed on a sample of 5,000 observations from the final test set.

SHAP was selected because it provides information about both:

* Global feature importance
* The direction and magnitude of feature contributions to predictions

The analysis showed strong contributions from:

* Current PM2.5
* PM2.5 lagged by one hour
* Hour
* Wind speed
* Month
* Temperature
* Short-term PM2.5 changes
* Dew point
* Pressure
* Short-term changes in other pollutants

The SHAP results were interpreted as model behavior rather than causal relationships.

---

## 13. Early-Warning Threshold Decision

The final model produces a probability of deterioration.

A probability threshold was therefore required to convert the probability into an early-warning decision.

A threshold of:

```text
0.30
```

was selected.

The threshold was selected using the validation period rather than the final test set.

The main consideration was the early-warning objective, where missing a deterioration event is particularly important.

Therefore, the threshold was intentionally selected to provide higher recall rather than simply maximizing accuracy.

This is a project design decision rather than a test-set optimization result.

---

## 14. Early-Warning Test Results

Using the 0.30 threshold on the final test set produced:

| Metric    | Result |
| --------- | -----: |
| Precision | 0.6252 |
| Recall    | 0.8998 |
| F1 Score  | 0.7378 |

The resulting confusion matrix was:

|                 | Predicted Negative | Predicted Positive |
| --------------- | -----------------: | -----------------: |
| Actual Negative |             31,575 |             31,652 |
| Actual Positive |              5,878 |             52,795 |

The model generated:

```text
84,447 warnings
```

out of 121,900 test observations.

The high recall reflects the project's emphasis on identifying deterioration events rather than minimizing the total number of warnings.

---

## 15. Lead-Time Definition

Lead time was estimated using the first future hour, from one to six hours ahead, at which PM2.5 reached at least 130% of its current value.

The lead time therefore represents the difference between:

* The time at which the model generates an early warning
* The estimated first occurrence of the defined deterioration event

The lead-time analysis was performed only for test observations associated with valid deterioration events.

---

## 16. Lead-Time Results

Among successful warnings:

* Lead time ranged from 1 to 6 hours
* Mean lead time: 2.74 hours
* Median lead time: 2 hours
* 52.57% of successful warnings occurred at least 2 hours before the estimated deterioration occurrence

These results describe the timing of warnings within the project's six-hour target definition.

They should not be interpreted as a guaranteed operational warning time under real-world deployment conditions.

---

## 17. API Design Decisions

A FastAPI service was added to expose the trained model through a simple prediction endpoint.

The API provides:

```text
GET  /
GET  /health
POST /predict
```

The `/predict` endpoint accepts recent hourly observations and returns:

* Prediction timestamp
* Station
* Deterioration probability
* Warning threshold
* Early-warning decision

The API uses the saved final XGBoost model rather than retraining the model at request time.

---

## 18. API Feature Schema Validation

The API was designed to reproduce the same feature structure expected by the trained model.

The incoming request provides the raw observation variables, while calendar features such as:

* `year`
* `month`
* `day`
* `hour`

are derived from the supplied datetime.

This was necessary because these variables were part of the original model feature schema.

The API feature-engineering implementation was tested against the feature-engineering logic used during model development.

The resulting engineered dataset matched the expected:

```text
99 engineered columns
97 model input features
```

---

## 19. API Validation Decisions

The API validates several conditions before attempting prediction.

### Minimum History

At least seven hourly observations are required.

This is necessary because the feature engineering process requires historical observations for lag and rolling features.

### Consecutive Timestamps

Observations must represent consecutive hourly measurements.

This prevents invalid lag and rolling calculations caused by missing time intervals.

### Duplicate Timestamps

Duplicate timestamps are rejected to ensure that each hourly observation represents a unique point in time.

### Single Station

All observations in a prediction request must belong to the same monitoring station.

This is required because the feature engineering process is station-specific.

### Feature Compatibility

The API checks that the generated features contain the feature names expected by the final model.

This provides an additional safeguard against training-serving feature mismatches.

---

## 20. Model Persistence

The final trained model is stored as:

```text
models/xgboost_final.joblib
```

The API loads this saved model when the application starts.

This separates model training from inference and avoids retraining the model every time a prediction is requested.

---

## 21. Final Model Fitting Correction

During API and final evaluation development, an issue was identified in which the saved final XGBoost pipeline contained a fitted preprocessing component but an unfitted XGBoost estimator.

This resulted in a `NotFittedError` when the model was loaded for downstream use.

The issue was resolved by explicitly fitting the complete final pipeline on the combined 2013–2015 development data before saving it.

The corrected model was then verified to ensure that:

* The XGBoost estimator was fitted
* The saved model file existed
* The API could load the model
* Predictions could be generated successfully

No additional hyperparameter tuning was performed as part of this correction.

---

## 22. Interpretation Boundaries

The project distinguishes between **prediction** and **causal explanation**.

Feature importance and SHAP identify patterns used by the trained model, but they do not establish that a feature causes air quality deterioration.

Correlated variables may also distribute predictive information across multiple features.

Similarly, high predictive probability does not guarantee that a deterioration event will occur.

The model should therefore be interpreted as a statistical early-warning system rather than a causal environmental model.

---

## 23. Current Project Boundaries

AirShift is currently an end-to-end machine learning prototype.

The project includes:

* Data acquisition
* Data cleaning
* Feature engineering
* Event definition
* Labeling
* Model development
* Hyperparameter optimization
* Final evaluation
* Model interpretation
* Early-warning prediction
* Lead-time analysis
* FastAPI inference

The current API is intended for local inference and has not been developed as a production service with authentication, rate limiting, monitoring, or cloud deployment.

---

## 24. Key Methodological Principles

Several principles guided the project throughout development:

1. **Preserve temporal ordering**
   Future observations should not influence model development or prediction features.

2. **Avoid artificial data creation**
   Long missing-data gaps are retained rather than aggressively interpolated.

3. **Keep the test period independent**
   The final test period is reserved for final evaluation.

4. **Prioritize the project's actual objective**
   The system is evaluated as an early-warning classifier rather than only as a general-purpose classifier.

5. **Separate prediction from interpretation**
   Model explanations are not treated as causal conclusions.

6. **Keep training and inference consistent**
   The API reproduces the feature structure expected by the trained model.

7. **Make data acquisition reproducible**
   The raw dataset can be obtained through a dedicated download script rather than relying entirely on manual file placement.

---

## 25. Final Notes

AirShift evolved from a data exploration project into a complete machine learning workflow covering data acquisition, preprocessing, feature engineering, temporal modeling, model interpretation, early-warning prediction, and API deployment.

The final system provides a reproducible research and portfolio prototype for investigating short-term air quality deterioration and the potential use of machine learning for early warning.

The project remains bounded by its target definition, historical dataset, six-hour prediction horizon, and local inference setup.

Future extensions can build on this foundation without changing the core experimental results documented in the current project.
