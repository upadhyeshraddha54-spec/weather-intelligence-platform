from langchain_core.tools import tool

from src.weather.live_weather import get_live_weather
from src.agent.risk_agent import assess_risk


@tool
def weather_tool(city: str) -> str:
    """
    Get current weather and air-quality observations for a city.
    """

    weather = get_live_weather(city)

    if weather is None:
        return f"Could not find weather data for {city}."

    return f"""
City: {weather['city']}

Temperature: {weather['temperature']} °C
Humidity: {weather['humidity']} %
Precipitation: {weather['precipitation']} mm
Wind Speed: {weather['wind_speed']} km/h
Pressure: {weather['pressure']} hPa
Cloud Cover: {weather['cloud_cover']} %

US AQI: {weather['aqi']}
PM2.5: {weather['pm2_5']} µg/m³
PM10: {weather['pm10']} µg/m³
NO2: {weather['nitrogen_dioxide']} µg/m³
Ozone: {weather['ozone']} µg/m³
"""


@tool
def risk_tool(city: str) -> str:
    """
    Assess current weather and air-quality risks for a city.
    """

    weather = get_live_weather(city)

    if weather is None:
        return f"Could not assess risk because {city} was not found."

    risks = assess_risk(weather)

    return "\n".join(
        f"- {risk}"
        for risk in risks
    )