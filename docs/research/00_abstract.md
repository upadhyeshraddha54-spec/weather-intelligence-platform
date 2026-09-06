# Abstract

## Title

**An AI-Powered Multi-Agent Weather Intelligence and Climate Decision Support System for the Indian Southwest Monsoon**

## Abstract

India's Southwest Monsoon (June–September) is the primary determinant of the country's agricultural output, water resource availability, and disaster risk profile. Conventional meteorological decision-support systems provide raw forecasts but lack the integration of multiple data streams, risk intelligence, and contextual climate knowledge required by operational decision-makers.

This work presents a comprehensive AI-powered weather intelligence platform that integrates (1) real-time weather and air-quality observations from the Open-Meteo API, (2) machine learning temperature prediction using a Random Forest regressor, (3) a deep learning LSTM architecture for time-series temperature forecasting, (4) a MobileNetV2-based computer vision model for satellite cloud classification, (5) optional Sentinel-2 remote sensing via Microsoft Planetary Computer, (6) geospatial analytics for monsoon zone classification and bounding-box generation, (7) a FAISS-based retrieval-augmented generation (RAG) pipeline over a curated weather knowledge base, and (8) a multi-agent LangGraph workflow orchestrating specialist AI agents to produce a structured weather intelligence bulletin via a large language model (LLM).

The system is deployed as a FastAPI REST API with a Streamlit interactive dashboard and Docker containerisation. A comprehensive test suite of 141 unit tests ensures correctness of the classification, routing, and API contracts.

**Keywords:** Indian Southwest Monsoon, Multi-Agent AI, LangGraph, LangChain, Retrieval-Augmented Generation, LSTM, MobileNetV2, Satellite Remote Sensing, Weather Intelligence, Decision Support, FastAPI
