import requests


def get_forecast(city):

    # Get latitude & longitude
    geo = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": city,
            "count": 1
        }
    ).json()

    if "results" not in geo:
        return None

    lat = geo["results"][0]["latitude"]
    lon = geo["results"][0]["longitude"]

    weather = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": lat,
            "longitude": lon,
            "daily": [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_sum",
                "windspeed_10m_max"
            ],
            "forecast_days": 3,
            "timezone": "auto"
        }
    ).json()

    daily = weather["daily"]

    forecast = []

    for i in range(len(daily["time"])):

        forecast.append({

            "date": daily["time"][i],

            "max_temp":
                daily["temperature_2m_max"][i],

            "min_temp":
                daily["temperature_2m_min"][i],

            "rainfall":
                daily["precipitation_sum"][i],

            "wind":
                daily["windspeed_10m_max"][i]
        })

    return forecast