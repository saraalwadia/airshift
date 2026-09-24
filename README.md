# 🌬️ AirShift

## Early Warning System for Air Quality Deterioration

AirShift is a machine learning system designed to detect **early warning signals of air quality deterioration** before a significant increase in PM2.5 occurs.

Rather than forecasting pollutant concentrations directly, AirShift predicts whether **PM2.5 is likely to increase by at least 30% within the following six hours**, using current conditions and recent environmental trends.

---

## 🎯 Objective

The project investigates whether historical air quality and meteorological patterns can be used to provide an early warning of short-term air quality deterioration.

The system also evaluates **warning lead time** to understand how far in advance deterioration can be detected.

---

## 📊 Dataset

AirShift uses the **Beijing Multi-Site Air Quality Dataset**, containing hourly observations from 12 monitoring stations between March 2013 and February 2017.

* **420,768 observations**
* **12 monitoring stations**
* **6 air pollutants**
* **5 meteorological variables + wind information**
* Hourly temporal resolution

### Target Event

A deterioration event is defined as:

> **PM2.5 increasing by at least 30% within the following six hours.**

The final labeled dataset contains **418,381 valid observations**.

---

## 📥 Data Setup

The original dataset can be downloaded and prepared automatically using:

```bash
python scripts/download_data.py
```

The script downloads the dataset and extracts the 12 station files into `data/raw/`.

If the dataset is already present, the script skips the download.

---

## 🔄 Machine Learning Pipeline

```text
Raw Data
   ↓
Data Profiling & Cleaning
   ↓
Feature Engineering
   ↓
Deterioration Event Definition
   ↓
Temporal Model Development
   ↓
XGBoost Optimization
   ↓
Final Test Evaluation
   ↓
Early Warning Prediction
   ↓
Lead Time Analysis
```

Feature engineering includes:

* Historical pollutant lags
* Rolling statistics
* Short-term changes
* Trend features
* Meteorological variables
* Temporal features
* Station and wind-direction information

All temporal features are constructed using information available at or before the prediction time to avoid future-data leakage.

---

## 🤖 Model Development

Three classification models were evaluated:

* Logistic Regression
* Random Forest
* XGBoost

A chronological split was used to preserve the time-series structure:

| Dataset    | Period    |
| ---------- | --------- |
| Training   | 2013–2014 |
| Validation | 2015      |
| Final Test | 2016–2017 |

XGBoost was selected for further optimization based on its validation performance.

### Final XGBoost

```text
n_estimators = 400
learning_rate = 0.1
max_depth = 6
min_child_weight = 3
subsample = 0.7
colsample_bytree = 1.0
```

---

## 📈 Final Test Performance

The final model was retrained on the 2013–2015 development data and evaluated once on the unseen 2016–2017 test period.

| Metric    |       Test |
| --------- | ---------: |
| Accuracy  | **0.7368** |
| Precision | **0.7244** |
| Recall    | **0.7315** |
| F1 Score  | **0.7279** |
| ROC-AUC   | **0.8215** |
| PR-AUC    | **0.8186** |

The final test set contains **121,900 observations** and was not used during model development or tuning.

---

## 🔎 Model Interpretation

Model interpretation was performed using both built-in XGBoost feature importance and SHAP.

The SHAP analysis showed that the model relies strongly on:

* Current PM2.5
* Recent PM2.5 levels
* Short-term pollutant changes
* Wind speed
* Meteorological conditions
* Temporal patterns

SHAP was used to examine both global feature importance and the direction of feature contributions.

---

## 🚨 Early Warning System

For the early-warning experiment, a probability threshold of **0.30** was selected using the validation period to emphasize sensitivity to deterioration events.

### Test Results

| Metric    | Threshold = 0.30 |
| --------- | ---------------: |
| Precision |       **0.6252** |
| Recall    |       **0.8998** |
| F1 Score  |       **0.7378** |

The system generated **84,447 warnings out of 121,900 test observations**.

---

## ⏱️ Warning Lead Time

For detected deterioration events, the estimated lead time ranged from **1 to 6 hours**.

* Mean: **2.74 hours**
* Median: **2 hours**
* **52.57%** of successful warnings occurred at least **2 hours before** the estimated deterioration occurrence.

Lead time represents the timing of warnings relative to the defined six-hour deterioration target; it should not be interpreted as a guaranteed operational warning time.

---

## 🚀 FastAPI Service

The trained model is exposed through a local **FastAPI** service.

### Endpoints

```text
GET  /
GET  /health
POST /predict
```

The `/predict` endpoint accepts recent hourly observations and returns:

* Deterioration probability
* Warning threshold
* Early warning decision
* Prediction timestamp
* Monitoring station

The API validates:

* Minimum historical observations
* Consecutive hourly timestamps
* Duplicate timestamps
* Single-station input
* Feature compatibility with the trained model

See the [API documentation](docs/api_documentation.md) for usage details.

---

## 📚 Documentation

Detailed project documentation is available in the `docs/` directory:

* [Project Card](docs/project_card.md)
* [Methodology](docs/methodology.md)
* [Error Log](docs/error_log.md)
* [API Documentation](docs/api_documentation.md)
* [Decisions & Notes](docs/decisions_and_notes.md)

---

## 🗂️ Project Structure

```text
airshift/
├── api/
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── models/
├── notebooks/
├── reports/
│   └── figures/
├── scripts/
│   └── download_data.py
├── requirements.txt
├── README.md
└── .gitignore
```

---

## ⚠️ Limitations

* The deterioration target is specifically based on **PM2.5** and a 30% relative increase within six hours.
* The model learns statistical patterns and does not establish causal relationships.
* Correlated environmental features may share predictive information.
* The current API is designed for local inference and is not a production deployment.
* Lead-time results are specific to the defined event and evaluation methodology.

---

## 📌 Project Status

**Completed**

* [x] Data profiling and cleaning
* [x] Automated dataset download
* [x] Feature engineering
* [x] Event definition and labeling
* [x] Model development and XGBoost optimization
* [x] Final test evaluation
* [x] Feature importance analysis
* [x] SHAP interpretation
* [x] Early warning evaluation
* [x] Lead-time analysis
* [x] FastAPI deployment and validation

**AirShift is a completed end-to-end machine learning prototype for research and portfolio purposes.**

---

## 👩‍💻 Author

**Sara Alwadia**

AI & Machine Learning | Data-Driven Solutions

[GitHub](https://github.com/saraalwadia)
