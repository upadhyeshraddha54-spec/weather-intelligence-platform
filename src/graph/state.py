from typing import TypedDict, List, Dict, Any

class WeatherState(TypedDict):

    city: str
    user_query: str

    selected_agents: List[str]

    weather: Dict[str, Any]
    aqi: Dict[str, Any]
    risk: List[str]
    rag: str
    forecast: Dict[str, Any]
    bulletin: str
    decision_logs: list