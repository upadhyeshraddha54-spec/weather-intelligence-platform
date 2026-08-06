import os

from dotenv import load_dotenv
from groq import Groq

from src.forecast.live_forecast import get_forecast
from src.forecast.forecast_risk import analyze_forecast


# --------------------------------------------------
# Load Environment
# --------------------------------------------------

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# --------------------------------------------------
# Forecast Agent
# --------------------------------------------------

def run_forecast_agent(city):

    # Get 3-day forecast
    forecast = get_forecast(city)

    if forecast is None:

        return {
            "city": city,
            "status": "ERROR",
            "message": "Forecast data unavailable."
        }

    # Rule-based forecast analysis
    analysis_data = analyze_forecast(forecast)

    # Prompt for LLM
    prompt = f"""
You are a Weather Forecast Specialist.

Below is a 3-day weather forecast that has already been analyzed
using rule-based weather classification.

Forecast Data:

{analysis_data}

Your task is NOT to recalculate the classifications.

Instead, explain the forecast in a clear and professional manner.

Return exactly these sections:

1. Daily Summary
2. Weather Risks
3. Recommendations

Important Rules:

- Do not invent weather values.
- Do not change any classifications.
- Do not exaggerate risks.
- Base every statement ONLY on the supplied forecast.
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional meteorological "
                    "forecast specialist."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2
    )

    return {
        "city": city,
        "forecast": forecast,
        "forecast_analysis": analysis_data,
        "analysis": response.choices[0].message.content
    }


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    city = input("Enter city: ")

    result = run_forecast_agent(city)

    print("\n==============================")
    print("📅 FORECAST AGENT")
    print("==============================\n")

    print(result["analysis"])