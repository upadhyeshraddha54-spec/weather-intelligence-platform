# 10. Results and Discussion

> **Note:** This section documents verified system behaviour. 
> Quantitative ML/DL accuracy metrics are placeholders — they will be 
> populated after training on a full historical dataset.

## 10.1 System Functionality

| Component | Status | Verified |
|-----------|--------|---------|
| Live Weather API | Operational | ✅ |
| Live AQI API | Operational | ✅ |
| 8-Day Forecast | Operational | ✅ |
| Random Forest Prediction | Operational (28.12°C for test input) | ✅ |
| LSTM Architecture | Built, awaiting training data | ⚠️ |
| CV Architecture | Built, awaiting fine-tuning data | ⚠️ |
| Satellite (Sentinel-2) | Honest unavailable state | ✅ |
| Geospatial Analytics | Operational (Pune = Moderate Monsoon Zone) | ✅ |
| RAG Pipeline | Operational (real PDF content retrieved) | ✅ |
| Multi-Agent LangGraph | Operational (9 nodes, conditional routing) | ✅ |
| LLM Bulletin | Operational (Groq qwen/qwen3.8-27b) | ✅ |
| FastAPI (7 endpoints) | Operational | ✅ |
| Streamlit Dashboard | Operational | ✅ |

## 10.2 API Verification

End-to-end API test results (live, 2026-09-06, Pune, India):

**`POST /analyze` — "What is the current weather and AQI?"**
- Selected agents: `["weather", "aqi"]`
- Temperature: 27.7°C, Humidity: 68%, Wind: 14.3 km/h
- AQI: 39 (Good), PM2.5: 8.8 µg/m³, PM10: 17.2 µg/m³
- Bulletin: 7-section structured report generated ✅

**`POST /predict`**
- Input: humidity=72, precip=0, month=9, day=6, dayofweek=6, season=2
- Output: `{"predicted_temperature_celsius": 28.12}` ✅

**`GET /geo/Pune`**
- Latitude: 18.5204, Longitude: 73.8567
- Monsoon Zone: Moderate Monsoon Zone ✅

## 10.3 Test Suite Results

```
141 tests collected
141 passed
0 failed
0 errors
Runtime: ~6 seconds (all offline, no network required)
```

Test coverage by module:
| Module | Tests |
|--------|-------|
| forecast_risk (classification) | 21 |
| risk_agent | 7 |
| LangGraph routing | 9 |
| WeatherState schema | 2 |
| bulletin_generator | 6 |
| API contract | 4 |
| DL (LSTM) | 18 |
| CV (MobileNetV2) | 13 |
| Geospatial | 23 |
| API endpoints | 25 |
| LLM config | 7 |
| RAG / satellite | 5 |
| data config | 2 |

## 10.4 ML Model Performance

> *Placeholder — to be completed after training on full historical dataset.*

**Random Forest Regressor:**
- Training dataset: `weather_data.csv`
- Features: humidity, precipitation, month, day, dayofweek, season
- Target: temperature (°C)
- Metrics: RMSE, MAE, R² — *to be measured*

## 10.5 DL Model Performance

> *Placeholder — to be completed after training.*

**LSTM (2-layer, hidden=64):**
- Input: 24-step × 6-feature sequences
- Target: next-step temperature
- Metrics: MSE (validation), MAE — *to be measured after training*

## 10.6 CV Model Performance

> *Placeholder — to be completed after fine-tuning.*

**MobileNetV2 Cloud Classifier:**
- Classes: Clear, Partly Cloudy, Mostly Cloudy, Rain/Convective, Thunderstorm/Severe
- Metrics: Accuracy, F1-score per class — *to be measured after fine-tuning*
