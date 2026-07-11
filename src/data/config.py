from dataclasses import dataclass


@dataclass
class WeatherConfig:
    latitude: float = 18.5204
    longitude: float = 73.8567
    timezone: str = "auto"