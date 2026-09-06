from typing import TypedDict, List, Dict, Any
class WeatherState(TypedDict):
    city: str
    user_query: str

    selected_agents: list

    weather: dict
    aqi: dict
    forecast: str
    satellite: dict    
    risk: list
    rag: str
    bulletin: str

    decision_logs: list