"""
Weather Intelligence Platform — FastAPI application.

Endpoints
---------
  GET  /               — health check + component status
  POST /predict        — ML (RandomForest) temperature prediction
  POST /predict/dl     — DL (LSTM) temperature prediction
  POST /analyze        — full multi-agent LangGraph weather intelligence
  GET  /cv/info        — CV model info
  GET  /dl/info        — DL model info
  GET  /geo/{city}     — geospatial summary for a city

Data truthfulness
-----------------
All weather data comes from Open-Meteo (free, no API key required).
ML/DL predictions are clearly marked with their model source.
Satellite, CV, and DL components return honest unavailable states
when their optional weights/dependencies are absent.
"""
import os
import logging
from typing import Optional, List

import joblib
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.graph.workflow import weather_graph

logger = logging.getLogger(__name__)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="Weather Intelligence Platform API",
    version="2.0.0",
    description=(
        "AI-powered multi-agent weather intelligence and climate "
        "decision support platform for the Indian Southwest Monsoon.\n\n"
        "Data sources: Open-Meteo (weather + AQI + forecast), "
        "Sentinel-2 / Planetary Computer (satellite, optional), "
        "PDF knowledge base (RAG).\n\n"
        "LLM: Groq (qwen/qwen3.8-27b) or Ollama (configurable via LLM_PROVIDER env)."
    ),
)


# ============================================================
# LOAD ML MODEL (RandomForest)
# ============================================================

_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "best_weather_model.pkl",
)

_ml_model = None
_ml_model_error: str = ""

try:
    _ml_model = joblib.load(_MODEL_PATH)
    logger.info("ML model loaded from %s", _MODEL_PATH)
except FileNotFoundError:
    _ml_model_error = f"ML model file not found at: {_MODEL_PATH}"
    logger.warning(_ml_model_error)
except Exception as exc:
    _ml_model_error = f"ML model could not be loaded: {exc}"
    logger.error(_ml_model_error)


# ============================================================
# SCHEMAS
# ============================================================

class WeatherInput(BaseModel):
    """Input for the /predict (RandomForest) endpoint."""
    humidity: float = Field(..., ge=0, le=100, description="Humidity (%)")
    precip: float = Field(..., ge=0, description="Precipitation (mm)")
    month: int = Field(..., ge=1, le=12, description="Month (1-12)")
    day: int = Field(..., ge=1, le=31, description="Day of month")
    dayofweek: int = Field(..., ge=0, le=6, description="Day of week (0=Mon)")
    season: int = Field(..., ge=0, le=3, description="Season (0=Winter … 3=Post-Monsoon)")


class DLWeatherInput(BaseModel):
    """
    Input for the /predict/dl (LSTM) endpoint.

    sequence: list of exactly 24 time steps, each with 6 features in order:
      [temperature_c, humidity_pct, precipitation_mm, wind_speed_kmh, month, hour]
    """
    sequence: List[List[float]] = Field(
        ...,
        description=(
            "24 time-steps × 6 features: "
            "[temperature_c, humidity_pct, precipitation_mm, wind_speed_kmh, month, hour]"
        ),
    )


class WeatherQuery(BaseModel):
    """Input for the /analyze endpoint."""
    city: str = Field(..., description="City name, e.g. Pune")
    question: str = Field(..., description="Natural-language weather question")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/", summary="Health check and component status")
def root():
    """Returns API health status and loaded component information."""
    from src.dl.lstm_model import get_model_info as dl_info
    from src.cv.cloud_classifier import get_cv_model_info as cv_info
    from src.llm.llm import get_llm_info

    return {
        "status": "online",
        "service": "Weather Intelligence Platform API",
        "version": "2.0.0",
        "components": {
            "ml_model": {
                "loaded": _ml_model is not None,
                "type": "RandomForestRegressor",
                "error": _ml_model_error or None,
            },
            "dl_model": dl_info(),
            "cv_model": cv_info(),
            "llm": get_llm_info(),
        },
    }


# ============================================================
# ML PREDICTION (RandomForest)
# ============================================================

@app.post("/predict", summary="RandomForest temperature prediction")
def predict(data: WeatherInput):
    """Predict temperature (°C) using the trained RandomForest model."""
    if _ml_model is None:
        raise HTTPException(
            status_code=503,
            detail=f"ML model unavailable: {_ml_model_error}",
        )

    input_df = pd.DataFrame([{
        "humidity": data.humidity,
        "precip": data.precip,
        "Month": data.month,
        "Day": data.day,
        "DayOfWeek": data.dayofweek,
        "Season": data.season,
    }])

    try:
        prediction = _ml_model.predict(input_df)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {exc}")

    return {
        "predicted_temperature_celsius": round(float(prediction[0]), 2),
        "model": "RandomForestRegressor",
        "input": data.model_dump(),
    }


# ============================================================
# DL PREDICTION (LSTM)
# ============================================================

@app.post("/predict/dl", summary="LSTM deep-learning temperature prediction")
def predict_dl(data: DLWeatherInput):
    """
    Predict next-step temperature using the LSTM model.

    Requires ``best_dl_model.pt`` in the project root.
    Returns status=``untrained`` (not an error) when weights are absent.
    """
    from src.dl.lstm_model import predict_next_temperature, SEQ_LEN, N_FEATURES

    seq = data.sequence
    if len(seq) != SEQ_LEN:
        raise HTTPException(
            status_code=422,
            detail=f"sequence must have exactly {SEQ_LEN} time steps, got {len(seq)}.",
        )
    if any(len(row) != N_FEATURES for row in seq):
        raise HTTPException(
            status_code=422,
            detail=f"Each time step must have exactly {N_FEATURES} features.",
        )

    arr = np.array(seq, dtype=np.float32)
    result = predict_next_temperature(arr)
    return result


# ============================================================
# CV MODEL INFO
# ============================================================

@app.get("/cv/info", summary="Computer Vision model information")
def cv_info():
    """Return metadata about the cloud classification CV model."""
    from src.cv.cloud_classifier import get_cv_model_info
    return get_cv_model_info()


# ============================================================
# DL MODEL INFO
# ============================================================

@app.get("/dl/info", summary="Deep Learning model information")
def dl_info():
    """Return metadata about the LSTM deep-learning model."""
    from src.dl.lstm_model import get_model_info
    return get_model_info()


# ============================================================
# GEOSPATIAL
# ============================================================

@app.get("/geo/{city}", summary="Geospatial summary for a city")
def geo_summary(city: str):
    """
    Return coordinates, monsoon zone, bounding box, and GeoJSON
    for the requested city.
    """
    from src.geospatial.geo_utils import get_location_summary
    result = get_location_summary(city)
    if result["status"] == "unavailable":
        raise HTTPException(status_code=404, detail=result["message"])
    return result


# ============================================================
# FULL MULTI-AGENT ANALYSIS
# ============================================================

@app.post("/analyze", summary="Full multi-agent weather intelligence analysis")
def analyze_weather(data: WeatherQuery):
    """
    Run the complete LangGraph multi-agent pipeline for a city.

    Pipeline:
      supervisor → dispatcher → [weather, aqi, forecast, satellite, risk, rag] → bulletin

    Returns a structured weather intelligence bulletin with all available data.
    """
    city = data.city.strip()
    question = data.question.strip()

    if not city:
        raise HTTPException(status_code=400, detail="city is required.")
    if not question:
        raise HTTPException(status_code=400, detail="question is required.")

    state = {
        "city": city,
        "user_query": question,
        "selected_agents": [],
        "weather": None,
        "aqi": None,
        "forecast": None,
        "satellite": None,
        "risk": [],
        "rag": "",
        "bulletin": "",
        "decision_logs": [],
    }

    try:
        result = weather_graph.invoke(state)
    except Exception as exc:
        logger.error("Weather graph failed for city=%s: %s", city, exc)
        raise HTTPException(
            status_code=500,
            detail=f"Weather analysis failed: {exc}",
        )

    return {
        "city": result.get("city", city),
        "question": question,
        "selected_agents": result.get("selected_agents", []),
        "weather": result.get("weather"),
        "aqi": result.get("aqi"),
        "forecast": result.get("forecast"),
        "satellite": result.get("satellite"),
        "risk": result.get("risk", []),
        "rag": result.get("rag", ""),
        "bulletin": result.get("bulletin", ""),
        "decision_logs": result.get("decision_logs", []),
    }
