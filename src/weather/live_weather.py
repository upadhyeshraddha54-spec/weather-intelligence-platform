"""
Live weather fetcher — retrieves current weather and air quality data
from the free Open-Meteo API (no API key required).

Data source: https://open-meteo.com
"""
import logging
import requests

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Open-Meteo API timeouts
# ---------------------------------------------------------------------------
TIMEOUT = 10  # seconds


# ===========================================================================
# GEOCODING
# ===========================================================================

def get_coordinates(city: str):
    """
    Convert a city name into geographic coordinates via Open-Meteo geocoding.

    Returns:
        dict with keys ``latitude``, ``longitude``, ``name`` on success.
        None if the city is not found or the API is unreachable.
    """
    try:
        response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        data = response.json()
    except requests.RequestException as exc:
        logger.warning("Geocoding API unavailable for '%s': %s", city, exc)
        return None

    if "results" not in data or not data["results"]:
        logger.info("City not found: %s", city)
        return None

    location = data["results"][0]
    return {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "name": location["name"],
    }


# ===========================================================================
# CURRENT WEATHER
# ===========================================================================

def get_weather(latitude: float, longitude: float):
    """
    Fetch current weather + hourly dashboard data from Open-Meteo.

    Returns:
        Parsed JSON response dict on success, None on API failure.
    """
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "wind_speed_10m",
                    "surface_pressure",
                    "cloud_cover",
                    "weather_code",
                ],
                "hourly": [
                    "visibility",
                    "uv_index",
                    "precipitation_probability",
                ],
                "daily": [
                    "sunrise",
                    "sunset",
                    "uv_index_max",
                    "precipitation_probability_max",
                ],
                "forecast_days": 1,
                "timezone": "auto",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as exc:
        logger.warning("Weather API unavailable (%s, %s): %s", latitude, longitude, exc)
        return None


# ===========================================================================
# AIR QUALITY
# ===========================================================================

def get_air_quality(latitude: float, longitude: float):
    """
    Fetch current air-quality data from Open-Meteo Air Quality API.

    Returns:
        The ``current`` sub-dict on success, None on failure.
    """
    try:
        response = requests.get(
            "https://air-quality-api.open-meteo.com/v1/air-quality",
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": [
                    "us_aqi",
                    "pm2_5",
                    "pm10",
                    "nitrogen_dioxide",
                    "ozone",
                ],
                "timezone": "auto",
            },
            timeout=TIMEOUT,
        )
        response.raise_for_status()
        return response.json().get("current", {})
    except requests.RequestException as exc:
        logger.warning("Air quality API unavailable (%s, %s): %s", latitude, longitude, exc)
        return {}


# ===========================================================================
# MAIN PUBLIC FUNCTION
# ===========================================================================

def get_live_weather(city: str):
    """
    Fetch live weather + AQI for the given city name.

    Returns:
        A dict with all weather and AQI fields on success.
        None if the city cannot be geocoded or the weather API is down.
    """
    location = get_coordinates(city)
    if location is None:
        return None

    lat = location["latitude"]
    lon = location["longitude"]

    data = get_weather(lat, lon)
    if data is None:
        return None

    weather = data.get("current", {})
    hourly = data.get("hourly", {})
    daily = data.get("daily", {})

    # ------------------------------------------------------------------
    # Find the current hourly index
    # ------------------------------------------------------------------
    current_time = weather.get("time")
    hourly_times = hourly.get("time", [])
    current_index = 0
    if current_time and current_time in hourly_times:
        current_index = hourly_times.index(current_time)

    # ------------------------------------------------------------------
    # Hourly values at current index
    # ------------------------------------------------------------------
    def _safe_index(lst, idx):
        return lst[idx] if lst and idx < len(lst) else None

    visibility = _safe_index(hourly.get("visibility", []), current_index)
    uv_index = _safe_index(hourly.get("uv_index", []), current_index)
    rain_probability = _safe_index(
        hourly.get("precipitation_probability", []), current_index
    )

    # ------------------------------------------------------------------
    # Daily values
    # ------------------------------------------------------------------
    sunrise = (daily.get("sunrise") or [None])[0]
    sunset = (daily.get("sunset") or [None])[0]
    daily_uv = (daily.get("uv_index_max") or [None])[0]
    daily_rain_probability = (
        daily.get("precipitation_probability_max") or [None]
    )[0]

    # ------------------------------------------------------------------
    # Air quality
    # ------------------------------------------------------------------
    air_quality = get_air_quality(lat, lon)

    # ------------------------------------------------------------------
    # Build result dict
    # ------------------------------------------------------------------
    return {
        "city": location["name"],
        "latitude": lat,
        "longitude": lon,

        # Current weather
        "temperature": weather.get("temperature_2m"),
        "feels_like": weather.get("apparent_temperature"),
        "humidity": weather.get("relative_humidity_2m"),
        "precipitation": weather.get("precipitation"),
        "wind_speed": weather.get("wind_speed_10m"),
        "pressure": weather.get("surface_pressure"),
        "cloud_cover": weather.get("cloud_cover"),
        "weather_code": weather.get("weather_code"),

        # Dashboard extras
        "visibility": visibility,
        "uv_index": uv_index if uv_index is not None else daily_uv,
        "rain_probability": (
            rain_probability if rain_probability is not None
            else daily_rain_probability
        ),
        "sunrise": sunrise,
        "sunset": sunset,

        # Air quality
        "aqi": air_quality.get("us_aqi"),
        "pm2_5": air_quality.get("pm2_5"),
        "pm10": air_quality.get("pm10"),
        "nitrogen_dioxide": air_quality.get("nitrogen_dioxide"),
        "ozone": air_quality.get("ozone"),
    }


# ===========================================================================
# STANDALONE TEST
# ===========================================================================

if __name__ == "__main__":
    city = input("Enter city: ")
    result = get_live_weather(city)
    print("\n==============================")
    print("🌦 LIVE WEATHER")
    print("==============================\n")
    print(result)