"""
LangGraph node functions for the Weather Intelligence Platform.

Each node receives the current graph state, performs its specialist task,
updates the relevant state field, and returns the updated state.
"""
import time
import logging

from src.weather.live_weather import get_live_weather
from src.agent.aqi_agent import run_aqi_agent
from src.agent.risk_agent import assess_risk
from src.agent.rag_tool import search_weather_knowledge
from src.agent.bulletin_generator import generate_bulletin
from src.agent.supervisor_agent import decide_agents
from src.graph.dispatcher import dispatch
from src.agent.forecast_agent import run_forecast_agent
from src.satellite.satellite_agent import run_satellite_agent

logger = logging.getLogger(__name__)


# -----------------------------------------------------------------------
# Supervisor Node
# -----------------------------------------------------------------------

def supervisor_node(state):
    """Use the LLM to decide which specialist agents are needed."""
    start = time.time()
    try:
        decision = decide_agents(state["user_query"])

        agents = [
            agent.strip()
            for agent in decision.split(",")
            if agent.strip()
        ]

        state["selected_agents"] = agents

        print("\n🧠 Supervisor selected:")
        print(agents)
    except Exception as exc:
        logger.error("Supervisor agent failed: %s", exc)
        # Fall back to running the full pipeline so the user gets *something*.
        state["selected_agents"] = ["weather", "forecast", "risk"]
        state.setdefault("decision_logs", []).append(
            f"Supervisor fallback (error: {exc})"
        )
    finally:
        print(
            f"✅ Supervisor Agent completed in "
            f"{time.time() - start:.2f} sec"
        )

    return state


# -----------------------------------------------------------------------
# Dispatcher Node
# -----------------------------------------------------------------------

def dispatcher_node(state):
    """Log which agents have been selected."""
    start = time.time()
    try:
        state = dispatch(state)
    finally:
        print(
            f"✅ Dispatcher completed in {time.time() - start:.2f} sec"
        )
    return state


# -----------------------------------------------------------------------
# Weather Node
# -----------------------------------------------------------------------

def weather_node(state):
    """Fetch current live weather for the requested city."""
    print("\n🌦 Running Weather Agent...")
    start = time.time()
    try:
        result = get_live_weather(state["city"])
        if result is None:
            state["decision_logs"] = state.get("decision_logs", []) + [
                f"Weather: city '{state['city']}' not found."
            ]
        state["weather"] = result
    except Exception as exc:
        logger.error("Weather node failed: %s", exc)
        state["weather"] = None
        state["decision_logs"] = state.get("decision_logs", []) + [
            f"Weather: fetch failed ({exc})"
        ]
    finally:
        print(
            f"✅ Weather Agent completed in {time.time() - start:.2f} sec"
        )
    return state


# -----------------------------------------------------------------------
# AQI Node
# -----------------------------------------------------------------------

def aqi_node(state):
    """Fetch live air quality data and perform LLM analysis."""
    print("\n🌫 Running AQI Agent...")
    start = time.time()
    try:
        state["aqi"] = run_aqi_agent(state["city"])
    except Exception as exc:
        logger.error("AQI node failed: %s", exc)
        state["aqi"] = {
            "city": state["city"],
            "status": "ERROR",
            "message": f"AQI data unavailable: {exc}",
        }
    finally:
        print(
            f"✅ AQI Agent completed in {time.time() - start:.2f} sec"
        )
    return state


# -----------------------------------------------------------------------
# Forecast Node
# -----------------------------------------------------------------------

def forecast_node(state):
    """Fetch multi-day forecast and generate LLM summary."""
    print("\n📅 Running Forecast Agent...")
    start = time.time()
    try:
        state["forecast"] = run_forecast_agent(
            state["city"],
            state.get("user_query", ""),
        )
    except Exception as exc:
        logger.error("Forecast node failed: %s", exc)
        state["forecast"] = {
            "city": state["city"],
            "status": "ERROR",
            "message": f"Forecast unavailable: {exc}",
            "forecast": [],
            "forecast_analysis": [],
            "analysis": "Forecast data could not be retrieved.",
        }
    finally:
        print(
            f"✅ Forecast Agent completed in {time.time() - start:.2f} sec"
        )
    return state


# -----------------------------------------------------------------------
# Satellite Node
# -----------------------------------------------------------------------

def satellite_node(state):
    """Fetch latest satellite metadata for the requested city."""
    print("\n🛰 Running Satellite Agent...")
    start = time.time()
    try:
        state["satellite"] = run_satellite_agent(state.get("city", ""))
    except Exception as exc:
        logger.error("Satellite node failed: %s", exc)
        state["satellite"] = {
            "status": "unavailable",
            "message": f"Satellite data unavailable: {exc}",
            "image_date": "N/A",
            "cloud_cover": "N/A",
            "condition": "N/A",
            "rain_potential": "N/A",
            "visibility": "N/A",
            "confidence": "N/A",
            "summary": "Satellite analysis was not performed.",
        }
    finally:
        print(
            f"✅ Satellite Agent completed in {time.time() - start:.2f} sec"
        )
    return state


# -----------------------------------------------------------------------
# Risk Node
# -----------------------------------------------------------------------

def risk_node(state):
    """Assess weather and air-quality risks from live observations."""
    print("\n🚨 Running Risk Agent...")
    start = time.time()
    try:
        weather = state.get("weather")

        # If weather node didn't run, fetch data directly.
        if weather is None:
            try:
                weather = get_live_weather(state["city"])
            except Exception as exc:
                logger.warning("Risk node could not fetch weather: %s", exc)
                weather = None

        if weather is None:
            state["risk"] = ["Weather data unavailable — risk assessment could not be performed."]
        else:
            state["risk"] = assess_risk(weather)

    except Exception as exc:
        logger.error("Risk node failed: %s", exc)
        state["risk"] = [f"Risk assessment failed: {exc}"]
    finally:
        print(
            f"✅ Risk Agent completed in {time.time() - start:.2f} sec"
        )
    return state


# -----------------------------------------------------------------------
# RAG Node
# -----------------------------------------------------------------------

def rag_node(state):
    """Search the weather knowledge base for relevant context."""
    print("\n📚 Running RAG Agent...")
    start = time.time()
    try:
        state["rag"] = search_weather_knowledge.invoke(
            {"query": state["user_query"]}
        )
    except Exception as exc:
        logger.error("RAG node failed: %s", exc)
        state["rag"] = "Knowledge base search was not available."
    finally:
        print(
            f"✅ RAG Agent completed in {time.time() - start:.2f} sec"
        )
    return state


# -----------------------------------------------------------------------
# Bulletin Node
# -----------------------------------------------------------------------

def bulletin_node(state):
    """Generate the final weather intelligence bulletin via LLM."""
    print("\n📝 Running Bulletin Agent...")
    start = time.time()
    try:
        weather = state.get("weather")

        # If weather agent didn't run, try to reuse AQI data.
        if weather is None:
            aqi_data = state.get("aqi")
            weather = dict(aqi_data) if isinstance(aqi_data, dict) else {}

        if not isinstance(weather, dict):
            weather = {}

        # Merge AQI values into weather dict for the bulletin template.
        aqi = state.get("aqi") or {}
        if isinstance(aqi, dict):
            weather.update(
                {
                    "aqi": aqi.get("aqi", "N/A"),
                    "pm2_5": aqi.get("pm2_5", "N/A"),
                    "pm10": aqi.get("pm10", "N/A"),
                    "nitrogen_dioxide": aqi.get("nitrogen_dioxide", "N/A"),
                    "ozone": aqi.get("ozone", "N/A"),
                }
            )

        # Ensure required keys have defaults.
        weather.setdefault("city", state["city"])
        weather.setdefault("temperature", "N/A")
        weather.setdefault("humidity", "N/A")
        weather.setdefault("precipitation", "N/A")
        weather.setdefault("wind_speed", "N/A")
        weather.setdefault("pressure", "N/A")
        weather.setdefault("cloud_cover", "N/A")
        weather.setdefault("aqi", "N/A")
        weather.setdefault("pm2_5", "N/A")
        weather.setdefault("pm10", "N/A")
        weather.setdefault("nitrogen_dioxide", "N/A")
        weather.setdefault("ozone", "N/A")

        forecast = state.get("forecast")
        risks = state.get("risk") or []
        context = state.get("rag") or ""
        satellite = state.get("satellite")

        state["bulletin"] = generate_bulletin(
            weather=weather,
            forecast=forecast,
            risks=risks,
            context=context,
            satellite=satellite,
        )

    except Exception as exc:
        logger.error("Bulletin node failed: %s", exc)
        state["bulletin"] = (
            f"Weather Intelligence Bulletin could not be generated: {exc}"
        )
    finally:
        print(
            f"✅ Bulletin Agent completed in {time.time() - start:.2f} sec"
        )
    return state