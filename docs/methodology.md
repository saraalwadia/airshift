# AirShift — Methodology

## 1. Overview

AirShift is an early-warning machine learning system designed to identify short-term air quality deterioration from historical air quality and meteorological observations.

The project formulates air quality deterioration as a **binary classification problem** rather than directly forecasting a future pollutant concentration.

For each hourly observation, the model estimates the probability that a defined PM2.5 deterioration event will occur within the following six hours.

The complete methodology consists of:

```text
Data Understanding
        ↓
Data Cleaning
        ↓
Feature Engineering
        ↓
Deterioration Event Definition
        ↓
Target Labeling
        ↓
Temporal Model Development
        ↓
XGBoost Optimization
        ↓
Final Test Evaluation
        ↓
Model Interpretation
        ↓
Early Warning Threshold
        ↓
Lead-Time Evaluation
        ↓
API Deployment
```

---

# 2. Data Understanding

## 2.1 Dataset

AirShift uses the Beijing Multi-Site Air Quality Dataset.

The dataset contains hourly observations from **12 monitoring stations** covering:

**March 2013 to February 2017**

Across all stations, the dataset contains:

* **420,768 observations**
* **18 original variables**
* Hourly temporal resolution

The variables include six air pollutants, meteorological measurements, temporal information, and station identifiers.

### Air pollutants

* `PM2.5`
* `PM10`
* `SO2`
* `NO2`
* `CO`
* `O3`

### Meteorological variables

* `TEMP`
* `PRES`
* `DEWP`
* `RAIN`
* `wd`
* `WSPM`

### Temporal and identification variables

* `No`
* `year`
* `month`
* `day`
* `hour`
* `station`

---

## 2.2 Structural Validation

The initial data-understanding stage examined the structure and temporal consistency of the station datasets.

The following checks were performed:

* Dataset dimensions
* Column names and data types
* Station count
* Temporal coverage
* Missing values
* Duplicate observations
* Hourly timestamp continuity
* Long missing-data periods
* Potential invalid values
* Extreme pollutant observations

Each station contained **35,064 hourly observations**, and the station datasets covered the same overall period.

No duplicate rows or temporal timestamp gaps were identified during the initial validation.

---

## 2.3 Missing-Data Assessment

Missing values were examined by feature and station rather than treating all missing values in the same way.

For example, in the Aotizhongxin station, missing observations were found across several pollutant and meteorological variables.

Some missing periods were short, while others formed prolonged gaps.

The longest missing blocks included substantial gaps in:

* `CO`
* `NO2`
* `O3`
* `SO2`
* `PM2.5`
* `PM10`

This distinction between short and prolonged gaps was important for the cleaning strategy.

---

# 3. Data Cleaning

## 3.1 Combining Stations

The station-level datasets were combined into one unified dataset containing all 12 monitoring stations.

A station identifier was retained so that temporal operations could be performed independently within each station.

The combined raw dataset contained:

**420,768 observations × 18 original columns**

---

## 3.2 Datetime Construction

The original temporal components:

```text
year
month
day
hour
```

were combined into a single `datetime` column.

This created a consistent timestamp representation for temporal sorting, validation, feature engineering, and model development.

The cleaned dataset therefore contained **19 columns**, including the new `datetime` variable.

---

## 3.3 Data-Type Validation

The data types were reviewed to ensure that:

* Temporal components were numeric.
* Pollutant measurements were numerical.
* Meteorological measurements were numerical.
* `wd` and `station` were categorical/string variables.
* `datetime` was stored as a datetime type.

No unnecessary data-type conversions were required after validation.

---

## 3.4 Invalid-Value Checks

Negative values were checked for variables where negative measurements are physically invalid.

The following variables had no invalid negative values after validation:

* `PM2.5`
* `PM10`
* `SO2`
* `NO2`
* `CO`
* `O3`
* `PRES`
* `RAIN`
* `WSPM`

Temperature was treated differently because negative temperatures can occur naturally and therefore were not considered invalid solely because they were below zero.

---

## 3.5 Short Missing-Data Gaps

Short numerical missing gaps of up to **six hours** were interpolated within each monitoring station.

The objective was to recover short gaps while avoiding the creation of artificial values across prolonged missing periods.

A total of approximately **4,006 pollutant values** were interpolated during this process.

---

## 3.6 Long Missing-Data Gaps

Prolonged pollutant gaps were **not** artificially interpolated.

Instead, missing values in long gaps were retained as `NaN`.

This was important because interpolating across long periods could introduce artificial pollution patterns that were not supported by observations.

After cleaning, approximately:

**14,654 pollutant values**

remained missing, representing approximately **3.48%** of the relevant observations.

---

## 3.7 Wind Direction

Missing wind-direction values were handled using forward filling within each station.

Wind direction was treated as a categorical variable rather than interpolated numerically.

---

## 3.8 Temporal Validation

After cleaning, the dataset was checked again for:

* Duplicate rows
* Station-level chronological ordering
* Hourly temporal consistency

The temporal structure remained consistent after cleaning.

---

# 4. Feature Engineering

## 4.1 Objective

The purpose of feature engineering was to represent recent pollution behavior and environmental context using information available at the prediction time.

The features were designed to capture:

* Current pollutant levels
* Recent pollutant levels
* Short-term changes
* Rolling pollution behavior
* Recent trends
* Temporal patterns
* Meteorological conditions
* Station and wind-direction effects

---

## 4.2 Feature Count

The feature-engineering stage produced:

**99 total columns**

This included the original variables and newly engineered features.

After excluding non-model fields such as:

* `No`
* `datetime`
* target variable

the final model used:

**97 input features**

Two categorical variables were included:

* `wd`
* `station`

The remaining model inputs were numerical.

---

## 4.3 Temporal Features

The following temporal features were added:

* `day_of_week`
* `is_weekend`

Existing temporal variables such as:

* `year`
* `month`
* `day`
* `hour`

were retained.

These features allow the model to capture recurring temporal patterns in air quality.

---

## 4.4 Lag Features

For each of the six pollutants, lagged values were generated for:

* 1 hour
* 3 hours
* 6 hours

This produced:

**6 pollutants × 3 lag periods = 18 lag features**

Lag features provide the model with information about recent pollutant conditions without using future observations.

---

## 4.5 Rolling Statistics

For each pollutant, rolling statistics were calculated over:

* 3 hours
* 6 hours

For each window, the following statistics were calculated:

* Mean
* Maximum
* Standard deviation

This produced:

**6 pollutants × 2 windows × 3 statistics = 36 rolling features**

The rolling calculations were shifted so that only previous observations contributed to the current feature.

This prevented the current observation from leaking into its own historical rolling statistics.

---

## 4.6 Short-Term Changes

For each pollutant, changes over:

* 1 hour
* 3 hours

were calculated.

This produced:

**6 pollutants × 2 change periods = 12 change features**

These features represent recent increases or decreases in pollutant concentration.

---

## 4.7 Trend Features

Trend features were calculated over:

* 3 hours
* 6 hours

for each pollutant.

This produced:

**6 pollutants × 2 trend windows = 12 trend features**

The trends were constructed using historical observations only.

---

## 4.8 Leakage Prevention

Preventing future-data leakage was a central methodological requirement.

The feature-engineering process therefore follows the principle:

> **At prediction time, every model feature must be computable using information available at or before that prediction timestamp.**

For example, rolling statistics use shifted historical observations rather than including future observations.

Future PM2.5 values are used only when constructing the target label, not as model inputs.

---

# 5. Deterioration Event Definition

## 5.1 Event Concept

AirShift defines deterioration as a substantial short-term increase in PM2.5.

The event threshold was set to:

**30% increase**

within a:

**6-hour future horizon**

The event is based on the maximum PM2.5 value observed during the following one to six hours.

---

## 5.2 Mathematical Definition

Let:

* \(PM_{t}\) be the current PM2.5 value.
* \(PM_{t+k}\) be the PM2.5 value \(k\) hours later.

For:

$$
k \in \{1,2,3,4,5,6\}
$$

the deterioration event is defined as:

$$
\max(PM_{t+1}, ..., PM_{t+6})
\geq 1.30 \times PM_t
$$

The resulting target is binary:

```text
1 → deterioration event
0 → no deterioration event
```

---

## 5.3 Important Temporal Detail

The event definition uses the **maximum value across the next six hours**, rather than requiring the increase to occur exactly six hours later.

This distinction is important because the deterioration may occur at any point between one and six hours after the current observation.

---

# 6. Target Labeling

## 6.1 Future Window

A complete six-hour future window is required to determine whether the deterioration event occurs.

Therefore, observations without sufficient future information cannot receive a reliable target label.

---

## 6.2 Final Labeled Dataset

After target construction:

* **418,381 observations** had valid labels.
* **219,985** were non-deterioration observations.
* **198,396** were deterioration observations.

Class distribution:

| Class                |       Count | Percentage |
| -------------------- | ----------: | ---------: |
| 0 — No deterioration |     219,985 |     52.58% |
| 1 — Deterioration    |     198,396 |     47.42% |
| **Total**            | **418,381** |   **100%** |

This produced a relatively balanced binary classification problem.

---

# 7. Temporal Model Development

## 7.1 Why a Temporal Split?

AirShift is a time-series problem.

A random train/test split could allow observations from later periods to appear in training while earlier periods are used for validation, making the evaluation less representative of future deployment.

The project therefore uses chronological splits.

---

## 7.2 Development and Test Periods

The data was divided as follows:

| Dataset        | Period    |
| -------------- | --------- |
| Model training | 2013–2014 |
| Validation     | 2015      |
| Final test     | 2016–2017 |

The final test period was kept completely separate from model development and hyperparameter optimization.

---

## 7.3 Initial Models

Three classification algorithms were evaluated:

### Logistic Regression

Used as a linear baseline for the binary classification task.

### Random Forest

Used as a tree-based ensemble model capable of representing nonlinear relationships.

### XGBoost

Used as a gradient-boosted tree model and selected for further optimization after the initial model comparison.

---

# 8. XGBoost Optimization

## 8.1 Baseline

The initial XGBoost model used:

```text
n_estimators = 200
learning_rate = 0.05
max_depth = 6
```

The baseline validation results were:

| Metric    | Baseline |
| --------- | -------: |
| Accuracy  |   0.7253 |
| Precision |   0.7118 |
| Recall    |   0.7059 |
| F1        |   0.7088 |
| ROC-AUC   |   0.8074 |
| PR-AUC    |   0.7982 |

---

## 8.2 Hyperparameter Search

XGBoost hyperparameters were optimized using:

* `RandomizedSearchCV`
* `TimeSeriesSplit`
* 3 temporal folds
* 15 sampled configurations
* 45 total model fits

The optimization metric was:

**Average Precision**

The search considered:

* Number of estimators
* Learning rate
* Maximum tree depth
* Minimum child weight
* Subsampling ratio
* Feature subsampling ratio

---

## 8.3 Selected Hyperparameters

The best configuration obtained during the search was:

```text
n_estimators = 400
learning_rate = 0.1
max_depth = 6
min_child_weight = 3
subsample = 0.7
colsample_bytree = 1.0
```

The best cross-validation PR-AUC was approximately:

**0.8324**

---

## 8.4 Tuned Validation Performance

The tuned model achieved:

| Metric    | Tuned Validation |
| --------- | ---------------: |
| Accuracy  |           0.7279 |
| Precision |           0.7125 |
| Recall    |           0.7134 |
| F1        |           0.7129 |
| ROC-AUC   |           0.8102 |
| PR-AUC    |           0.8015 |

The tuned model was subsequently used as the basis for final training.

---

# 9. Final Model Training

After model development and tuning were completed, the final XGBoost model was retrained using:

* 2013–2014 training data
* 2015 validation data

Combined:

**296,481 training observations**

The 2016–2017 test set remained untouched during this final training stage.

The final model was saved as:

```text
models/xgboost_final.joblib
```

The saved model was verified to contain a fitted XGBoost estimator and fitted preprocessing pipeline.

---

# 10. Final Test Evaluation

## 10.1 Test Set

The final test set contains:

**121,900 observations**

covering:

**2016-01-01 to 2017-02-28 17:00**

The test set was not used for:

* Model selection
* Hyperparameter tuning
* Threshold selection
* Final model training

---

## 10.2 Standard Classification Threshold

At the standard classification threshold of 0.50, the final model achieved:

| Metric    | Final Test |
| --------- | ---------: |
| Accuracy  |     0.7368 |
| Precision |     0.7244 |
| Recall    |     0.7315 |
| F1        |     0.7279 |
| ROC-AUC   |     0.8215 |
| PR-AUC    |     0.8186 |

---

## 10.3 Confusion Matrix

The standard 0.50 threshold produced:

|          | Predicted 0 | Predicted 1 |
| -------- | ----------: | ----------: |
| Actual 0 |      46,896 |      16,331 |
| Actual 1 |      15,756 |      42,917 |

Therefore:

* True Negatives: **46,896**
* False Positives: **16,331**
* False Negatives: **15,756**
* True Positives: **42,917**

---

# 11. Model Interpretation

Two complementary interpretation approaches were used.

## 11.1 Built-in XGBoost Feature Importance

The final XGBoost model provides built-in feature importance scores based on feature usage within the learned trees.

The preprocessing pipeline expands the original 97 model inputs into **123 processed features**, primarily because categorical variables are one-hot encoded.

The strongest built-in feature importance was:

```text
PM2.5_lag_1h
```

with an importance value of approximately:

**0.2099**

Other highly ranked processed features included wind-direction categories, current PM2.5, PM10 lag, RAIN, hour, short-term pollutant changes, WSPM, and rolling statistics.

---

## 11.2 SHAP Analysis

SHAP was used to investigate how individual features contribute to model predictions.

The analysis used:

* Final trained XGBoost model
* Final test data
* A sample of **5,000 test observations**
* Random seed: `42`
* `TreeExplainer`

The transformed test data contained:

**123 model features**

The highest mean absolute SHAP contributions included:

| Feature         | Mean Absolute SHAP |
| --------------- | -----------------: |
| PM2.5           |             0.8581 |
| PM2.5_lag_1h    |             0.3912 |
| hour            |             0.3741 |
| WSPM            |             0.2636 |
| month           |             0.2611 |
| TEMP            |             0.2241 |
| PM2.5_change_1h |             0.1640 |
| DEWP            |             0.1617 |
| PM2.5_change_3h |             0.1253 |
| PRES            |             0.1074 |

SHAP provides information about the contribution and direction of features for individual predictions, while built-in feature importance primarily describes how strongly features are used by the model.

Neither method establishes a causal relationship.

---

# 12. Early Warning Threshold

## 12.1 Motivation

The standard classification threshold of 0.50 is not necessarily appropriate for an early-warning application.

Missing a true deterioration event can be particularly important in an early-warning context.

Therefore, a separate threshold-selection procedure was performed using the validation period.

---

## 12.2 Threshold Selection

A separate model using the same tuned XGBoost hyperparameters was trained on the 2013–2014 development period and evaluated on 2015.

Candidate thresholds from:

```text
0.30 → 0.70
```

were evaluated.

The selected threshold was:

**0.30**

The selection was made based on the early-warning objective and the need to prioritize detection of deterioration events.

The final test set was not used to select this threshold.

---

## 12.3 Validation Results at 0.30

| Metric          | Validation |
| --------------- | ---------: |
| Precision       |     0.6201 |
| Recall          |     0.8813 |
| F1              |     0.7280 |
| False Positives |     26,795 |
| False Negatives |      5,894 |

---

# 13. Final Early Warning Evaluation

The final trained model was evaluated on the held-out test set using the 0.30 threshold.

Results:

| Metric    | Early Warning Test |
| --------- | -----------------: |
| Precision |             0.6252 |
| Recall    |             0.8998 |
| F1        |             0.7378 |

The resulting confusion matrix was:

|                         | Predicted No Warning | Predicted Warning |
| ----------------------- | -------------------: | ----------------: |
| Actual No Deterioration |               31,575 |            31,652 |
| Actual Deterioration    |                5,878 |            52,795 |

This threshold changes the operating point of the classifier by increasing the number of observations classified as warnings.

---

# 14. Warning Lead-Time Evaluation

## 14.1 Purpose

Model classification performance alone does not indicate when a warning occurs relative to the deterioration event.

AirShift therefore includes a separate lead-time analysis.

---

## 14.2 Occurrence Time

For each positive deterioration event, the occurrence time is defined as the **earliest future hour from 1 to 6** at which:

$$
PM2.5_{t+k} \geq 1.30 \times PM2.5_t
$$

This provides an estimated occurrence timestamp for the defined event.

---

## 14.3 Lead-Time Results

For successful warnings:

* Minimum lead time: **1 hour**
* Maximum lead time: **6 hours**
* Mean: **2.7364 hours**
* Median: **2 hours**

Distribution:

| Lead Time |  Count | Percentage |
| --------- | -----: | ---------: |
| 1 hour    | 15,677 |     29.70% |
| 2 hours   | 12,072 |     22.87% |
| 3 hours   |  8,937 |     16.93% |
| 4 hours   |  6,770 |     12.83% |
| 5 hours   |  5,247 |      9.94% |
| 6 hours   |  4,083 |      7.74% |

Overall, **52.57%** of successful warnings occurred at least two hours before the estimated event occurrence.

These results describe lead time according to the project's event-definition methodology and should not be interpreted as a guaranteed operational warning duration.

---

# 15. API Deployment

The final model was integrated into a FastAPI application.

The API loads the saved:

```text
models/xgboost_final.joblib
```

model at application startup.

## 15.1 Prediction Workflo
