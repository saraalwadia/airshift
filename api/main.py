from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException

from api.feature_engineering import create_features
from api.schemas import (
    PredictionRequest,
    PredictionResponse,
)


# --------------------------------------------------
# Project paths
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent

MODEL_PATH = (
    BASE_DIR
    / "models"
    / "xgboost_final.joblib"
)


# --------------------------------------------------
# Load final model
# --------------------------------------------------

final_xgb = joblib.load(MODEL_PATH)

MODEL_FEATURES = list(
    final_xgb.feature_names_in_
)

WARNING_THRESHOLD = 0.30


# --------------------------------------------------
# FastAPI application
# --------------------------------------------------

app = FastAPI(
    title="AirShift API",
    description="Early Warning API for Air Quality Deterioration",
    version="1.0.0",
)


# --------------------------------------------------
# Root endpoint
# --------------------------------------------------

@app.get("/")
def root():
    return {
        "message": "AirShift API is running",
        "status": "ok",
    }


# --------------------------------------------------
# Health endpoint
# --------------------------------------------------

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": True,
    }


# --------------------------------------------------
# Prediction endpoint
# --------------------------------------------------

@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict(request: PredictionRequest):

    # --------------------------------------------------
    # 1. Validate number of observations
    # --------------------------------------------------

    if len(request.observations) < 7:
        raise HTTPException(
            status_code=400,
            detail="At least 7 hourly observations are required.",
        )

    # --------------------------------------------------
    # 2. Convert request to DataFrame
    # --------------------------------------------------

    observations = pd.DataFrame(
        [
            observation.model_dump()
            for observation in request.observations
        ]
    )

    # --------------------------------------------------
    # 3. Rename PM2_5 to dataset column name
    # --------------------------------------------------

    observations = observations.rename(
        columns={
            "PM2_5": "PM2.5",
        }
    )

    # --------------------------------------------------
    # 4. Validate station
    # --------------------------------------------------

    stations = observations["station"].unique()

    if len(stations) != 1:
        raise HTTPException(
            status_code=400,
            detail="All observations must belong to the same station.",
        )

    # --------------------------------------------------
    # 5. Sort observations chronologically
    # --------------------------------------------------

    observations = (
        observations
        .sort_values("datetime")
        .reset_index(drop=True)
    )

    # --------------------------------------------------
    # 5.1 Create original time features
    # --------------------------------------------------

    observations["year"] = (
        observations["datetime"].dt.year
    )

    observations["month"] = (
        observations["datetime"].dt.month
    )

    observations["day"] = (
        observations["datetime"].dt.day
    )

    observations["hour"] = (
        observations["datetime"].dt.hour
    )

    # --------------------------------------------------
    # 6. Check duplicate timestamps
    # --------------------------------------------------

    if observations["datetime"].duplicated().any():
        raise HTTPException(
            status_code=400,
            detail="Duplicate datetime values are not allowed.",
        )

    # --------------------------------------------------
    # 7. Check hourly continuity
    # --------------------------------------------------

    time_difference = (
        observations["datetime"]
        .diff()
        .dropna()
    )

    if not (
        time_difference == pd.Timedelta(hours=1)
    ).all():
        raise HTTPException(
            status_code=400,
            detail=(
                "Observations must be consecutive hourly "
                "measurements."
            ),
        )

    # --------------------------------------------------
    # 8. Create AirShift features
    # --------------------------------------------------

    try:
        featured = create_features(
            observations
        )

    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Feature engineering failed: {str(e)}",
        )

    # --------------------------------------------------
    # 9. Select latest observation
    # --------------------------------------------------

    final_row = featured.iloc[[-1]].copy()

    # --------------------------------------------------
    # 10. Validate model feature schema
    # --------------------------------------------------

    missing_features = [
        feature
        for feature in MODEL_FEATURES
        if feature not in final_row.columns
    ]

    if missing_features:
        raise HTTPException(
            status_code=500,
            detail={
                "error": (
                    "Generated features do not "
                    "match the model schema."
                ),
                "missing_features": missing_features,
            },
        )

    # --------------------------------------------------
    # 11. Select features in exact training order
    # --------------------------------------------------

    model_input = final_row[
        MODEL_FEATURES
    ]

    # --------------------------------------------------
    # 12. Check missing values
    # --------------------------------------------------

    if model_input.isna().any().any():

        missing_columns = (
            model_input.columns[
                model_input.isna().any()
            ]
            .tolist()
        )

        raise HTTPException(
            status_code=400,
            detail={
                "error": (
                    "Insufficient historical data "
                    "for feature generation."
                ),
                "missing_features": missing_columns,
            },
        )

    # --------------------------------------------------
    # 13. Generate prediction probability
    # --------------------------------------------------

    try:
        probability = float(
            final_xgb.predict_proba(
                model_input
            )[0, 1]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Prediction failed: {str(e)}",
        )

    # --------------------------------------------------
    # 14. Apply warning threshold
    # --------------------------------------------------

    early_warning = (
        probability >= WARNING_THRESHOLD
    )

    # --------------------------------------------------
    # 15. Prepare response
    # --------------------------------------------------

    prediction_time = (
        observations["datetime"].iloc[-1]
    )

    return PredictionResponse(
        prediction_time=prediction_time,
        station=stations[0],
        deterioration_probability=round(
            probability,
            4,
        ),
        warning_threshold=WARNING_THRESHOLD,
        early_warning=early_warning,
    )
