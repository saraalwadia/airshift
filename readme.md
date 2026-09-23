# 🌬️ AirShift

## Early Warning System for Air Quality Deterioration

AirShift is a machine learning project that aims to detect **early warning signals of significant air quality deterioration** before severe pollution episodes occur.

Instead of simply predicting future air pollution levels, AirShift focuses on identifying whether the current environmental conditions and recent pollution trends indicate that air quality is likely to deteriorate within the next several hours.

---

## 🎯 Project Objective

The main objective of AirShift is to develop an ML-powered early warning system that can answer:

> **Can we detect early warning signals that air quality is about to deteriorate?**

The system will analyze historical air quality and meteorological patterns and predict the probability of a future deterioration event.

---

## 💡 Key Idea

Traditional air quality prediction systems often focus on forecasting pollutant concentrations.

AirShift takes a different approach:

```text
Current & Historical Conditions
            ↓
     Trend Analysis
            ↓
    Feature Engineering
            ↓
 Future Deterioration Event
            ↓
      ML Prediction
            ↓
     Early Warning Risk
```

The project will also investigate **warning lead time** — how many hours before a deterioration event the model can provide a useful warning.

---

## 🔄 Project Workflow

The AirShift pipeline is organized into several stages:

```text
Raw Data
   ↓
Data Profiling & Understanding
   ↓
Data Cleaning
   ↓
Feature Engineering
   ↓
Deterioration Event Definition
   ↓
Model Development
   ↓
Early Warning Prediction
   ↓
Warning Lead Time Evaluation
```

### 1. Data Profiling & Understanding

The raw Beijing Multi-Site Air Quality dataset was examined to understand its structure, quality, and temporal characteristics before applying any cleaning procedures.

The profiling stage included:

* Inspecting the structure and dimensions of the dataset
* Validating the 12 monitoring stations
* Checking temporal coverage and continuity
* Analyzing missing values by feature, row, station, and time period
* Identifying prolonged missing-data gaps
* Reviewing potential invalid values and extreme observations

This stage provided the basis for defining the data cleaning strategy.

### 2. Data Cleaning

The cleaning stage prepares the dataset for subsequent feature engineering and machine learning while preserving the original raw data.

The cleaning process included:

* Combining data from all monitoring stations
* Creating a unified `datetime` column
* Validating data types and column structure
* Checking for invalid negative values
* Interpolating short numerical gaps of up to 6 hours
* Handling missing wind direction values using forward filling within each station
* Retaining prolonged pollutant gaps as `NaN` rather than creating artificial values
* Validating duplicates and temporal consistency
* Saving the cleaned dataset separately from the raw data

The cleaned dataset contains **420,768 observations across 12 monitoring stations** covering **March 2013 to February 2017**.


### 3. Feature Engineering

The feature engineering stage transforms the cleaned air quality data into meaningful temporal and historical features for the early warning machine learning task.

The feature engineering process included:

* Creating time-based features such as day of the week and weekend indicators

* Creating lag features for pollutant variables using 1-hour, 3-hour, and 6-hour intervals

* Creating rolling mean, maximum, and standard deviation features using previous 3-hour and 6-hour windows

* Creating pollutant change features using 1-hour and 3-hour intervals

* Creating short-term pollutant trend features using previous 3-hour and 6-hour windows

* Ensuring that temporal features use only information available at or before each observation

The feature engineering stage created **80 new features**, resulting in a dataset with **99 columns** and **420,768 observations**.

These features provide information about recent pollution conditions, temporal patterns, changes, and short-term trends that may help identify early warning signals of future air quality deterioration.


### 4. Deterioration Event Definition

The deterioration event definition stage establishes a clear and measurable definition of future air quality deterioration for the AirShift early warning task.

The analysis focused on:

* Selecting **PM2.5** as the primary pollutant for defining deterioration

* Evaluating different deterioration thresholds to identify a meaningful increase in PM2.5

* Evaluating different future time horizons for short-term early warning

* Selecting a **30% or greater increase in PM2.5 within the following 6 hours** as the initial deterioration-event definition

The selected definition provides a reasonable balance between detecting meaningful short-term increases and maintaining a sufficient number of potential deterioration events.

No target labels are created at this stage. The selected event definition is applied in the following labeling stage.

### 5. Labeling

The labeling stage applies the predefined deterioration-event definition to create the binary target variable required for machine learning.

The labeling process included:

* Calculating the maximum PM2.5 concentration within the following 6 hours for each monitoring station

* Comparing the future maximum PM2.5 value with the current PM2.5 concentration

* Assigning a deterioration label of `1` when PM2.5 increases by **30% or more** within the future 6-hour window

* Assigning a label of `0` when the deterioration threshold is not reached

* Using only observations with a complete 6-hour future PM2.5 window to ensure reliable target labels

* Removing observations for which a reliable deterioration label could not be determined

The final labeled dataset contains **418,381 valid observations across 12 monitoring stations** and **100 columns**.

A total of **2,387 observations (0.57%)** were excluded because sufficient future PM2.5 information was not available to determine the deterioration event reliably.

Among the valid observations, **47.42%** are classified as deterioration events and **52.58%** as non-deterioration events, resulting in a relatively balanced binary target.

The future-derived variables used only for target construction were removed from the final dataset to prevent accidental data leakage during model development.

### 6. Model Development

The model development stage compares multiple machine learning algorithms for the AirShift early warning task.

Three candidate models were evaluated using a chronological validation strategy:

* Logistic Regression
* Random Forest
* XGBoost

The models were evaluated using Accuracy, Precision, Recall, F1-score, ROC-AUC, and PR-AUC.

**XGBoost achieved the strongest overall performance** across most evaluation metrics and was selected for further development and hyperparameter tuning.

Logistic Regression achieved the highest Recall, while XGBoost provided a stronger overall balance between Precision, Recall, F1-score, ROC-AUC, and PR-AUC.

### 7. XGBoost Optimization

The XGBoost model was further optimized using time-aware hyperparameter tuning.

The tuning process included:

* Using **TimeSeriesSplit** with 3 chronological folds

* Testing 15 XGBoost configurations using `RandomizedSearchCV`

* Optimizing based on **PR-AUC**

* Evaluating `n_estimators`, `learning_rate`, `max_depth`, `min_child_weight`, `subsample`, and `colsample_bytree`

The best configuration achieved a cross-validation **PR-AUC of 0.8324**.

The selected configuration was:

* `n_estimators`: 400
* `learning_rate`: 0.10
* `max_depth`: 6
* `min_child_weight`: 3
* `subsample`: 0.70
* `colsample_bytree`: 1.00

On the held-out 2015 validation period, the tuned XGBoost model achieved:

| Metric    |  Score |
| --------- | -----: |
| Accuracy  | 0.7279 |
| Precision | 0.7125 |
| Recall    | 0.7134 |
| F1-score  | 0.7129 |
| ROC-AUC   | 0.8102 |
| PR-AUC    | 0.8015 |

Compared with the baseline XGBoost model, hyperparameter tuning improved all evaluated metrics, with the largest improvement in **Recall (+0.0075)**.

The selected configuration was retrained using the combined **2013–2015 training and validation data** and saved as the final XGBoost model for evaluation on the unseen 2016–2017 test period.

### 8. Final Test Evaluation

The final XGBoost model was evaluated on the unseen **2016–2017 test period**.

| Metric    | Test Result |
| --------- | ----------: |
| Accuracy  |  **0.7368** |
| Precision |  **0.7244** |
| Recall    |  **0.7315** |
| F1-score  |  **0.7279** |
| ROC-AUC   |  **0.8215** |
| PR-AUC    |  **0.8186** |

The model achieved a PR-AUC of **0.8186**, indicating meaningful predictive performance for identifying deterioration events beyond the positive-class prevalence of approximately 48%.

---

### 9. Feature Importance

Feature importance analysis was performed using the trained XGBoost model.

The most important features included:

* `PM2.5_lag_1h`
* `PM2.5`
* `PM10_lag_1h`
* Wind direction categories
* `RAIN`
* `hour`
* `CO_change_1h`
* `WSPM`
* `PM10_rolling_mean_3h`

The results show that the model relies strongly on **recent pollution conditions, short-term pollutant dynamics, wind direction, and meteorological variables**.

Feature importance describes how the model uses the features but does not establish causal relationships.

---

### 10. SHAP Interpretation

SHAP analysis was used to examine how individual features contribute to model predictions.

The strongest contributors included:

* `PM2.5`
* `PM2.5_lag_1h`
* `hour`
* `WSPM`
* `month`
* `TEMP`
* `PM2.5_change_1h`
* `DEWP`
* `PM2.5_change_3h`
* `PRES`

The analysis showed that higher current and recent PM2.5 values generally contribute toward higher predicted deterioration probability, while higher wind speed tends to contribute toward lower predicted probability.

SHAP results describe **model behavior and feature contributions**, rather than causal effects.

---

### 11. Early Warning Prediction

The final XGBoost model was converted into an early warning system by applying a probability threshold to its deterioration predictions.

A warning threshold of **0.30** was selected using the 2015 validation period, with emphasis on recall because missed deterioration events are particularly important in an early warning context.

Final performance on the unseen test period:

| Metric            |               Result |
| ----------------- | -------------------: |
| Warning threshold |             **0.30** |
| Precision         |           **0.6252** |
| Recall            |           **0.8998** |
| F1-score          |           **0.7378** |
| True positives    |           **52,795** |
| False negatives   |            **5,878** |
| Warning signals   | **84,447 / 121,900** |
| Lead time range   |        **1–6 hours** |
|                   |                      |

---

## 📊 Dataset

AirShift uses the **Beijing Multi-Site Air Quality Dataset**, containing hourly observations from 12 monitoring stations.

The dataset includes:

* Air pollutants: `PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3`
* Meteorological variables: `TEMP`, `PRES`, `DEWP`, `RAIN`, `wd`, `WSPM`
* Temporal information: year, month, day, and hour
* Monitoring station identifier

---

