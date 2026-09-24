# AirShift — Project Card

> **Early Warning System for Air Quality Deterioration**

AirShift is a machine learning project designed to detect early warning signals of significant air quality deterioration before the deterioration event occurs.

Rather than predicting a specific future pollutant concentration, AirShift estimates the probability that **PM2.5 will increase by at least 30% within the following six hours** based on current and historical air quality conditions, meteorological variables, temporal patterns, and recent pollution trends.

---

## 1. Project Overview

| Item                    | Details                                               |
| ----------------------- | ----------------------------------------------------- |
| **Project Name**        | AirShift                                              |
| **Project Type**        | Machine Learning / Time-Series / Early Warning System |
| **Primary Task**        | Binary classification                                 |
| **Target Event**        | PM2.5 increase of ≥30% within the following 6 hours   |
| **Prediction Output**   | Probability of future deterioration                   |
| **Warning Threshold**   | 0.30                                                  |
| **Final Model**         | XGBoost                                               |
| **Dataset**             | Beijing Multi-Site Air Quality Dataset                |
| **Monitoring Stations** | 12                                                    |
| **Temporal Resolution** | Hourly                                                |
| **Data Period**         | March 2013 – February 2017                            |
| **Final Test Period**   | January 2016 – February 2017                          |
| **Main Frameworks**     | Python, Pandas, Scikit-learn, XGBoost, SHAP, FastAPI  |

---

## 2. Problem

Conventional air quality prediction systems often focus on forecasting future pollutant concentrations.

AirShift approaches the problem from an early-warning perspective:

> **Can current and recent environmental conditions provide a useful warning that air quality is likely to deteriorate soon?**

The system therefore focuses on **risk detection and warning**, rather than directly forecasting a future pollutant value.

This distinction is important because an operational warning system needs to identify deterioration early enough for the warning to be useful.

---

## 3. Project Objective

The main objectives of AirShift are to:

* Detect future air quality deterioration events.
* Use current and historical environmental information without future-data leakage.
* Compare multiple machine learning approaches.
* Optimize an XGBoost classification model.
* Evaluate performance on a strictly held-out future test period.
* Interpret the model using feature importance and SHAP.
* Investigate how much lead time the model can provide within the defined six-hour prediction horizon.
* Expose the trained model through a FastAPI prediction endpoint.

---

## 4. Dataset

AirShift uses the **Beijing Multi-Site Air Quality Dataset**, containing hourly observations from 12 monitoring stations.

### Dataset Characteristics

* **12 monitoring stations**
* **420,768 observations**
* **Hourly measurements**
* **March 2013 – February 2017**
* **18 original variables**

### Air Quality Variables

* `PM2.5`
* `PM10`
* `SO2`
* `NO2`
* `CO`
* `O3`

### Meteorological Variables

* `TEMP`
* `PRES`
* `DEWP`
* `RAIN`
* `wd`
* `WSPM`

### Temporal Variables

* `year`
* `month`
* `day`
* `hour`

Each observation also contains a station identifier.

---

## 5. Data Preparation

The data preparation process was designed to preserve the temporal structure of the dataset and avoid introducing artificial information.

The main steps included:

1. Combining observations from all 12 monitoring stations.
2. Creating a unified `datetime` variable.
3. Validating data types and column structure.
4. Checking for invalid negative values.
5. Checking duplicate observations and temporal continuity.
6. Interpolating short numerical missing-data gaps of up to six hours.
7. Retaining prolonged pollutant gaps as missing values rather than artificially filling them.
8. Forward-filling missing wind-direction values within each station.
9. Validating the cleaned dataset before feature engineering.

After cleaning, the dataset retained its original temporal structure while reducing short numerical gaps.

---

## 6. Feature Engineering

AirShift uses historical and short-term temporal features to capture recent pollution behavior.

The final feature-engineering stage produced **99 columns**, including the original variables and engineered features.

After removing non-model fields such as `No` and `datetime`, the model used **97 input features**.

### Engineered Feature Groups

#### Temporal Features

* `day_of_week`
* `is_weekend`

Existing temporal variables such as `year`, `month`, `day`, and `hour` were also retained.

#### Lag Features

For each pollutant:

* 1-hour lag
* 3-hour lag
* 6-hour lag

#### Rolling Statistics

For each pollutant:

* 3-hour rolling mean
* 3-hour rolling maximum
* 3-hour rolling standard deviation
* 6-hour rolling mean
* 6-hour rolling maximum
* 6-hour rolling standard deviation

Rolling statistics were calculated using previous observations so that future information was not introduced.

#### Short-Term Changes

For each pollutant:

* 1-hour change
* 3-hour change

#### Trend Features

For each pollutant:

* 3-hour trend
* 6-hour trend

These features were designed to capture whether pollutant concentrations were increasing, decreasing, or changing rapidly before the prediction time.

---

## 7. Deterioration Event Definition

The AirShift target is a binary deterioration event based on PM2.5.

A deterioration event is defined when:

> **PM2.5 increases by at least 30% within the following six hours.**

For each observation, the maximum PM2.5 value across the next one to six hours was compared with the current PM2.5 value.

The event is therefore defined as:

```text
Future maximum PM2.5 ≥ Current PM2.5 × 1.30
```

The target was designed to capture a meaningful short-term deterioration rather than simply predicting small pollutant fluctuations.

---

## 8. Labeling

The labeling process required a complete six-hour future window for valid target construction.

After removing observations for which the target could not be reliably determined:

* **418,381 observations** received valid labels.
* **219,985 observations (52.58%)** were classified as non-deterioration.
* **198,396 observations (47.42%)** were classified as deterioration.

This produced a relatively balanced binary classification problem.

---

## 9. Model Development

Three classification models were evaluated:

1. Logistic Regression
2. Random Forest
3. XGBoost

A temporal rather than random data split was used to preserve the chronological nature of the problem.

### Development Split

| Dataset    | Period    |
| ---------- | --------- |
| Training   | 2013–2014 |
| Validation | 2015      |
| Final Test | 2016–2017 |

The final test period was kept separate from model development, hyperparameter tuning, and final training.

---

## 10. XGBoost Optimization

XGBoost was selected for further optimization after the initial model comparison.

Hyperparameter optimization used:

* `TimeSeriesSplit`
* 3 temporal folds
* `RandomizedSearchCV`
* 15 parameter configurations
* 45 total fits
* `average_precision` as the optimization metric

### Final XGBoost Parameters

```text
n_estimators = 400
learning_rate = 0.1
max_depth = 6
min_child_weight = 3
subsample = 0.7
colsample_bytree = 1.0
random_state = 42
```

The final model was retrained using the combined **2013–2014 training data and 2015 validation data** before evaluation on the unseen 2016–2017 test period.

---

## 11. Final Model Performance

The final XGBoost model was evaluated on the completely held-out test period.

### Final Test Results

| Metric        |     Result |
| ------------- | ---------: |
| **Accuracy**  | **0.7368** |
| **Precision** | **0.7244** |
| **Recall**    | **0.7315** |
| **F1 Score**  | **0.7279** |
| **ROC-AUC**   | **0.8215** |
| **PR-AUC**    | **0.8186** |

### Test Set

* **121,900 observations**
* Period: **2016-01-01 to 2017-02-28 17:00**

The test set was not used for model development or hyperparameter optimization.

---

## 12. Confusion Matrix

At the standard classification threshold of 0.50, the final test confusion matrix was:

|                     | Predicted Negative | Predicted Positive |
| ------------------- | -----------------: | -----------------: |
| **Actual Negative** |             46,896 |             16,331 |
| **Actual Positive** |             15,756 |             42,917 |

The confusion matrix shows the balance between correctly detected deterioration events and missed or false warnings at the standard classification threshold.

For an early-warning application, false negatives are particularly important because they represent deterioration events that were not identified as positive by the classifier.

---

## 13. Model Interpretation

AirShift uses two complementary approaches to interpret the final XGBoost model.

### Built-in Feature Importance

The highest-ranked model features included:

* `PM2.5_lag_1h`
* wind-direction categories
* current `PM2.5`
* `PM10_lag_1h`
* `RAIN`
* `hour`
* `CO_change_1h`
* `WSPM`
* `PM10_rolling_mean_3h`
* `NO2_change_1h`

The strongest built-in feature importance was associated with:

```text
PM2.5_lag_1h
```

with an importance value of approximately **0.210**.

### SHAP Interpretation

SHAP analysis was performed on a sample of **5,000 test observations**.

The highest mean absolute SHAP contributions included:

| Feature | Mean |SHAP| |
|---|---:|
| `PM2.5` | 0.8581 |
| `PM2.5_lag_1h` | 0.3912 |
| `hour` | 0.3741 |
| `WSPM` | 0.2636 |
| `month` | 0.2611 |
| `TEMP` | 0.2241 |
| `PM2.5_change_1h` | 0.1640 |
| `DEWP` | 0.1617 |
| `PM2.5_change_3h` | 0.1253 |
| `PRES` | 0.1074 |

The SHAP analysis indicates that current and recent PM2.5 conditions contribute substantially to the model's predictions.

SHAP results also provide information about the direction of feature contributions for individual predictions, unlike built-in XGBoost importance alone.

---

## 14. Early Warning Strategy

For the early-warning application, AirShift uses a probability threshold of:

```text
0.30
```

A warning is generated when:

```text
P(Deterioration) ≥ 0.30
```

The threshold was selected using the **2015 validation period**, not the final test set.

The choice reflects the project's early-warning objective, where reducing missed deterioration events is an important consideration.

### Validation Threshold Selection

At the selected threshold of 0.30:

| Metric    | Validation Result |
| --------- | ----------------: |
| Precision |            0.6201 |
| Recall    |            0.8813 |
| F1 Score  |            0.7280 |

The threshold was therefore treated as an application-level design choice rather than optimized on the final test data.

---

## 15. Final Early Warning Performance

The final trained model was evaluated on the unseen test period using the 0.30 warning threshold.

| Metric        | Test Result |
| ------------- | ----------: |
| **Precision** |  **0.6252** |
| **Recall**    |  **0.8998** |
| **F1 Score**  |  **0.7378** |

### Test Confusion Matrix at Warning Threshold = 0.30

|                     | Predicted No Warning | Predicted Warning |
| ------------------- | -------------------: | ----------------: |
| **Actual Negative** |               31,575 |            31,652 |
| **Actual Positive** |                5,878 |            52,795 |

The threshold increased the number of detected deterioration events compared with the standard 0.50 classification threshold, while also generating more positive warnings.

---

## 16. Warning Lead Time

AirShift also evaluates when warnings occur relative to the estimated deterioration occurrence.

The occurrence time is defined as the **earliest future hour within the six-hour horizon** at which PM2.5 reaches at least 130% of its current value.

Among successful warnings:

* Lead time ranged from **1 to 6 hours**.
* Mean lead time: **2.74 hours**
* Median lead time: **2 hours**
* **52.57%** of successful warnings occurred at least two hours before the estimated deterioration occurrence.

### Lead-Time Distribution

| Lead Time | Successful Warnings | Percentage |
| --------- | ------------------: | ---------: |
| 1 hour    |              15,677 |     29.70% |
| 2 hours   |              12,072 |     22.87% |
| 3 hours   |               8,937 |     16.93% |
| 4 hours   |               6,770 |     12.83% |
| 5 hours   |               5,247 |      9.94% |
| 6 hours   |               4,083 |      7.74% |

The lead-time analysis describes the timing of detected events **within the six-hour target horizon**. It should not be interpreted as a guarantee that the system will always provide 2.74 hours of operational warning.

---

## 17. API

The trained AirShift model is exposed through a **FastAPI** application.

### Available Endpoints

| Endpoint   | Method | Purpose                              |
| ---------- | ------ | ------------------------------------ |
| `/`        | GET    | API status                           |
| `/health`  | GET    | Health and model-loading check       |
| `/predict` | POST   | Generate an early-warning prediction |

The `/predict` endpoint accepts a sequence of at least **seven consecutive hourly observations** from the same monitoring station.

The API:

1. Validates the input.
2. Derives temporal variables from `datetime`.
3. Generates the same feature-engineering structure used during model development.
4. Validates the resulting model features.
5. Generates a deterioration probability.
6. Applies the 0.30 warning threshold.
7. Returns the prediction and warning status.

### Example Response

```json
{
  "prediction_time": "2013-03-01T06:00:00",
  "station": "Aotizhongxin",
  "deterioration_probability": 0.939,
  "warning_threshold": 0.3,
  "early_warning": true
}
```

The API was validated for:

* Valid prediction requests
* Insufficient observations
* Non-consecutive timestamps
* Duplicate timestamps
* Multiple monitoring stations

---

## 18. Technology Stack

### Programming & Data

* Python
* Pandas
* NumPy

### Machine Learning

* Scikit-learn
* XGBoost
* SHAP

### API

* FastAPI
* Uvicorn
* Pydantic

### Development & Visualization

* Jupyter Notebook
* Matplotlib
* Git / GitHub

---

## 19. Project Architecture

```text
Raw Air Quality Data
        │
        ▼
Data Profiling
        │
        ▼
Data Cleaning
        │
        ▼
Feature Engineering
        │
        ▼
Deterioration Event Definition
        │
        ▼
Target Labeling
        │
        ▼
Model Development
        │
        ├── Logistic Regression
        ├── Random Forest
        └── XGBoost
                │
                ▼
        XGBoost Optimization
                │
                ▼
        Final Model Training
                │
                ▼
        Final Test Evaluation
                │
        ┌───────┴────────┐
        ▼                ▼
 Feature Importance     SHAP
        │                │
        └───────┬────────┘
                ▼
       Early Warning Prediction
                │
                ▼
        Lead Time Evaluation
                │
                ▼
             FastAPI
```

---

## 20. Key Findings

The completed analysis provides several model-level findings:

* Recent PM2.5 conditions are highly influential in deterioration predictions.
* The previous-hour PM2.5 value was the strongest feature according to built-in XGBoost feature importance.
* SHAP analysis identified current PM2.5 and recent PM2.5 history as major contributors to model predictions.
* Meteorological and temporal variables also contribute to predictions.
* The final XGBoost model achieved a **ROC-AUC of 0.8215** and **PR-AUC of 0.8186** on the held-out test period.
* Using the 0.30 early-warning threshold produced a test recall of **0.8998**.
* Successful warnings occurred between **1 and 6 hours** before the estimated deterioration occurrence, with a mean timing of **2.74 hours**.

These findings describe the behavior of the trained model and should not be interpreted as causal relationships between environmental variables and air quality deterioration.

---

## 21. Limitations

AirShift has several important limitations:

* The deterioration event is defined specifically around PM2.5 and a 30% increase threshold.
* The prediction horizon is limited to six hours.
* The dataset represents historical observations from Beijing and may not generalize directly to other locations.
* The model depends on the availability and quality of recent hourly observations.
* Missing or insufficient historical observations can prevent feature generation.
* The warning threshold represents a project design choice and may need recalibration for operational deployment.
* Built-in feature importance and SHAP explain model behavior but do not establish causality.
* Lead-time results are based on the project's defined event-occurrence methodology and should not be interpreted as guaranteed operational warning time.

---

## 22. Future Improvements

Potential future work includes:

* Testing the system on additional cities and datasets.
* Evaluating alternative deterioration definitions.
* Exploring longer and shorter prediction horizons.
* Calibrating predicted probabilities.
* Evaluating threshold stability across different periods and stations.
* Adding more advanced time-series models.
* Investigating station-specific and cross-station features.
* Adding automated monitoring and alert delivery.
* Deploying the FastAPI service as a production-ready application.
* Monitoring model performance and data drift after deployment.

---

## 23. Project Status

### Completed

* [x] Data Profiling & Understanding
* [x] Data Cleaning
* [x] Feature Engineering
* [x] Deterioration Event Definition
* [x] Target Labeling
* [x] Model Development
* [x] XGBoost Optimization
* [x] Final Test Evaluation
* [x] Feature Importance Analysis
* [x] SHAP Interpretation
* [x] Early Warning Prediction
* [x] Warning Lead-Time Evaluation
* [x] FastAPI Prediction API
* [x] API Validation

### Final Stage

* [ ] Final GitHub documentation review
* [ ] Repository organization and presentation
* [ ] Final project documentation

---

## 24. Summary

**AirShift** combines time-series feature engineering, machine learning, model interpretation, and API deployment to investigate an early-warning approach to air quality deterioration.

The final system uses an optimized **XGBoost classifier** trained on historical air quality and meteorological patterns. On the held-out 2016–2017 test period, the model achieved a **ROC-AUC of 0.8215**, while the early-warning threshold of **0.30** achieved **89.98% recall** for the defined deterioration events.

The project demonstrates a complete machine learning workflow:

```text
Data
→ Cleaning
→ Feature Engineering
→ Event Definition
→ Labeling
→ Model Development
→ Optimization
→ Evaluation
→ Interpretation
→ Early Warning
→ API Deployment
```

The main purpose of AirShift is not to claim a production-ready air quality forecasting system, but to demonstrate how machine learning can be structured around **early detection of short-term deterioration risk** while maintaining temporal separation between model development and final evaluation.
