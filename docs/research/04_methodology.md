# 4. Methodology and System Architecture

## 4.1 Overall Architecture

The platform follows a **multi-tier agent-based architecture**:

```
Layer 1: Data Acquisition
  Open-Meteo Weather API → current weather, forecast, AQI
  Sentinel-2 via Planetary Computer → satellite imagery metadata (optional)

Layer 2: ML/DL/CV Processing
  RandomForest → temperature prediction
  LSTM → time-series temperature forecasting
  MobileNetV2 → cloud/weather image classification

Layer 3: Agent Orchestration (LangGraph)
  Supervisor → Dispatcher → Specialist Agents → Bulletin

Layer 4: Knowledge Retrieval (RAG)
  PDF Documents → FAISS Vector DB → Semantic Search → Context

Layer 5: LLM Reasoning (Groq / Ollama)
  Retrieved context + observations → structured bulletin

Layer 6: API + Frontend
  FastAPI REST API → Streamlit Dashboard
```

## 4.2 LangGraph Multi-Agent Workflow

The workflow is implemented as a `StateGraph` with 9 nodes:

```
supervisor → dispatcher → weather → aqi → forecast → satellite → risk → rag → bulletin → END
```

Routing is **conditional** — the Supervisor LLM determines which agents are required based on the user query. The routing functions follow the precedence:

```
after_dispatcher: weather > aqi > forecast > satellite > risk > rag > bulletin
after_weather:    aqi > forecast > satellite > risk > rag > bulletin
after_aqi:        forecast > satellite > risk > rag > bulletin
after_forecast:   satellite > risk > rag > bulletin
after_satellite:  risk > rag > bulletin
after_risk:       rag > bulletin
```

All nodes have:
- Error handling with graceful fallback
- Timing instrumentation
- Honest unavailable states when external data is inaccessible

## 4.3 Machine Learning (Random Forest)

**Model:** `sklearn.ensemble.RandomForestRegressor`

**Features:**
| Feature | Description |
|---------|-------------|
| humidity | Relative humidity (%) |
| precip | Precipitation (mm) |
| Month | Calendar month (1-12) |
| Day | Day of month (1-31) |
| DayOfWeek | Day of week (0=Monday) |
| Season | 0=Winter, 1=Summer, 2=Monsoon, 3=Post-Monsoon |

**Target:** Temperature (°C)

**Training data:** `weather_data.csv` collected via Open-Meteo API

## 4.4 Deep Learning (LSTM)

**Architecture:** Stacked LSTM (2 layers, hidden_size=64) + Linear head

**Input:** 24-step sliding window × 6 features:
- temperature_c, humidity_pct, precipitation_mm, wind_speed_kmh, month, hour

**Target:** Next time-step temperature (regression)

**Normalisation:** Feature-wise min-max to [0, 1] using Indian climate ranges

**Training configuration:**
- Loss: MSELoss
- Optimiser: Adam (lr=1e-3)
- Scheduler: ReduceLROnPlateau (patience=5)
- Epochs: 30
- Batch size: 64

**Status:** Architecture implemented; weights require training on `weather_data.csv`

## 4.5 Computer Vision (MobileNetV2)

**Architecture:** MobileNetV2 (ImageNet pretrained) + Dropout(0.2) + Linear(1280→5)

**Classes:**
0. Clear
1. Partly Cloudy
2. Mostly Cloudy
3. Rain / Convective
4. Thunderstorm / Severe

**Input:** 224×224 RGB, ImageNet normalisation

**Status:** Architecture implemented with pretrained backbone; classification head requires fine-tuning on a labelled cloud dataset

**Inference:** Returns `status="untrained"` with `class_name=None` when fine-tuned weights are absent — does not fabricate predictions.

## 4.6 Remote Sensing (Sentinel-2)

**Source:** Microsoft Planetary Computer STAC API

**Data:** Sentinel-2 L2A tile metadata (date, cloud cover %)

**Cloud classification:**
| Cloud Cover (%) | Condition | Rain Potential | Visibility |
|----------------|-----------|----------------|------------|
| ≥ 80 | Overcast | High | Poor |
| 50–79 | Mostly Cloudy | Moderate | Moderate |
| 20–49 | Partly Cloudy | Low | Good |
| < 20 | Clear | Low | Good |

**Dependencies:** `pystac-client`, `planetary-computer` (optional)

## 4.7 Geospatial Analytics

**Capabilities:**
- City → WGS-84 coordinate lookup (static table + geocoding fallback)
- Bounding box generation (configurable radius in km)
- Haversine great-circle distance
- Indian Southwest Monsoon zone classification
- GeoJSON Feature generation for map rendering

**Monsoon zones classified:**
- Heavy Monsoon Zone (West coast + Deccan, 8–18°N, 73–82°E)
- Moderate Monsoon Zone (Central India, 18–26°N, 70–88°E)
- Weak Monsoon Zone (Northwest India)
- Northeast Monsoon Zone (Tamil Nadu coast)

## 4.8 RAG Pipeline

**Documents:** 3 IMD/WMO weather knowledge PDFs:
- `forecasting_sop.pdf` — Weather Forecasting and Warning SOP
- `cyclone_sop.pdf` — Cyclone Standard Operating Procedure
- `FAQ_heat_wave.pdf` — Heat Wave FAQ

**Pipeline:**
```
PDFs → PyPDF loader → RecursiveCharacterTextSplitter (chunk=1000, overlap=200)
     → HuggingFace Embeddings (all-MiniLM-L6-v2, 384-dim)
     → FAISS index (cosine similarity)
     → Top-3 retrieved chunks → LLM context
```

**Query:** Natural language weather/climate question → top-3 semantically similar document chunks → included in LLM prompt for grounded responses

## 4.9 LLM Integration

**Primary:** Groq API (qwen/qwen3.8-27b)
**Fallback:** Ollama (configurable via `LLM_PROVIDER=ollama`)

**LLM tasks:**
1. Supervisor routing — which agents to invoke
2. AQI analysis — interpret air quality readings
3. Forecast explanation — explain multi-day forecast
4. Bulletin generation — structured 7-section intelligence report

**Anti-hallucination measures:**
- All prompts supply verified factual data from APIs
- LLM instructed not to invent observations, warnings, or forecasts
- Bulletin template constrains output structure
