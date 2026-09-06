"""
Forecast risk classification helpers.

Classifies forecast fields (rainfall, temperature, wind, rain probability)
into human-readable risk categories and produces a per-day analysis list.
"""


def classify_rainfall(rainfall):
    """Classify daily rainfall total (mm) into a risk category."""
    if rainfall is None:
        return "Unknown"
    if rainfall == 0:
        return "No Rain"
    elif rainfall < 5:
        return "Light Rain"
    elif rainfall < 20:
        return "Moderate Rain"
    elif rainfall < 50:
        return "Heavy Rain"
    elif rainfall < 100:
        return "Very Heavy Rain"
    return "Extreme Rain"


def classify_temperature(temp):
    """Flag heatwave risk when max temperature reaches 40 °C."""
    if temp is None:
        return "Unknown"
    if temp >= 40:
        return "Heatwave Risk"
    return "Normal"


def classify_wind(wind):
    """Flag strong-wind risk when max wind speed reaches 60 km/h."""
    if wind is None:
        return "Unknown"
    if wind >= 60:
        return "Strong Wind Risk"
    return "Normal"


def classify_rain_probability(probability):
    """Classify rainfall probability (%) into a qualitative band."""
    if probability is None:
        return "Unknown"
    if probability < 20:
        return "Low"
    elif probability < 50:
        return "Moderate"
    elif probability < 80:
        return "High"
    return "Very High"


def analyze_forecast(forecast):
    """
    Produce a per-day risk analysis list from the raw forecast list.

    Each day dict from `live_forecast.get_forecast` uses the key
    ``rain_chance`` (not ``rain_probability``); this function reads the
    correct key and maps it to the ``rain_probability`` output key so
    downstream consumers receive a consistent contract.
    """
    results = []

    for day in forecast:
        # ``live_forecast.py`` outputs ``rain_chance``; read that key.
        rain_chance = day.get("rain_chance")

        results.append(
            {
                "date": day.get("date"),
                "max_temp": day.get("max_temp"),
                "min_temp": day.get("min_temp"),
                "rainfall": day.get("rainfall"),
                # Expose as rain_probability for downstream consumers.
                "rain_probability": rain_chance,
                "wind": day.get("wind"),
                "weather_code": day.get("weather_code"),
                "uv_index": day.get("uv_index"),
                "rainfall_class": classify_rainfall(day.get("rainfall")),
                "rain_probability_class": classify_rain_probability(
                    rain_chance
                ),
                "temperature_class": classify_temperature(
                    day.get("max_temp")
                ),
                "wind_class": classify_wind(day.get("wind")),
            }
        )

    return results