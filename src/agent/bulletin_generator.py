import os

from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def generate_bulletin(weather, forecast, risks, context, satellite=None):

    if not forecast:
        forecast = "No forecast analysis was performed."

    if not context:
        context = "No reference documents were used."

    if satellite is None:
     satellite = {
        "image_date": "N/A",
        "cloud_cover": "N/A",
        "condition": "N/A",
        "summary": "No satellite analysis was performed."
    }
    if not risks:
        risks = ["No significant weather or air-quality risks identified."]

    prompt = f"""
You are a professional Weather Intelligence Decision Support Assistant.

Prepare a concise, professional weather intelligence bulletin.

Use ONLY the supplied observations, forecast, risk assessment,
and reference context.

--------------------------------------------------
CURRENT WEATHER
--------------------------------------------------

City: {weather["city"]}

Temperature: {weather["temperature"]} °C
Humidity: {weather["humidity"]} %
Precipitation: {weather["precipitation"]} mm
Wind Speed: {weather["wind_speed"]} km/h
Pressure: {weather["pressure"]} hPa
Cloud Cover: {weather["cloud_cover"]} %

--------------------------------------------------
WEATHER FORECAST
--------------------------------------------------

{forecast}

--------------------------------------------------
AIR QUALITY
--------------------------------------------------

US AQI: {weather["aqi"]}
PM2.5: {weather["pm2_5"]} µg/m³
PM10: {weather["pm10"]} µg/m³
NO₂: {weather["nitrogen_dioxide"]} µg/m³
Ozone: {weather["ozone"]} µg/m³


--------------------------------------------------
SATELLITE OBSERVATION
--------------------------------------------------

Image Date: {satellite["image_date"]}
Cloud Cover: {satellite["cloud_cover"]} %
Condition: {satellite["condition"]}

Summary:
{satellite["summary"]}

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
If no forecast exists, state:
"No forecast analysis was performed."

## 3. Air Quality Situation
Summarize the supplied AQI observations.

## 4. Satellite Observation
Summarize the supplied satellite analysis.
If unavailable, state:
"No satellite analysis was performed."

## 5. Risk Assessment
Summarize only the supplied risks.
Do not invent new risks.

## 6. Recommended Action
Provide practical recommendations based ONLY on:
- Current weather
- Forecast
- Air quality
- Satellite observations
- Risk assessment

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

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a Weather Intelligence Decision Support Assistant. "
                    "Produce factual, concise operational weather bulletins."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
    )

    return response.choices[0].message.content