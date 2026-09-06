# 🌦️ AI Weather Intelligence Platform

**An AI-powered multi-agent weather intelligence and climate decision support system focused on the Indian Southwest Monsoon.**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-2.0-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.6-orange.svg)](https://langchain-ai.github.io/langgraph/)
[![Tests](https://img.shields.io/badge/tests-141%20passed-brightgreen.svg)](#testing)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## Problem Statement

India's Southwest Monsoon (June–September) accounts for ~75% of the country's annual rainfall and directly impacts agriculture, water resources, disaster management, and public health. Existing weather systems often operate in silos — raw forecasts are not automatically integrated with risk assessment, historical climate knowledge, or actionable recommendations.

This platform addresses that gap by combining **real-time open weather data**, **machine learning**, **deep learning**, **computer vision**, **retrieval-augmented generation (RAG)**, and **LLM-powered multi-agent reasoning** into a unified decision support system.

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────────────┐
│              LangGraph Workflow              │
│                                             │
│  Supervisor Agent  →  Dispatcher            │
│         │                                   │
│    ┌────▼────────────────────────────────┐  │
│    │  Specialist Agents (in sequence)   │  │
│    │                                    │  │
│    │  Weather ──► AQI ──► Forecast      │  │
│    │      └──► Satellite                │  │
│    │      └──► Risk ──► RAG             │  │
│    │                    │               │  │
│    │              Bulletin Agent        │  │
│    └────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
    │
    ▼
Weather Intelligence Bulletin
```

### Data Flow

```
Open-Meteo API ──► Live Weather + AQI + Forecast (no API key required)
Sentinel-2 ──────► Satellite Imagery Metadata (optional: pystac-client)
PDF Documents ───► RAG Vector Database (FAISS + sentence-transformers)
ML Model ────────► Temperature Prediction (RandomForest)
DL Model ────────► LSTM Time-Series Forecast (requires training)
CV Model ────────► Cloud Classification (MobileNetV2, requires fine-tuning)
Groq / Ollama ───► LLM Reasoning (qwen/qwen3.8-27b)
```

---

## Features

| Feature | Status | Notes |
|---------|--------|-------|
| Live Weather (temp, humidity, wind, pressure, rain) | ✅ | Open-Meteo, no key |
| Live AQI (PM2.5, PM10, NO₂, Ozone) | ✅ | Open-Meteo Air Quality API |
| 8-day Forecast | ✅ | Open-Meteo forecast API |
| ML Temperature Prediction | ✅ | RandomForest, trained model included |
| Deep Learning LSTM | ✅ arch | Requires `weather_data.csv` to train |
| Computer Vision Cloud Classifier | ✅ arch | Requires labelled dataset to fine-tune |
| Satellite Imagery | ✅ graceful | Needs `pystac-client` + `planetary-computer` |
| Geospatial Analytics | ✅ | City coords, monsoon zones, bbox, GeoJSON |
| RAG Knowledge Base | ✅ | 3 weather/climate PDFs indexed in FAISS |
| Multi-Agent LangGraph | ✅ | 9-node graph, conditional routing |
| LLM Integration | ✅ | Groq (default) or Ollama |
| Tool Calling | ✅ | weather_tool, risk_tool, search_weather_knowledge |
| Risk Intelligence | ✅ | Rule-based + LLM-explained |
| AI Weather Bulletin | ✅ | Structured 7-section LLM bulletin |
| FastAPI Backend | ✅ | 7 endpoints, Pydantic validation |
| Streamlit Dashboard | ✅ | Current weather, 8-day forecast, charts |
| Docker | ✅ | Dockerfile + docker-compose.yml |
| Tests | ✅ | 141 unit tests, all passing |

---

## Technology Stack

| Category | Technology |
|----------|-----------|
| Language | Python 3.9+ |
| ML Framework | scikit-learn (RandomForest) |
| Deep Learning | PyTorch + LSTM |
| Computer Vision | PyTorch + torchvision (MobileNetV2) |
| LLM | Groq API (qwen/qwen3.8-27b) / Ollama |
| LLM Framework | LangChain + LangGraph |
| Vector DB | FAISS |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) |
| Weather Data | Open-Meteo (free, no API key) |
| Satellite | Sentinel-2 via Microsoft Planetary Computer |
| API Framework | FastAPI + Pydantic v2 |
| Frontend | Streamlit |
| Containerisation | Docker + Docker Compose |
| Testing | pytest (141 tests) |

---

## Project Structure

```
weather-intelligence-platform/
├── src/
│   ├── agent/           # Specialist LLM agents
│   │   ├── supervisor_agent.py
│   │   ├── weather_agent.py
│   │   ├── aqi_agent.py
│   │   ├── forecast_agent.py
│   │   ├── risk_agent.py
│   │   ├── rag_tool.py
│   │   ├── bulletin_generator.py
│   │   └── tools.py
│   ├── api/             # FastAPI backend
│   │   ├── app.py       # Main application (7 endpoints)
│   │   └── schema.py
│   ├── cv/              # Computer Vision
│   │   └── cloud_classifier.py
│   ├── data/            # Data engineering pipeline
│   │   ├── collector.py
│   │   ├── preprocessing.py
│   │   ├── storage.py
│   │   └── model.py
│   ├── dl/              # Deep Learning (LSTM)
│   │   ├── lstm_model.py
│   │   └── train.py
│   ├── forecast/        # Time-series forecasting
│   │   ├── live_forecast.py
│   │   └── forecast_risk.py
│   ├── geospatial/      # Geospatial analytics
│   │   └── geo_utils.py
│   ├── graph/           # LangGraph workflow
│   │   ├── workflow.py
│   │   ├── nodes.py
│   │   ├── state.py
│   │   └── dispatcher.py
│   ├── llm/             # LLM backend abstraction
│   │   └── llm.py
│   ├── rag/             # RAG pipeline
│   │   ├── ingest.py
│   │   └── query.py
│   ├── satellite/       # Satellite / remote sensing
│   │   ├── satellite_fetcher.py
│   │   ├── satellite_analysis.py
│   │   └── satellite_agent.py
│   └── weather/         # Live weather fetcher
│       └── live_weather.py
├── frontend/
│   └── app.py           # Streamlit dashboard
├── tests/               # 141 unit tests
│   ├── test_unit.py
│   ├── test_dl.py
│   ├── test_cv.py
│   ├── test_geo.py
│   ├── test_api.py
│   └── test_llm.py
├── docs/
│   ├── research/        # Research paper documentation
│   └── *.pdf            # Weather/climate knowledge base
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── requirements-docker.txt
├── .env.example
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.9+
- pip
- A Groq API key ([get one free](https://console.groq.com/keys))

### 1. Clone and set up

```bash
git clone <repository-url>
cd weather-intelligence-platform

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements-docker.txt
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env and set your GROQ_API_KEY
```

### 3. Build the RAG knowledge base

```bash
python src/rag/ingest.py
```

This indexes the 3 PDF documents in `docs/` into a FAISS vector database.
Only needs to be run once (or after adding new documents).

---

## Running Locally

### FastAPI Backend

```bash
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000
```

API docs available at: http://localhost:8000/docs

### Streamlit Frontend

```bash
streamlit run frontend/app.py
```

Dashboard available at: http://localhost:8501

### CLI Weather Analysis

```bash
python -m src.graph.workflow
```

---

## Running with Docker

```bash
# Build and start all services
docker compose up --build

# API:       http://localhost:8000
# Streamlit: http://localhost:8501
```

Required files before Docker:
- `.env` with `GROQ_API_KEY`
- `best_weather_model.pkl` (included)
- `weather_vector_db/` (run `python src/rag/ingest.py` first)

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Health check + component status |
| `POST` | `/predict` | RandomForest temperature prediction |
| `POST` | `/predict/dl` | LSTM deep-learning prediction (requires training) |
| `GET` | `/dl/info` | LSTM model metadata |
| `GET` | `/cv/info` | CV model metadata |
| `GET` | `/geo/{city}` | Geospatial summary (coords, monsoon zone, bbox) |
| `POST` | `/analyze` | Full multi-agent weather intelligence analysis |

### Example: Full Analysis

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{"city": "Pune", "question": "What is the weather and AQI today?"}'
```

### Example: Temperature Prediction

```bash
curl -X POST http://localhost:8000/predict \
  -H "Content-Type: application/json" \
  -d '{"humidity": 72, "precip": 0.0, "month": 9, "day": 6, "dayofweek": 6, "season": 2}'
```

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GROQ_API_KEY` | Yes (Groq) | — | Groq cloud API key |
| `LLM_PROVIDER` | No | `groq` | `groq` or `ollama` |
| `GROQ_MODEL` | No | `qwen/qwen3.8-27b` | Groq model name |
| `OLLAMA_BASE_URL` | No | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | No | `qwen3:8b` | Ollama model name |
| `TRANSFORMERS_OFFLINE` | No | — | Set to `1` in offline/Docker |

---

## Training the Deep Learning Model

The LSTM model requires a training dataset:

```bash
# 1. Collect weather data (generates weather_data.csv)
python src/main.py

# 2. Train the LSTM model
python src/dl/train.py
# Saves best_dl_model.pt when training completes
```

**Training configuration** (`src/dl/train.py`):
- Architecture: 2-layer stacked LSTM, hidden_size=64
- Input: 24-step sequences × 6 features
- Target: next-step temperature
- Epochs: 30, batch_size: 64, LR: 1e-3 (with ReduceLROnPlateau)
- Framework: PyTorch

---

## Fine-tuning the CV Model

The cloud classifier uses MobileNetV2 (ImageNet backbone). Fine-tuning requires a labelled cloud/satellite dataset:

1. Prepare images in class folders: `Clear/`, `Partly_Cloudy/`, `Mostly_Cloudy/`, `Rain_Convective/`, `Thunderstorm_Severe/`
2. Write a training script using `src/cv/cloud_classifier.py:WeatherLSTM`
3. Save fine-tuned weights to `best_cv_model.pt`

Suitable datasets: [EUMETSAT](https://www.eumetsat.int/), [Kaggle Cloud datasets](https://www.kaggle.com/search?q=cloud+classification), [NASA GOES imagery](https://registry.opendata.aws/noaa-goes/)

---

## Satellite Integration

Optional Sentinel-2 support via Microsoft Planetary Computer:

```bash
pip install pystac-client planetary-computer
```

When installed, the satellite agent fetches real Sentinel-2 L2A metadata and classifies cloud conditions. Without these packages, the system returns an honest "unavailable" state.

---

## Testing

```bash
# Run all 141 tests
python -m pytest tests/ -v

# Run specific modules
python -m pytest tests/test_dl.py -v      # DL tests
python -m pytest tests/test_cv.py -v      # CV tests
python -m pytest tests/test_geo.py -v     # Geospatial tests
python -m pytest tests/test_api.py -v     # API tests
python -m pytest tests/test_unit.py -v    # Core logic tests
```

**Current test coverage:**
- 141 tests, 141 passing
- Covers: ML, DL, CV, Geospatial, API, LLM config, LangGraph routing, risk classification, forecast classification, RAG, satellite, bulletin generator, state schema

---

## Data Sources

| Source | Data | License | Key Required |
|--------|------|---------|--------------|
| [Open-Meteo](https://open-meteo.com/) | Weather, AQI, Forecast | Open (CC BY 4.0) | No |
| [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/) | Sentinel-2 imagery | Various open licenses | Optional |
| IMD/WMO PDFs | Weather SOPs, climate knowledge | Public domain | No |

---

## Limitations

1. **DL model not pre-trained** — requires `weather_data.csv` (generated by running the pipeline) to train.
2. **CV model not fine-tuned** — backbone is ImageNet-pretrained; cloud classification head requires a labelled satellite dataset.
3. **Satellite data optional** — requires `pystac-client` and `planetary-computer` packages.
4. **AQI data** — Open-Meteo AQI may return N/A for some locations; falls back gracefully.
5. **LLM** — requires a valid Groq API key or a locally running Ollama instance.

---

## Future Work

- Fine-tune CV model on real EUMETSAT/Kaggle cloud datasets
- Collect historical weather data and train the LSTM model
- Add IMD (India Meteorological Department) API integration
- Expand city coverage beyond Indian cities
- Add WebSocket support for real-time weather updates
- Implement historical trend analysis
- Add multi-language support (Hindi, Marathi)
- Deploy to cloud (AWS/GCP) with CI/CD pipeline

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Acknowledgements

- [Open-Meteo](https://open-meteo.com/) for free weather API
- [Groq](https://groq.com/) for fast LLM inference
- [LangChain](https://langchain.com/) / [LangGraph](https://langchain-ai.github.io/langgraph/) for agent framework
- [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/) for satellite data
- India Meteorological Department for weather SOPs used in the knowledge base
