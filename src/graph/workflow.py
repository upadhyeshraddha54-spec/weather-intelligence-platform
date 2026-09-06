
import time
from langgraph.graph import StateGraph, END

from src.graph.state import WeatherState
from src.graph.nodes import (
    supervisor_node,
    dispatcher_node,
    weather_node,
    aqi_node,
    forecast_node,
    satellite_node,
    risk_node,
    rag_node,
    bulletin_node,
)

# ============================================================
# ROUTING FUNCTIONS
# ============================================================

def after_dispatcher(state):

    agents = state.get("selected_agents", [])

    # --------------------------------------------------------
    # First priority: current weather
    # --------------------------------------------------------

    if "weather" in agents:
        return "weather"

    # --------------------------------------------------------
    # AQI
    # --------------------------------------------------------

    if "aqi" in agents:
        return "aqi"

    # --------------------------------------------------------
    # Forecast
    # --------------------------------------------------------

    if "forecast" in agents:
        return "forecast"
    
    if "satellite" in agents:
     return "satellite"
    # --------------------------------------------------------
    # Risk
    # --------------------------------------------------------

    if "risk" in agents:
        return "risk"

    # --------------------------------------------------------
    # RAG
    # --------------------------------------------------------

    if "rag" in agents:
        return "rag"

    # --------------------------------------------------------
    # Nothing selected
    # --------------------------------------------------------

    return "bulletin"


def after_weather(state):

    agents = state.get("selected_agents", [])

    if "aqi" in agents:
        return "aqi"

    if "forecast" in agents:
        return "forecast"

    if "satellite" in agents:
     return "satellite"

    if "risk" in agents:
        return "risk"

    if "rag" in agents:
        return "rag"

    return "bulletin"


def after_aqi(state):

    agents = state.get("selected_agents", [])

    if "forecast" in agents:
        return "forecast"

    if "satellite" in agents:
        return "satellite"

    if "risk" in agents:
        return "risk"

    if "rag" in agents:
        return "rag"

    return "bulletin"


def after_forecast(state):

    agents = state.get("selected_agents", [])

    if "risk" in agents:
        return "risk"

    if "satellite" in agents:
        return "satellite"

    if "rag" in agents:
        return "rag"

    return "bulletin"

def after_satellite(state):

    agents = state.get("selected_agents", [])

    if "risk" in agents:
        return "risk"

    

    if "rag" in agents:
        return "rag"

    return "bulletin"


def after_risk(state):

    agents = state.get("selected_agents", [])

    if "rag" in agents:
        return "rag"

    return "bulletin"


# ============================================================
# CREATE GRAPH
# ============================================================

graph = StateGraph(WeatherState)


# ============================================================
# ADD NODES
# ============================================================

graph.add_node("supervisor", supervisor_node)
graph.add_node("dispatcher", dispatcher_node)

graph.add_node("weather", weather_node)
graph.add_node("aqi", aqi_node)
graph.add_node("forecast", forecast_node)
graph.add_node("satellite", satellite_node)
graph.add_node("risk", risk_node)
graph.add_node("rag", rag_node)

graph.add_node("bulletin", bulletin_node)


# ============================================================
# ENTRY POINT
# ============================================================

graph.set_entry_point("supervisor")


# ============================================================
# SUPERVISOR → DISPATCHER
# ============================================================

graph.add_edge(
    "supervisor",
    "dispatcher"
)


# ============================================================
# DISPATCHER → FIRST AGENT
# ============================================================
graph.add_conditional_edges(
    "dispatcher",
    after_dispatcher,
    {
        "weather": "weather",
        "aqi": "aqi",
        "forecast": "forecast",
        "satellite": "satellite",
        "risk": "risk",
        "rag": "rag",
        "bulletin": "bulletin",
    }
)


# ============================================================
# WEATHER ROUTING
# ============================================================

graph.add_conditional_edges(
    "weather",
    after_weather,
    
    {
    "aqi": "aqi",
    "forecast": "forecast",
    "satellite": "satellite",
    "risk": "risk",
    "rag": "rag",
    "bulletin": "bulletin",

    }
)


# ============================================================
# AQI ROUTING
# ============================================================

graph.add_conditional_edges(
    "aqi",
    after_aqi,
  {
    "forecast": "forecast",
    "satellite": "satellite",
    "risk": "risk",
    "rag": "rag",
    "bulletin": "bulletin",
}
)


# ============================================================
# FORECAST ROUTING
# ============================================================

graph.add_conditional_edges(
    "forecast",
    after_forecast,
    {
        "risk": "risk",
        "rag": "rag",
        "bulletin": "bulletin",
    }
)

# ============================================================
# SATELLITE ROUTING
# ============================================================

graph.add_conditional_edges(
    "satellite",
    after_satellite,
    {
        "risk": "risk",
        "rag": "rag",
        "bulletin": "bulletin",
    }
)
# ============================================================
# RISK ROUTING
# ============================================================

graph.add_conditional_edges(
    "risk",
    after_risk,
    {
        "rag": "rag",
        "bulletin": "bulletin",
    }
)


# ============================================================
# RAG → BULLETIN
# ============================================================

graph.add_edge(
    "rag",
    "bulletin"
)


# ============================================================
# BULLETIN → END
# ============================================================

graph.add_edge(
    "bulletin",
    END
)


# ============================================================
# COMPILE
# ============================================================

weather_graph = graph.compile()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":

    print("\n===================================")
    print("🌦 WEATHER INTELLIGENCE PLATFORM")
    print("===================================")

    city = input("\nEnter City: ")
    question = input("Ask your question: ")

    # --------------------------------------------------------
    # Initial State
    # --------------------------------------------------------

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

        "decision_logs": []
    }

    # --------------------------------------------------------
    # Execute LangGraph
    # --------------------------------------------------------

    start = time.time()

    result = weather_graph.invoke(state)

    print("\n===================================")
    print(f"⏱ Total Workflow Time: {time.time() - start:.2f} sec")
    print("===================================")

    # --------------------------------------------------------
    # Selected Agents
    # --------------------------------------------------------

    print("\n===================================")
    print("🧠 SELECTED AGENTS")
    print("===================================")

    for agent in result.get("selected_agents", []):
        print(f"✓ {agent}")

    # --------------------------------------------------------
    # Final Bulletin
    # --------------------------------------------------------

    print("\n===================================")
    print("📋 FINAL BULLETIN")
    print("===================================\n")

    print(result.get("bulletin", "No bulletin generated."))

    # --------------------------------------------------------
    # Decision Logs
    # --------------------------------------------------------

    print("\n===================================")
    print("🧾 DECISION LOG")
    print("===================================")

    for log in result.get("decision_logs", []):
        print(log)