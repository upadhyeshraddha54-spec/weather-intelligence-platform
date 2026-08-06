import requests


def get_coordinates(city):
    """Convert city name into latitude and longitude."""

    url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    if "results" not in data or not data["results"]:
        return None

    location = data["results"][0]

    return {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "name": location["name"]
    }


def get_weather(latitude, longitude):
    """Fetch current weather data."""

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "precipitation",
            "wind_speed_10m",
            "surface_pressure",
            "cloud_cover"
        ],
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()["current"]


def get_air_quality(latitude, longitude):
    """Fetch current air-quality data."""

    url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": [
            "us_aqi",
            "pm2_5",
            "pm10",
            "nitrogen_dioxide",
            "ozone"
        ],
        "timezone": "auto"
    }

    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()

    return response.json()["current"]


def get_live_weather(city):
    """Get current weather + air quality for a city."""

    location = get_coordinates(city)

    if location is None:
        return None

    weather = get_weather(
        location["latitude"],
        location["longitude"]
    )

    air_quality = get_air_quality(
        location["latitude"],
        location["longitude"]
    )

    return {
        "city": location["name"],
        "latitude": location["latitude"],
        "longitude": location["longitude"],

        # Weather
        "temperature": weather["temperature_2m"],
        "humidity": weather["relative_humidity_2m"],
        "precipitation": weather["precipitation"],
        "wind_speed": weather["wind_speed_10m"],
        "pressure": weather["surface_pressure"],
        "cloud_cover": weather["cloud_cover"],

        # Air quality
        "aqi": air_quality["us_aqi"],
        "pm2_5": air_quality["pm2_5"],
        "pm10": air_quality["pm10"],
        "nitrogen_dioxide": air_quality["nitrogen_dioxide"],
        "ozone": air_quality["ozone"]
    }