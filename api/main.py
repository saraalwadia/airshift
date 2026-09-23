from pathlib import Path

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


# Project paths
BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "xgboost_final.joblib"


# Load final trained model
final_xgb = joblib.load(MODEL_PATH)

# Get the exact feature names used during model training
MODEL_FEATURES = list(final_xgb.feature_names_in_)


app = FastAPI(
    title="AirShift API",
    description="Early Warning API for Air Quality Deterioration",
    version="1.0.0"
)


class PredictionRequest(BaseModel):
    features: dict


@app.get("/")
def root():
    return {
        "message": "AirShift API is running",
        "status": "ok"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": True
    }


@app.post("/predict")
def predict(request: PredictionRequest):

    missing_features = [
        feature
        for feature in MODEL_FEATURES
        if feature not in request.features
    ]

    if missing_features:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "Missing required features",
                "missing_features": missing_features
            }
        )

    try:
        input_data = pd.DataFrame(
            [request.features],
            columns=MODEL_FEATURES
        )

        probability = float(
            final_xgb.predict_proba(input_data)[0, 1]
        )

        warning = probability >= 0.30

        return {
            "deterioration_probability": round(probability, 4),
            "warning_threshold": 0.30,
            "early_warning": warning
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e)
        )