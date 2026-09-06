"""
Bulletin Generator — produces the final weather intelligence bulletin via Groq LLM.

The bulletin aggregates current weather, forecast analysis, air quality,
satellite observations, risk assessment, and RAG context into a
professional, factual situational report.
"""
import os
import logging

from dotenv import load_dotenv
from groq import Groq

load_dotenv()
logger = logging.getLogger(__name__)

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def _safe_satellite(satellite):
    """
    Return a satellite dict guaranteed to have all required keys.

    Accepts:
      - None          → full unavailable defaults
      - dict          → fills in any missing keys with "N/A" / unavailable text
      - string/other  → full unavailable defaults
    """
    defaults = {
        "image_date": "N/A",
        "cloud_cover": "N/A",
        "condition": "N/A",
        "rain_potential": "N/A",
        "visibility": "N/A",
        "confidence": "N/A",
        "summary": "No satellite analysis was performed.",
    }

    if not isinstance(satellite, dict):
        return defaults

    # If the satellite dict indicates unavailability, use the summary from it.
    if satellite.get("status") in ("unavailable", "error"):
        defaults["summary"] = satellite.get("message") or satellite.get("summary") or defaults["summary"]
        return defaults

    result = dict(defaults)
    result.update({k: satellite.get(k, defaults[k]) for k in defaults})
    return result


def _format_forecast(forecast):
    """
    Convert forecast data (dict or string) into a readable string for the prompt.
    """
    if not forecast:
        return "No forecast analysis was performed."

    if isinstance(forecast, str):
        return forecast

    if isinstance(forecast, dict):
        status = forecast.get("status", "")
        if status == "ERROR":
            return f"Forecast unavailable: {forecast.get('message', '')}"
        if status == "DATE_UNAVAILABLE":
            return forecast.get("analysis", "Requested forecast date is outside available range.")
        # Return the LLM analysis if present, otherwise a summary of the data.
        analysis = forecast.get("analysis")
        if analysis:
            return analysis
        # Fall back to raw forecast data
        days = forecast.get("forecast_analysis") or forecast.get("forecast") or []
        if days:
            lines = []
            for d in days:
                lines.append(
                    f"  {d.get('date', 'N/A')}: "
                    f"max {d.get('max_temp', 'N/A')}°C, "
                    f"min {d.get('min_temp', 'N/A')}°C, "
                    f"rain {d.get('rainfall', 'N/A')} mm "
                    f"({d.get('rainfall_class', 'N/A')})"
                )
            return "\n".join(lines)

    return "Forecast data format not recognized."


def generate_bulletin(weather: dict, forecast, risks: list, context: str, satellite=None) -> str:
    """
    Generate a professional weather intelligence bulletin using the Groq LLM.

    Args:
        weather:   Dict of current weather observations (must include ``city``,
                   ``temperature``, ``humidity``, etc.).
        forecast:  Forecast data (dict from forecast_agent, str, or None).
        risks:     List of risk strings from risk_agent.
        context:   RAG knowledge-base context string.
        satellite: Satellite analysis dict or None.

    Returns:
        The bulletin text as a string.
    """
    # ----------------------------------------------------------------
    # Prepare inputs
    # ----------------------------------------------------------------
    if not isinstance(weather, dict):
        weather = {}

    if not risks:
        risks = ["No significant weather or air-quality risks identified."]

    if not context:
        context = "No reference documents were used."

    sat = _safe_satellite(satellite)
    forecast_text = _format_forecast(forecast)

    # ----------------------------------------------------------------
    # Build prompt
    # ----------------------------------------------------------------
    prompt = f"""
You are a professional Weather Intelligence Decision Support Assistant.

Prepare a concise, professional weather intelligence bulletin.

Use ONLY the supplied observations, forecast, risk assessment, and reference context.

--------------------------------------------------
CURRENT WEATHER
--------------------------------------------------

City: {weather.get("city", "N/A")}

Temperature: {weather.get("temperature", "N/A")} °C
Humidity: {weather.get("humidity", "N/A")} %
Precipitation: {weather.get("precipitation", "N/A")} mm
Wind Speed: {weather.get("wind_speed", "N/A")} km/h
Pressure: {weather.get("pressure", "N/A")} hPa
Cloud Cover: {weather.get("cloud_cover", "N/A")} %

--------------------------------------------------
WEATHER FORECAST
--------------------------------------------------

{forecast_text}

--------------------------------------------------
AIR QUALITY
--------------------------------------------------

US AQI: {weather.get("aqi", "N/A")}
PM2.5: {weather.get("pm2_5", "N/A")} µg/m³
PM10: {weather.get("pm10", "N/A")} µg/m³
NO₂: {weather.get("nitrogen_dioxide", "N/A")} µg/m³
Ozone: {weather.get("ozone", "N/A")} µg/m³

--------------------------------------------------
SATELLITE OBSERVATION
--------------------------------------------------

Image Date: {sat["image_date"]}
Cloud Cover: {sat["cloud_cover"]} %
Condition: {sat["condition"]}
Rain Potential: {sat["rain_potential"]}
Visibility: {sat["visibility"]}
Confidence: {sat["confidence"]}

Summary:
{sat["summary"]}

--------------------------------------------------
RISK ASSESSMENT
--------------------------------------------------

{chr(10).join("- " + risk for risk in risks)}

--------------------------------------------------
REFERENCE CONTEXT
--------------------------------------------------

{context}

Return the bulletin using EXACTLY these sections:

# Weather Intelligence Situation Bulletin

## 1. Current Weather Situation
Summarize the current observed weather only.

## 2. Weather Forecast
Summarize the supplied forecast.
If no forecast exists, state: "No forecast analysis was performed."

## 3. Air Quality Situation
Summarize the supplied AQI observations.

## 4. Satellite Observation
Summarize the supplied satellite analysis.
If unavailable, state: "No satellite analysis was performed."

## 5. Risk Assessment
Summarize only the supplied risks. Do not invent new risks.

## 6. Recommended Action
Provide practical recommendations based ONLY on the supplied data.

## 7. Reference Basis
Mention whether recommendations were supported by the supplied reference context.

Important Rules:
- Never invent weather observations.
- Never invent forecast values.
- Never invent AQI values.
- Never invent warnings.
- Never claim IMD or any authority has issued alerts unless provided.
- Clearly distinguish observations from forecast.
- Use the supplied reference context only when relevant.
- Keep the bulletin concise and professional.
"""

    # ----------------------------------------------------------------
    # Call LLM
    # ----------------------------------------------------------------
    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.8-27b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a Weather Intelligence Decision Support Assistant. "
                        "Produce factual, concise operational weather bulletins."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
        )
        return response.choices[0].message.content

    except Exception as exc:
        logger.error("Bulletin LLM call failed: %s", exc)
        # Return a minimal text bulletin so the API still returns something useful.
        return (
            "# Weather Intelligence Situation Bulletin\n\n"
            f"**City:** {weather.get('city', 'N/A')}\n\n"
            f"**Temperature:** {weather.get('temperature', 'N/A')} °C\n"
            f"**Humidity:** {weather.get('humidity', 'N/A')} %\n"
            f"**Precipitation:** {weather.get('precipitation', 'N/A')} mm\n"
            f"**Wind Speed:** {weather.get('wind_speed', 'N/A')} km/h\n\n"
            f"**Risks:**\n" + "\n".join(f"- {r}" for r in risks) + "\n\n"
            f"*(LLM bulletin generation failed: {exc})*"
        )