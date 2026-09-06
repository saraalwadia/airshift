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

---

## 📊 Dataset

AirShift uses the **Beijing Multi-Site Air Quality Dataset**, containing hourly observations from 12 monitoring stations.

The dataset includes:

* Air pollutants: `PM2.5`, `PM10`, `SO2`, `NO2`, `CO`, `O3`
* Meteorological variables: `TEMP`, `PRES`, `DEWP`, `RAIN`, `wd`, `WSPM`
* Temporal information: year, month, day, and hour
* Monitoring station identifier

---

## 🚧 Project Status

### Completed

* [x] Data Profiling & Understanding
* [x] Data Cleaning
* [x] Cleaned Dataset Validation

### Upcoming

* [ ] Feature Engineering
* [ ] Deterioration Event Definition
* [ ] Model Development
* [ ] Early Warning Prediction
* [ ] Warning Lead Time Evaluation
