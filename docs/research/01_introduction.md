# 1. Introduction

## 1.1 Background

India's Southwest Monsoon is one of the world's most significant climate phenomena, affecting the livelihoods of over 1.4 billion people. The monsoon season (June–September) contributes approximately 75% of India's annual rainfall and is critical for:

- Agricultural planning and crop yield forecasting
- Water reservoir management
- Flood and landslide early warning
- Public health and disease outbreak prevention (dengue, leptospirosis, cholera)
- Urban infrastructure and transport operations

Despite advances in numerical weather prediction (NWP) and satellite remote sensing, the translation of raw forecast data into actionable, contextualised intelligence for operational decision-makers remains a significant challenge. Existing systems often operate in silos — weather forecast models do not automatically integrate with air quality data, risk assessment frameworks, historical climate knowledge, or natural-language recommendations.

## 1.2 Motivation

The emergence of large language models (LLMs), retrieval-augmented generation (RAG), and agent-based AI frameworks (LangChain, LangGraph) creates an opportunity to bridge this gap. By combining real-time meteorological data with AI reasoning, we can provide:

1. **Contextualised intelligence** — not just "30mm rainfall expected" but "30mm rainfall in a region with history of urban flooding constitutes a flood risk requiring evacuation advisory"
2. **Multi-modal fusion** — integrating weather observations, satellite imagery, air quality, and climate knowledge into a coherent picture
3. **Natural language accessibility** — enabling non-expert users to query weather conditions in plain language and receive professional-grade intelligence bulletins

## 1.3 Contributions

This work makes the following contributions:

1. A complete multi-agent weather intelligence architecture combining 9 specialist AI agents in a directed acyclic LangGraph workflow
2. Integration of real-time Open-Meteo weather and AQI data with zero API cost
3. A RandomForest ML temperature prediction model with 6 engineered features
4. A PyTorch LSTM architecture for time-series temperature forecasting
5. A MobileNetV2 computer vision architecture for cloud/weather classification
6. Optional Sentinel-2 satellite integration via Microsoft Planetary Computer
7. A FAISS-based RAG pipeline over curated IMD weather knowledge documents
8. A production-ready FastAPI backend with 7 validated endpoints
9. An interactive Streamlit dashboard
10. A 141-test suite ensuring system correctness

## 1.4 Scope

The primary geographic focus is **peninsular India**, with special emphasis on the Southwest Monsoon belt (Maharashtra, Karnataka, Kerala, Andhra Pradesh, Telangana, Odisha). The system supports any city geocodable via the Open-Meteo API globally.

## 1.5 Paper Organisation

- Section 2: Problem Statement and Objectives
- Section 3: Related Work
- Section 4: Methodology and System Architecture
- Section 5: Data Sources and Description
- Section 6: ML/DL/CV Implementation
- Section 7: Multi-Agent Architecture
- Section 8: RAG Pipeline
- Section 9: API and Frontend
- Section 10: Experiments and Evaluation
- Section 11: Results and Discussion
- Section 12: Limitations and Future Work
- Section 13: Conclusion
