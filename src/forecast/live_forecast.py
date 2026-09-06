"""
Live forecast fetcher — retrieves daily weather forecast from Open-Meteo.

Data source: https://open-meteo.com  (no API key required)

The returned list uses the key ``rain_chance`` (not ``rain_probability``)
to match the field name available from the Open-Meteo ``precipitation_probability_max``
field, and to be consistent with how forecast_risk.py reads it.
"""
import logging
import requests

logger = logging.getLogger(__name__)

TIMEOUT = 10  # seconds


def get_forecast(city: str, forecast_days: int = 8):
    """
    Retrieve a daily weather forecast for the given city.

    Args:
        city:          City name (geocoded via Open-Meteo).
        forecast_days: Number of days to forecast (1–16).

    Returns:
        A list of daily forecast dicts, or None if data is unavailable.

        Each dict has the following keys:
          ``date``        — ISO date string (YYYY-MM-DD)
          ``max_temp``    — maximum temperature (°C)
          ``min_temp``    — minimum temperature (°C)
          ``rainfall``    — daily precipitation sum (mm)
          ``rain_chance`` — max precipitation probability (%)
          ``wind``        — maximum wind speed (km/h)
          ``weather_code``— WMO weather code
          ``uv_index``    — maximum UV index
    """
    # ------------------------------------------------------------------
    # Geocoding
    # ------------------------------------------------------------------
    try:
        geo_response = requests.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={
                "name": city,
                "count": 1,
                "language": "en",
                "format": "json",
            },
            timeout=TIMEOUT,
        )
        geo_response.raise_for_status()
        geo = geo_response.json()
    except requests.RequestException as exc:
        logger.warning("Forecast geocoding failed for '%s': %s", city, exc)
        return None

    if "results" not in geo or not geo["results"]:
        logger.info("Forecast: city not found: %s", city)
        return None

    location = geo["results"][0]
    lat = location["latitude"]
    lon = location["longitude"]
    location_name = location.get("name", city)

    # ------------------------------------------------------------------
    # Forecast API
    # ------------------------------------------------------------------
    try:
        weather_response = requests.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": ",".join(
                    [
                        "temperature_2m_max",
                        "temperature_2m_min",
                        "precipitation_sum",
                        "precipitation_probability_max",
                        "wind_speed_10m_max",
                        "weather_code",
                        "uv_index_max",
                    ]
                ),
                "forecast_days": forecast_days,
                "timezone": "auto",
            },
            timeout=TIMEOUT,
        )
        weather_response.raise_for_status()
        weather = weather_response.json()
    except requests.RequestException as exc:
        logger.warning("Forecast API failed for '%s': %s", city, exc)
        return None

    if "daily" not in weather:
        logger.warning("Forecast: no daily data in response for %s", city)
        return None

    daily = weather["daily"]

    dates = daily.get("time", [])
    max_temps = daily.get("temperature_2m_max", [])
    min_temps = daily.get("temperature_2m_min", [])
    rainfall = daily.get("precipitation_sum", [])
    rain_chance = daily.get("precipitation_probability_max", [])
    wind = daily.get("wind_speed_10m_max", [])
    weather_codes = daily.get("weather_code", [])
    uv_index = daily.get("uv_index_max", [])

    forecast = []
    for i, date in enumerate(dates):
        forecast.append(
            {
                "date": date,
                "max_temp": max_temps[i] if i < len(max_temps) else None,
                "min_temp": min_temps[i] if i < len(min_temps) else None,
                "rainfall": rainfall[i] if i < len(rainfall) else None,
                "rain_chance": rain_chance[i] if i < len(rain_chance) else None,
                "wind": wind[i] if i < len(wind) else None,
                "weather_code": weather_codes[i] if i < len(weather_codes) else None,
                "uv_index": uv_index[i] if i < len(uv_index) else None,
            }
        )

    logger.info(
        "Forecast retrieved for %s: %d days", location_name, len(forecast)
    )
    print(f"Forecast retrieved for {location_name}: {len(forecast)} days")
    return forecast