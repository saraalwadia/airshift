# AirShift — Decisions and Notes

This document records the main methodological, modeling, and engineering decisions made during the development of AirShift.

The purpose of this document is to explain **why specific approaches were selected**, rather than repeating the complete implementation described in the project methodology.

The decisions documented here are based on the actual development process, validation results, and final model evaluation.

---

## 1. Project Scope

### Decision

AirShift was designed as an **early-warning classification system** rather than a conventional pollutant forecasting system.

The objective is to estimate whether current and recent environmental conditions indicate that a deterioration event is likely to occur within the following six hours.

### Rationale

The project focuses on the practical question of detecting an upcoming deterioration event rather than predicting the exact future concentration of an individual pollutant.

This led to a binary classification formulation in which each observation is assigned either:

* `0` — no deterioration event
* `1` — deterioration event

The resulting probability can then be converted into an early-warning decision using a selected threshold.

---

# 2. Deterioration Event Definition

## 2.1 Choice of PM2.5

### Decision

PM2.5 was selected as the primary pollutant for defining the deterioration event.

### Rationale

PM2.5 is one of the central air-quality measurements available in the dataset and provides a direct measure around which the project's deterioration definition can be constructed.

The project therefore defines deterioration in terms of a relative increase in PM2.5 rather than attempting to combine multiple pollutants into a single manually defined event score.

---

## 2.2 Relative Increase Threshold

### Decision

A deterioration event is defined as a **30% or greater increase in PM2.5** within the following six-hour prediction horizon.

Formally:

```text
Future PM2.5 >= Current PM2.5 × 1.30
```

### Rationale

A relative increase was used instead of a fixed concentration threshold so that the event definition represents a substantial change relative to the current pollution level.

The 30% threshold is a project-specific operational definition and should not be interpreted as a universal air-quality standard.

---

## 2.3 Six-Hour Prediction Horizon

### Decision

The deterioration event is evaluated over the next **1–6 hours**.

### Rationale

AirShift is intended to provide an early warning over a short operational horizon.

A six-hour horizon provides enough time to investigate whether the current environmental trajectory contains useful warning information while keeping the prediction problem focused on short-term deterioration.

---

## 2.4 Maximum Future PM2.5

### Decision

The event label is based on the **maximum PM2.5 value observed during the following 1–6 hours**.

### Rationale

Using the maximum future value allows an observation to be labeled positive if a qualifying deterioration occurs at any point within the defined prediction horizon.

This is different from checking only the PM2.5 value exactly six hours later.

---

## 2.5 Clarification of `shift(-6)`

### Note

During development, the interpretation of `shift(-6)` was explicitly corrected.

A single:

```python
shift(-6)
```

represents the value exactly **six hours later**.

It does **not** represent an event occurring at any point within the next six hours.

The final labeling approach therefore considers the complete future 1–6 hour window.

---

# 3. Missing Data Decisions

## 3.1 Short Numerical Gaps

### Decision

Short numerical missing-data gaps of up to **6 consecutive hours** were interpolated within each monitoring station.

### Rationale

Short gaps can occur between otherwise available observations in an hourly time series.

Interpolation was limited to short gaps to avoid creating artificial long-term sequences across extended periods of missing data.

---

## 3.2 Long Missing Gaps

### Decision

Long pollutant gaps greater than six hours were retained as `NaN`.

### Rationale

Long missing periods contain insufficient information to reliably reconstruct the underlying pollutant trajectory.

Filling such gaps would introduce a large amount of artificial information into the time series and could affect subsequent feature engineering and model training.

The cleaned dataset therefore preserves prolonged missingness rather than aggressively imputing it.

---

## 3.3 Wind Direction

### Decision

Missing wind-direction values were handled using forward filling within each station.

### Rationale

Wind direction is a categorical variable rather than a continuous numerical measurement.

It was therefore handled separately from the numerical pollutant and meteorological variables.

---

## 3.4 Extreme Pollution Values

### Decision

High pollutant measurements were not automatically removed as statistical outliers.

### Rationale

AirShift is specifically designed to detect deterioration in air quality.

Consequently, unusually high pollution observations may represent genuine severe pollution conditions rather than measurement errors.

Removing these observations solely because they are statistically extreme could remove important examples of the phenomenon the model is intended to detect.

---

# 4. Feature Engineering Decisions

## 4.1 Historical Features

### Decision

The model uses historical pollutant information through:

* 1-hour lags
* 3-hour lags
* 6-hour lags
* 3-hour rolling statistics
* 6-hour rolling statistics
* 1-hour changes
* 3-hour changes
* 3-hour trends
* 6-hour trends

### Rationale

The objective of AirShift is not simply to identify the current pollution level.

The project investigates whether **recent changes and temporal patterns** provide useful information about future deterioration.

These features therefore allow the model to represent both current conditions and short-term historical behavior.

---

## 4.2 Leakage Prevention in Rolling Features

### Decision

Rolling statistics were calculated using previous observations rather than including the current observation.

For example, the implementation uses:

```python
shift(1).rolling(...)
```

### Rationale

At prediction time, the model should only use information that would have been available at that prediction moment.

Including future observations would introduce temporal leakage and make model performance unreliable.

---

## 4.3 Historical Trends

### Decision

Trend features were constructed from previous observations.

The 3-hour trend uses earlier values, while the 6-hour trend is calculated from previous hourly observations.

### Rationale

The trends are intended to represent the recent direction of pollutant movement without using future information.

---

# 5. Temporal Validation Strategy

## Decision

The dataset was divided chronologically:

```text
2013–2014 → Training
2015      → Validation
2016–2017 → Final Test
```

### Rationale

AirShift is a temporal prediction problem.

A random train/test split could place observations from similar time periods on both sides of the split and would not represent the intended forecasting scenario.

The chronological split ensures that the final test period represents a later period than the data used for model development.

---

# 6. Model Development Decisions

## 6.1 Initial Model Comparison

### Decision

Three classification models were evaluated:

1. Logistic Regression
2. Random Forest
3. XGBoost

### Rationale

The project compared models with different characteristics rather than immediately assuming that one algorithm would be appropriate.

The comparison provided a baseline for evaluating the suitability of the models for the engineered tabular feature set.

---

## 6.2 Selection of XGBoost

### Decision

XGBoost was selected for further optimization and final model development.

### Rationale

During the initial model comparison, XGBoost achieved the following validation results:

| Metric    | XGBoost |
| --------- | ------: |
| Accuracy  |  0.7253 |
| Precision |  0.7118 |
| Recall    |  0.7059 |
| F1        |  0.7088 |
| ROC-AUC   |  0.8074 |
| PR-AUC    |  0.7982 |

The model was therefore taken forward to the optimization stage.

This selection refers to the project's validation results and does not imply that XGBoost is universally superior to the other algorithms.

---

# 7. XGBoost Optimization Decisions

## 7.1 Time-Series Cross-Validation

### Decision

`TimeSeriesSplit` with three splits was used during XGBoost hyperparameter optimization.

### Rationale

Random cross-validation would not preserve temporal ordering.

Time-series cross-validation provides a validation structure that is more consistent with the temporal nature of the problem.

---

## 7.2 Randomized Search

### Decision

`RandomizedSearchCV` was used to search the XGBoost hyperparameter space.

The search evaluated:

* 15 parameter configurations
* 3 time-series folds
* 45 total fits

### Rationale

The search explored multiple combinations of model parameters without exhaustively evaluating every possible combination.

---

## 7.3 Optimization Metric

### Decision

Average Precision (`average_precision`) was used as the optimization scoring metric.

### Rationale

The project evaluates a binary deterioration event and uses precision-recall analysis as part of model evaluation.

Average Precision was therefore selected as the optimization objective during hyperparameter search.

The best cross-validation PR-AUC was approximately:

```text
0.8324
```

---

## 7.4 Final Tuned Hyperparameters

The selected configuration was:

```text
n_estimators      = 400
learning_rate     = 0.1
max_depth         = 6
min_child_weight  = 3
subsample         = 0.7
colsample_bytree  = 1.0
```

These parameters were then used to train the final XGBoost model.

---

# 8. Final Model Training Decision

## Decision

After model development and tuning, the final XGBoost model was retrained using the combined **2013–2014 training data and 2015 validation data**.

The final training dataset contained:

```text
296,481 observations
97 model input features
```

The 2016–2017 test period was kept separate.

### Rationale

Once model development and hyperparameter selection were completed, the available pre-test data could be combined to train the final model before evaluating it on the untouched test period.

This preserves the role of the final test period as an independent evaluation period.

---

# 9. Final Test Evaluation

## Decision

The final model was evaluated on the chronological test period:

```text
2016-01-01 → 2017-02-28 17:00
```

### Rationale

The final test period was not used for:

* model selection
* hyperparameter tuning
* final training
* warning-threshold selection

This provides a cleaner estimate of how the finalized model performs on later observations.

---

## Final Test Results

The final XGBoost model achieved:

| Metric    | Final Test |
| --------- | ---------: |
| Accuracy  |     0.7368 |
| Precision |     0.7244 |
| Recall    |     0.7315 |
| F1        |     0.7279 |
| ROC-AUC   |     0.8215 |
| PR-AUC    |     0.8186 |

The test set contained:

```text
121,900 observations
```

These results are treated as the final model evaluation rather than as a basis for further tuning.

---

# 10. Feature Importance Decisions

## Decision

Built-in XGBoost feature importance was used as an initial model-interpretation method.

### Rationale

The final XGBoost model provides feature-importance information based on how features are used within its learned decision trees.

This provides an initial view of which features the model relies on most frequently.

The strongest feature by this measure was:

```text
PM2.5_lag_1h
```

with an importance score of approximately:

```text
0.209936
```

---

## Interpretation Note

Feature importance was not treated as a causal analysis.

A high importance score indicates that a feature is useful to the trained model, but it does not establish that the feature causes air-quality deterioration.

Correlated features may also distribute predictive information across multiple variables.

---

# 11. SHAP Interpretation Decision

## Decision

SHAP was added after built-in feature importance to investigate the magnitude and direction of feature contributions.

### Rationale

Built-in feature importance does not directly show whether a feature pushes an individual prediction toward a higher or lower deterioration probability.

SHAP provides additional information about the contribution of feature values to model predictions.

---

## SHAP Analysis Configuration

The final model was evaluated using:

```text
Test observations: 121,900
SHAP sample: 5,000
Random seed: 42
```

The transformed feature space contained:

```text
123 features
```

because the categorical variables were one-hot encoded during preprocessing.

---

## Main SHAP Findings

The highest global mean absolute SHAP importance included:

| Feature         | Mean Absolute SHAP |
| --------------- | -----------------: |
| PM2.5           |           0.858137 |
| PM2.5_lag_1h    |           0.391194 |
| hour            |           0.374115 |
| WSPM            |           0.263583 |
| month           |           0.261140 |
| TEMP            |           0.224092 |
| PM2.5_change_1h |           0.164035 |

The analysis indicated that current and recent PM2.5 information had substantial influence on the model predictions.

The SHAP analysis also showed directional patterns for some variables, including higher recent PM2.5 and short-term PM2.5 increases tending to contribute toward higher predicted deterioration probability in the evaluated sample.

These findings describe model behavior and are not causal conclusions.

---

# 12. Early-Warning Threshold Decision

## Decision

The final early-warning threshold was set to:

```text
0.30
```

### Rationale

AirShift is intended to function as an early-warning system.

For this purpose, missing a deterioration event is particularly important because a false negative represents an event for which the system did not issue a warning.

The validation results showed the trade-off between precision and recall at different thresholds.

For example:

| Threshold | Precision | Recall |     F1 |
| --------: | --------: | -----: | -----: |
|      0.30 |    0.6201 | 0.8813 | 0.7280 |
|      0.40 |    0.6650 | 0.8046 | 0.7281 |
|      0.50 |    0.7112 | 0.7106 | 0.7109 |
|      0.60 |    0.7617 | 0.6041 | 0.6738 |
|      0.70 |    0.8169 | 0.4881 | 0.6111 |

The threshold of 0.30 was selected because the early-warning objective places greater emphasis on maintaining high recall and reducing missed deterioration events.

The threshold was selected using the validation period rather than the final test set.

---

# 13. Early-Warning Test Results

Using the 0.30 threshold on the final test period produced:

| Metric    | Warning Mode |
| --------- | -----------: |
| Precision |       0.6252 |
| Recall    |       0.8998 |
| F1        |       0.7378 |

The resulting confusion matrix was:

|                    | Actual Negative | Actual Positive |
| ------------------ | --------------: | --------------: |
| Predicted Negative |          31,575 |           5,878 |
| Predicted Positive |          31,652 |          52,795 |

This threshold therefore increased recall substantially compared with the default 0.50 classification threshold, while also producing more false-positive warnings.

This trade-off is a consequence of the selected warning threshold.

---

# 14. Lead-Time Definition

## Decision

For lead-time analysis, the estimated deterioration occurrence time was defined as the **earliest future hour between 1 and 6 hours** at which PM2.5 reached the deterioration threshold.

### Rationale

The project needs a consistent definition of when a deterioration event is considered to occur in order to estimate the time between a warning and the event.

The earliest qualifying future hour provides a concrete reference point within the six-hour event horizon.

---

# 15. Lead-Time Results

For the final test period:

```text
Positive labels: 58,673
Positive labels with occurrence time: 58,650
Successful warnings: 52,786
```

The successful-warning lead times were:

| Lead Time |  Count | Percentage |
| --------: | -----: | ---------: |
|    1 hour | 15,677 |     29.70% |
|   2 hours | 12,072 |     22.87% |
|   3 hours |  8,937 |     16.93% |
|   4 hours |  6,770 |     12.83% |
|   5 hours |  5,247 |      9.94% |
|   6 hours |  4,083 |      7.74% |

Summary:

* Mean lead time: **2.7364 hours**
* Median lead time: **2 hours**
* Range: **1–6 hours**
* 52.57% of successful warnings occurred at least 2 hours before the estimated deterioration occurrence.

### Interpretation Note

The mean lead time of approximately 2.74 hours should **not** be presented as a guaranteed operational warning duration.

It describes the observed timing of successful warnings relative to the project's six-hour deterioration definition.

---

# 16. API Design Decisions

## 16.1 Minimum Seven Observations

### Decision

The `/predict` endpoint requires at least seven hourly observations.

### Rationale

The feature-engineering pipeline requires historical information up to six hours before the prediction point.

Seven observations provide the current observation plus the preceding six hourly observations needed for the maximum lag requirement.

---

## 16.2 Consecutive Hourly Observations

### Decision

The API rejects observations that are not consecutive hourly measurements.

### Rationale

The lag and rolling features assume that adjacent rows represent adjacent hours.

If an hour is missing, a row-based six-step lag would no longer represent a six-hour temporal interval.

The API therefore checks timestamp continuity before feature generation.

---

## 16.3 Single Station per Request

### Decision

All observations in one `/predict` request must belong to the same monitoring station.

### Rationale

The feature-engineering process groups historical calculations by station.

Mixing observations from different stations within a single request could produce invalid temporal features.

The API therefore validates station consistency before generating features.

---

## 16.4 Duplicate Timestamp Validation

### Decision

Duplicate timestamps are rejected.

### Rationale

Duplicate timestamps would violate the expected hourly time-series structure and could produce ambiguous historical features.

---

## 16.5 Reusing Feature Engineering

### Decision

The API uses the same feature-engineering logic developed for the modeling pipeline.

### Rationale

The model was trained using a specific set of engineered features.

Reimplementing the feature logic differently inside the API could cause a mismatch between training-time and inference-time features.

The API therefore reuses the project feature-engineering implementation.

---

# 17. API Feature-Schema Validation

## Decision

The API explicitly checks that the generated feature columns match the features expected by the saved final model.

### Rationale

The final model expects:

```text
97 model input features
```

The API verifies that these features are available before prediction.

This check was especially important during development because the API initially failed to generate the original `year` and `day` model features from the supplied `datetime`.

The API was subsequently updated to derive:

```text
year
month
day
hour
```

from the request's `datetime` values before feature engineering.

---

# 18. API Validation Decisions

A dedicated API test script was created to validate both successful prediction and input errors.

The implemented validation tests cover:

1. Valid prediction
2. Fewer than seven observations
3. Non-consecutive timestamps
4. Duplicate timestamps
5. Multiple stations

All five validation scenarios produced the expected results.

The valid prediction test returned:

```text
HTTP 200
```

while the invalid-input tests returned:

```text
HTTP 400
```

for the corresponding validation errors.

---

# 19. Model Persistence Decision

## Decision

The final fitted XGBoost pipeline is saved as:

```text
models/xgboost_final.joblib
```

### Rationale

Saving the fitted pipeline allows the API to load the trained model directly without repeating model training or preprocessing fitting.

The saved model includes the fitted preprocessing stage and trained XGBoost estimator.

This makes the model available for inference through the FastAPI service.

---

# 20. Important Development Correction: Final Model Fitting

## Issue

During development of the final evaluation and interpretation notebooks, the saved `xgboost_final.joblib` file initially contained a fitted preprocessing component but an unfitted XGBoost estimator.

This caused a `NotFittedError` when the model was loaded for later analysis.

## Decision

The final model was retrained using the already selected XGBoost hyperparameters and the combined training and validation data.

No additional hyperparameter search was performed.

## Result

The corrected final model was successfully verified as fitted and saved again.

The resulting model file was approximately:

```text
1.74 MB
```

This correction ensured that the final evaluation, feature-importance analysis, SHAP analysis, and API all use a properly fitted model.

---

# 21. Interpretation Boundaries

Several results in AirShift are deliberately treated as model interpretation rather than causal conclusions.

### Feature importance

A feature's importance indicates its usefulness to the trained model.

It does not prove that the feature causes deterioration.

### SHAP

SHAP explains how feature values contribute to model predictions.

It does not establish causal relationships.

### Lead time

Lead time describes the timing of successful predictions relative to the project's event definition.

It does not guarantee that the system would provide the same warning duration in a real-world deployment.

### Test performance

The final test metrics describe performance on the selected Beijing dataset and test period.

They should not automatically be interpreted as expected performance on another city, sensor network, or environmental setting.

---

# 22. Current Project Boundaries

AirShift currently represents a research and portfolio implementation rather than a production air-quality warning service.

The current implementation does not include:

* Real-time external sensor integration
* Production deployment infrastructure
* Authentication
* Rate limiting
* Production monitoring
* Automated model retraining

These are future engineering possibilities rather than completed project components.

---

# 23. Key Methodological Principles

The following principles guided the development of AirShift:

### 1. Preserve temporal structure

Future observations should not influence model development or feature generation.

### 2. Avoid unnecessary imputation

Short gaps can be interpolated, while prolonged gaps are preserved as missing.

### 3. Treat severe pollution as meaningful

Extreme pollution values are potentially important deterioration observations rather than automatic outliers.

### 4. Separate development from final testing

The final test period remains separate from model selection, hyperparameter tuning, final training, and threshold selection.

### 5. Distinguish prediction from causality

Model importance and SHAP results describe learned predictive relationships rather than causal effects.

### 6. Keep inference consistent with training

The API reuses the same feature-engineering logic and saved preprocessing/model pipeline.

---

# 24. Final Notes

AirShift evolved from a conventional air-quality prediction idea into a more specific early-warning classification problem.

The final system combines:

```text
Historical Environmental Data
          ↓
Temporal Feature Engineering
          ↓
Deterioration Event Definition
          ↓
Chronological Model Development
          ↓
XGBoost Optimization
          ↓
Independent Test Evaluation
          ↓
Model Interpretation
          ↓
Early-Warning Threshold
          ↓
Lead-Time Evaluation
          ↓
FastAPI Inference
```

The main methodological decisions documented here were made to preserve the temporal nature of the problem, reduce leakage risk, maintain consistency between training and inference, and align the final prediction system with the project's early-warning objective.
