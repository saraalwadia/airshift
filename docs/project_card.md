# AirShift — Project Card

> **Early Warning System for Air Quality Deterioration**

## 1. Project Summary

**AirShift** is a machine learning project that investigates whether current and recent air-quality conditions can provide an early warning of short-term air quality deterioration.

Instead of forecasting the exact future concentration of a pollutant, AirShift formulates the problem as a **binary classification task**: predicting whether **PM2.5 will increase by at least 30% within the following six hours**.

The project combines time-series feature engineering, supervised machine learning, model interpretation, early-warning threshold selection, lead-time analysis, and a FastAPI prediction service.

---

## 2. Problem

Air quality deterioration can develop over a relatively short period. A useful early-warning system therefore needs to identify signals of increasing pollution before the defined deterioration event occurs.

AirShift addresses the following question:

> **Can historical and current environmental patterns be used to identify an upcoming PM2.5 deterioration event?**

The project focuses on **early detection**, rather than direct pollutant concentration forecasting.

---

## 3. Objective

The project aims to:

* Define a measurable short-term air-quality deterioration event.
* Capture recent pollution behavior through temporal features.
* Compare multiple classification models.
* Optimize an XGBoost model using time-aware validation.
* Evaluate the final model on a completely held-out future period.
* Interpret model behavior using feature importance and SHAP.
* Select an application-oriented warning threshold.
* Evaluate the timing of successful warnings.
* Expose the final model through a FastAPI endpoint.

---

## 4. Dataset

AirShift uses the **Beijing Multi-Site Air Quality Dataset**.

| Characteristic           | Value                      |
| ------------------------ | -------------------------- |
| Monitoring stations      | 12                         |
| Total observations       | 420,768                    |
| Frequency                | Hourly                     |
| Period                   | March 2013 – February 2017 |
| Original variables       | 18                         |
| Primary target pollutant | PM2.5                      |

### Variables

**Air pollutants**

`PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3`

**Meteorological variables**

`TEMP`, `PRES`, `DEWP`, `RAIN`, `wd`, `WSPM`

**Temporal variables**

`year`, `month`, `day`, `hour`

---

## 5. Target Definition

A **deterioration event** is defined when the maximum PM2.5 value observed during the following six hours reaches at least **130% of the current PM2.5 value**.

In simplified form:

```text
Future maximum PM2.5 ≥ Current PM2.5 × 1.30
```

The target uses future observations only for **label construction**. Future information is not used as an input feature during prediction.

Because a complete six-hour future window is required to determine the target, observations without sufficient future information are excluded from the final labeled dataset.

### Final labeled dataset

| Class            | Observations |    Share |
| ---------------- | -----------: | -------: |
| No deterioration |      219,985 |   52.58% |
| Deterioration    |      198,396 |   47.42% |
| **Valid labels** |  **418,381** | **100%** |

---

## 6. Feature Engineering

The feature-engineering pipeline produces **99 columns**, including the original data and engineered features.

After excluding non-model fields, the final model uses **97 input features**.

Feature groups include:

* Temporal features
* 1-hour, 3-hour, and 6-hour pollutant lags
* 3-hour and 6-hour rolling statistics
* 1-hour and 3-hour pollutant changes
* 3-hour and 6-hour trend features
* Meteorological variables
* Wind direction
* Monitoring station

Rolling and historical features are constructed using information available at or before the prediction time to avoid future-data leakage.

---

## 7. Modeling Strategy

Three classification models were evaluated:

1. Logistic Regression
2. Random Forest
3. XGBoost

The project uses a **chronological split** rather than a random train/test split.

| Dataset    | Period    |
| ---------- | --------- |
| Training   | 2013–2014 |
| Validation | 2015      |
| Final Test | 2016–2017 |

The final test period was kept separate from model development and hyperparameter optimization.

---

## 8. Final Model

The final model is an **XGBoost classifier**.

Hyperparameter optimization used:

* `TimeSeriesSplit`
* 3 temporal folds
* `RandomizedSearchCV`
* 15 parameter configurations
* `average_precision` scoring

### Final configuration

```text
n_estimators = 400
learning_rate = 0.1
max_depth = 6
min_child_weight = 3
subsample = 0.7
colsample_bytree = 1.0
random_state = 42
```

The final XGBoost model was retrained using the combined **2013–2014 training data and 2015 validation data**, then evaluated on the held-out test period.

---

## 9. Final Test Performance

The final test period contains **121,900 observations** covering:

**2016-01-01 → 2017-02-28 17:00**

| Metric    |     Result |
| --------- | ---------: |
| Accuracy  | **0.7368** |
| Precision | **0.7244** |
| Recall    | **0.7315** |
| F1 Score  | **0.7279** |
| ROC-AUC   | **0.8215** |
| PR-AUC    | **0.8186** |

These results were obtained on the held-out test period, which was not used for model tuning.

---

## 10. Model Interpretation

Two complementary interpretation approaches were used.

### Feature Importance

The strongest built-in XGBoost feature importance was associated with:

```text
PM2.5_lag_1h
```

Other highly ranked features included:

* Wind-direction categories
* Current PM2.5
* PM10 lag
* RAIN
* Hour
* CO short-term change
* WSPM
* PM10 rolling statistics
* NO2 short-term change

### SHAP

SHAP analysis was performed on a **5,000-observation sample from the final test set**.

The largest mean absolute SHAP contributions included:

| Feature | Mean |SHAP| |
|---|---:|
| PM2.5 | 0.8581 |
| PM2.5_lag_1h | 0.3912 |
| hour | 0.3741 |
| WSPM | 0.2636 |
| month | 0.2611 |
| TEMP | 0.2241 |
| PM2.5_change_1h | 0.1640 |
| DEWP | 0.1617 |
| PM2.5_change_3h | 0.1253 |
| PRES | 0.1074 |

The interpretation results indicate that current and recent PM2.5 conditions are major contributors to the model's predictions.

Feature importance and SHAP describe **model behavior** and should not be interpreted as evidence of causal relationships.

---

## 11. Early Warning Strategy

For the early-warning application, a probability threshold of:

```text
0.30
```

was selected using the **2015 validation period**.

A warning is generated when:

```text
P(Deterioration) ≥ 0.30
```

The threshold was selected with the early-warning objective in mind, where detecting more deterioration events and reducing false negatives are important considerations.

### Validation Performance at 0.30

| Metric    | Result |
| --------- | -----: |
| Precision | 0.6201 |
| Recall    | 0.8813 |
| F1 Score  | 0.7280 |

The threshold was selected without using the final test set.

---

## 12. Final Early Warning Performance

Using the 0.30 threshold on the held-out test period:

| Metric    |     Result |
| --------- | ---------: |
| Precision | **0.6252** |
| Recall    | **0.8998** |
| F1 Score  | **0.7378** |

The resulting test confusion matrix was:

|                             | Predicted No Warning | Predicted Warning |
| --------------------------- | -------------------: | ----------------: |
| **Actual No Deterioration** |               31,575 |            31,652 |
| **Actual Deterioration**    |                5,878 |            52,795 |

The threshold increases sensitivity to the defined deterioration events, while also producing more positive warnings.

---

## 13. Warning Lead Time

AirShift evaluates the timing of successful warnings relative to the estimated deterioration occurrence.

The occurrence time is defined as the **earliest future hour within the six-hour horizon** at which PM2.5 reaches at least 130% of its current value.

For successful warnings:

* Lead time range: **1–6 hours**
* Mean lead time: **2.74 hours**
* Median lead time: **2 hours**
* **52.57%** occurred at least two hours before the estimated deterioration occurrence

### Lead-Time Distribution

| Lead Time | Successful Warnings |  Share |
| --------- | ------------------: | -----: |
| 1 hour    |              15,677 | 29.70% |
| 2 hours   |              12,072 | 22.87% |
| 3 hours   |               8,937 | 16.93% |
| 4 hours   |               6,770 | 12.83% |
| 5 hours   |               5,247 |  9.94% |
| 6 hours   |               4,083 |  7.74% |

These values describe warning timing under the project's defined six-hour event methodology. They should not be interpreted as a guaranteed operational warning time.

---

## 14. API

The final model is exposed through a **FastAPI** service.

### Endpoints

| Endpoint   | Method | Purpose                              |
| ---------- | ------ | ------------------------------------ |
| `/`        | GET    | API status                           |
| `/health`  | GET    | Health and model-loading check       |
| `/predict` | POST   | Generate an early-warning prediction |

The prediction endpoint requires at least **seven consecutive hourly observations** from the same monitoring station.

The API validates:

* Minimum observation count
* Station consistency
* Duplicate timestamps
* Consecutive hourly timestamps
* Feature compatibility
* Availability of sufficient historical information for feature generation

### Example Prediction

```json
{
  "prediction_time": "2013-03-01T06:00:00",
  "station": "Aotizhongxin",
  "deterioration_probability": 0.939,
  "warning_threshold": 0.3,
  "early_warning": true
}
```

The API validation suite successfully tested:

* Valid prediction
* Fewer than seven observations
* Non-consecutive timestamps
* Duplicate timestamps
* Multiple stations

---

## 15. Technology Stack

**Language:** Python

**Data:** Pandas, NumPy

**Machine Learning:** Scikit-learn, XGBoost

**Interpretability:** SHAP

**API:** FastAPI, Uvicorn, Pydantic

**Development:** Jupyter Notebook, VS Code

**Version Control:** Git, GitHub

---

## 16. Project Pipeline

```text
Raw Data
    ↓
Data Profiling
    ↓
Data Cleaning
    ↓
Feature Engineering
    ↓
Deterioration Event Definition
    ↓
Target Labeling
    ↓
Model Development
    ↓
XGBoost Optimization
    ↓
Final Test Evaluation
    ↓
Feature Importance + SHAP
    ↓
Early Warning Prediction
    ↓
Lead-Time Evaluation
    ↓
FastAPI
```

---

## 17. Limitations

AirShift should be interpreted within the scope of its dataset and target definition.

Key limitations include:

* The deterioration event is specifically defined using a **30% PM2.5 increase within six hours**.
* The dataset represents historical air-quality observations from Beijing.
* Model performance may not directly generalize to other cities or monitoring networks.
* The model depends on sufficiently recent hourly observations.
* The 0.30 warning threshold is an application-oriented design choice rather than a universally optimal threshold.
* Feature importance and SHAP describe model behavior but do not establish causality.
* Lead-time measurements depend on the project's operational definition of deterioration occurrence.

---

## 18. Project Status

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

### Final Documentation

* [ ] Final GitHub documentation review
* [ ] Repository presentation and cleanup

---

## 19. Project Takeaway

AirShift demonstrates a complete machine learning workflow for an early-warning classification problem:

> **From historical environmental observations to feature engineering, temporal modeling, model interpretation, early-warning thresholding, lead-time analysis, and API deployment.**

The final XGBoost model achieved a **ROC-AUC of 0.8215** on the held-out test period. Under the project's early-warning threshold of **0.30**, the system achieved **89.98% recall** for the defined PM2.5 deterioration events.

The project is intended as a machine learning research and portfolio implementation of an early-warning approach, rather than a claim of a production-ready public air-quality alert system.
