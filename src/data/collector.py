import requests

from .config import WeatherConfig


class WeatherCollector:
    """
    Collects current weather data from the Open-Meteo API.
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self, config: WeatherConfig):
        """
        Initialize the weather collector with configuration.
        """
        self.config = config

    def fetch_current_weather(self) -> dict:
        """
        Fetch current weather from Open-Meteo.

        Returns:
            dict: API response as a Python dictionary.

        Raises:
            requests.exceptions.RequestException:
                If the request fails.
        """

        params = {
            "latitude": self.config.latitude,
            "longitude": self.config.longitude,
            "current": (
                "temperature_2m,"
                "relative_humidity_2m,"
                "wind_speed_10m"
            ),
            "timezone": self.config.timezone,
        }

        response = requests.get(
            self.BASE_URL,
            params=params,
            timeout=10,
        )

        # Raise an exception if the request was not successful
        response.raise_for_status()

        # Convert JSON response into a Python dictionary
        return response.json()