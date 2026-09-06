import os

from dotenv import load_dotenv
from groq import Groq

from src.weather.live_weather import get_live_weather

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def run_aqi_agent(city):

    weather = get_live_weather(city)

    if weather is None:
        return {
            "city": city,
            "status": "ERROR",
            "message": "Could not retrieve live data."
        }

    aqi = weather.get("aqi")
    pm25 = weather.get("pm2_5")
    pm10 = weather.get("pm10")

    prompt = f"""
You are an Air Quality Specialist Agent.

Analyze the following LIVE air-quality observations.

City: {city}
US AQI: {aqi}
PM2.5: {pm25} µg/m³
PM10: {pm10} µg/m³

Determine:
1. AQI condition
2. Pollution concern
3. Whether increased monitoring is required
4. A short recommendation

Do not invent measurements.
Base your assessment only on the supplied observations.
"""

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",
        messages=[
            {
                "role": "system",
                "content": "You are an air-quality decision-support specialist."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1
    )

    return {
        "city": city,

        # Weather observations
        "temperature": weather["temperature"],
        "humidity": weather["humidity"],
        "precipitation": weather["precipitation"],
        "wind_speed": weather["wind_speed"],
        "pressure": weather["pressure"],
        "cloud_cover": weather["cloud_cover"],

        # AQI observations
        "aqi": aqi,
        "pm2_5": pm25,
        "pm10": pm10,
        "nitrogen_dioxide": weather["nitrogen_dioxide"],
        "ozone": weather["ozone"],

        # LLM analysis
        "analysis": response.choices[0].message.content
    }


if __name__ == "__main__":

    city = input("Enter city: ")

    result = run_aqi_agent(city)

    print("\n================================")
    print("🌫 AQI SPECIALIST AGENT")
    print("================================")

    print(result)