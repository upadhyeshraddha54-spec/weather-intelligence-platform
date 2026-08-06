from src.weather.live_weather import get_live_weather
from src.agent.aqi_agent import run_aqi_agent
from src.agent.risk_agent import assess_risk
from src.agent.rag_tool import search_weather_knowledge
from src.agent.bulletin_generator import generate_bulletin
from src.agent.supervisor_agent import decide_agents
from src.graph.dispatcher import dispatch
from src.agent.forecast_agent import run_forecast_agent
from src.satellite.satellite_agent import run_satellite_agent


# ---------------------------------------
# Supervisor Node
# ---------------------------------------

def supervisor_node(state):

    decision = decide_agents(state["user_query"])

    agents = [
        agent.strip()
        for agent in decision.split(",")
        if agent.strip()
    ]

    state["selected_agents"] = agents

    print("\n🧠 Supervisor selected:")
    print(agents)

    return state


# ---------------------------------------
# Dispatcher Node
# ---------------------------------------

def dispatcher_node(state):

    return dispatch(state)


# ---------------------------------------
# Weather Node
# ---------------------------------------

def weather_node(state):

    print("\n🌦 Running Weather Agent...")

    state["weather"] = get_live_weather(state["city"])

    return state


# ---------------------------------------
# AQI Node
# ---------------------------------------

def aqi_node(state):

    print("\n🌫 Running AQI Agent...")

    state["aqi"] = run_aqi_agent(state["city"])

    return state


# ---------------------------------------
# Forecast Node
# ---------------------------------------

def forecast_node(state):

    print("\n📅 Running Forecast Agent...")

    state["forecast"] = run_forecast_agent(state["city"])

    return state


# ---------------------------------------
# Satellite Node
# ---------------------------------------

def satellite_node(state):

    print("\n🛰 Running Satellite Agent...")

    state["satellite"] = run_satellite_agent()

    return state

# ---------------------------------------
# Risk Node
# ---------------------------------------

def risk_node(state):

    print("\n🚨 Running Risk Agent...")

    weather = state.get("weather")

    if weather is None:
        weather = get_live_weather(state["city"])

    if weather is None:
        state["risk"] = ["Weather data unavailable."]
        return state

    risks = assess_risk(weather)

    state["risk"] = risks

    return state


# ---------------------------------------
# RAG Node
# ---------------------------------------

def rag_node(state):

    print("\n📚 Running RAG Agent...")

    state["rag"] = search_weather_knowledge.invoke(
        {"query": state["user_query"]}
    )

    return state


# ---------------------------------------
# Bulletin Node
# ---------------------------------------

def bulletin_node(state):

    print("\n📝 Running Bulletin Agent...")

    # Weather observations
    weather = state.get("weather")

    # If Weather Agent didn't run, use weather returned by AQI Agent
    if weather is None:
        weather = state.get("aqi", {}).copy()

    if weather is None:
        weather = {}

    # AQI
    aqi = state.get("aqi") or {}

    # Forecast
    forecast = state.get("forecast")

    # Risks
    risks = state.get("risk") or []

    # RAG
    context = state.get("rag") or ""
    satellite = state.get("satellite")
    # Merge AQI values
    if isinstance(aqi, dict):

        weather.update({
            "aqi": aqi.get("aqi", "N/A"),
            "pm2_5": aqi.get("pm2_5", "N/A"),
            "pm10": aqi.get("pm10", "N/A"),
            "nitrogen_dioxide": aqi.get("nitrogen_dioxide", "N/A"),
            "ozone": aqi.get("ozone", "N/A"),
        })

    # Default values
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

    state["bulletin"] = generate_bulletin(
        weather=weather,
        forecast=forecast,
        risks=risks,
        context=context,
        satellite=satellite

    )

    return state