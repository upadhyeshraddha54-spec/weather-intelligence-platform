import os
import re
from datetime import datetime, timedelta

from dotenv import load_dotenv
from groq import Groq

from src.forecast.live_forecast import get_forecast
from src.forecast.forecast_risk import analyze_forecast

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# EXTRACT REQUESTED DATE
# ============================================================

def extract_requested_date(question):

    if not question:
        return None

    question_lower = question.lower()

    today = datetime.now().date()

    # --------------------------------------------------------
    # Today
    # --------------------------------------------------------

    if "today" in question_lower:
        return today.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # Day after tomorrow
    # IMPORTANT: check before tomorrow
    # --------------------------------------------------------

    if "day after tomorrow" in question_lower:
        target = today + timedelta(days=2)
        return target.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # Tomorrow
    # --------------------------------------------------------

    if "tomorrow" in question_lower:
        target = today + timedelta(days=1)
        return target.strftime("%Y-%m-%d")

    # --------------------------------------------------------
    # Dates:
    #
    # 8 aug
    # 8th aug
    # 8 august
    # 8th august
    # --------------------------------------------------------

    pattern = (
        r"\b(\d{1,2})(?:st|nd|rd|th)?\s*"
        r"(january|february|march|april|may|june|july|"
        r"august|september|october|november|december)\b"
    )

    match = re.search(pattern, question_lower)

    if match:

        day = int(match.group(1))
        month_name = match.group(2)

        month_number = datetime.strptime(
            month_name,
            "%B"
        ).month

        year = today.year

        try:

            target = datetime(
                year,
                month_number,
                day
            ).date()

            # If date has already passed,
            # use next year.

            if target < today:
                target = datetime(
                    year + 1,
                    month_number,
                    day
                ).date()

            return target.strftime("%Y-%m-%d")

        except ValueError:
            return None

    return None


# ============================================================
# FORECAST AGENT
# ============================================================

def run_forecast_agent(city, question=""):

    print("\n📅 Forecast Agent is required.")

    # --------------------------------------------------------
    # Get 8-day forecast
    # --------------------------------------------------------

    forecast = get_forecast(
        city,
        forecast_days=8
    )

    if not forecast:

        return {
            "city": city,
            "status": "ERROR",
            "message": "Forecast data unavailable.",
            "forecast": [],
            "forecast_analysis": [],
            "analysis": "Forecast data unavailable."
        }

    # --------------------------------------------------------
    # Find requested date
    # --------------------------------------------------------

    requested_date = extract_requested_date(question)

    print(f"📅 Requested date: {requested_date}")

    # --------------------------------------------------------
    # Analyze forecast
    # --------------------------------------------------------

    analysis_data = analyze_forecast(
        forecast
    )

    # --------------------------------------------------------
    # Default = complete forecast
    # --------------------------------------------------------

    selected_forecast = forecast
    selected_analysis = analysis_data

    # --------------------------------------------------------
    # Specific date requested
    # --------------------------------------------------------

    if requested_date:

        selected_forecast = [
            day
            for day in forecast
            if day["date"] == requested_date
        ]

        selected_analysis = [
            day
            for day in analysis_data
            if day["date"] == requested_date
        ]

        # ----------------------------------------------------
        # Date unavailable
        # ----------------------------------------------------

        if not selected_forecast:

            return {
                "city": city,
                "status": "DATE_UNAVAILABLE",
                "requested_date": requested_date,
                "available_from": forecast[0]["date"],
                "available_to": forecast[-1]["date"],
                "forecast": [],
                "forecast_analysis": [],
                "analysis": (
                    f"Forecast is available from "
                    f"{forecast[0]['date']} to "
                    f"{forecast[-1]['date']}. "
                    f"The requested date "
                    f"{requested_date} is outside "
                    f"the available forecast range."
                )
            }

    # --------------------------------------------------------
    # Display selected data
    # --------------------------------------------------------

    print("\n📊 Selected Forecast Data:")

    for day in selected_forecast:
        print(day)

    # --------------------------------------------------------
    # LLM explanation
    # --------------------------------------------------------

    prompt = f"""
You are a professional Weather Forecast Specialist.

The user asked:

{question}

Requested date:

{requested_date if requested_date else "No specific date requested"}

IMPORTANT:

If a requested date is provided, ONLY discuss that date.

Do NOT summarize other forecast days.

Do NOT calculate new weather values.

Do NOT invent information.

Verified forecast data:

{selected_analysis}

Return exactly:

1. Daily Summary
2. Weather Risks
3. Recommendations

Rules:

- Use only the supplied forecast data.
- Do not invent weather values.
- Do not change rainfall classifications.
- Do not change temperature classifications.
- Do not change wind classifications.
- Do not mention dates outside the supplied selected data.
- If rainfall is 0, say that no rainfall is forecast.
- If rainfall is greater than 0, clearly state the forecast rainfall.
- Keep the response concise.
"""

    # --------------------------------------------------------
    # Groq
    # --------------------------------------------------------

    response = client.chat.completions.create(
        model="qwen/qwen3.8-27b",

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a professional "
                    "meteorological forecast specialist."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0.1
    )

    # --------------------------------------------------------
    # Return
    # --------------------------------------------------------

    return {
        "city": city,
        "status": "SUCCESS",

        "requested_date": requested_date,

        "forecast": selected_forecast,

        "forecast_analysis": selected_analysis,

        "analysis": response.choices[0].message.content
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    city = input("Enter city: ")

    question = input(
        "Ask your forecast question: "
    )

    result = run_forecast_agent(
        city,
        question
    )

    print("\n==============================")
    print("📅 FORECAST AGENT")
    print("==============================\n")

    print(result.get("analysis"))

    print("\n==============================")
    print("📊 SELECTED FORECAST")
    print("==============================")

    for day in result.get("forecast", []):
        print(day)