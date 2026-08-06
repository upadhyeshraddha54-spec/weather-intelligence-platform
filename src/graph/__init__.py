
from typing import TypedDict


class WeatherState(TypedDict):
    city: str

    weather: dict

    aqi: dict

    risk: list

    rag: str

    bulletin: str