from datetime import datetime

from pydantic import BaseModel


class Observation(BaseModel):
    datetime: datetime
    PM2_5: float
    PM10: float
    SO2: float
    NO2: float
    CO: float
    O3: float
    TEMP: float
    PRES: float
    DEWP: float
    RAIN: float
    wd: str
    WSPM: float
    station: str


class PredictionRequest(BaseModel):
    observations: list[Observation]


class PredictionResponse(BaseModel):
    prediction_time: datetime
    station: str
    deterioration_probability: float
    warning_threshold: float
    early_warning: bool