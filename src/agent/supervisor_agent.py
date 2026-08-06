import os

from dotenv import load_dotenv
from groq import Groq


load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


def decide_agents(user_query: str):

    prompt = f"""
You are the Supervisor Agent of a Weather Intelligence Platform.

Your job is to decide which specialist agents are required
to answer the user's question.

AVAILABLE AGENTS:

weather
- Current weather observations.
- Temperature, humidity, rainfall, wind, pressure, clouds.

aqi
- Current air quality.
- AQI, PM2.5, PM10, NO2, ozone.

forecast
- Future weather.
- Tomorrow, next 24-72 hours, next few days,
  weekend, upcoming rainfall, upcoming storms.

risk
- Weather and environmental risk assessment.
- Flood, heavy rain, heatwave, strong wind,
  air-quality risk.

rag
- Weather/climate knowledge.
- SOPs, preparedness, safety guidance,
  official documentation and general weather knowledge.

satellite
- Latest Sentinel-2 satellite observations.
- Cloud cover, satellite imagery,
  overcast conditions, satellite-based weather observations.

IMPORTANT ROUTING RULES:

1. Current weather only:
   weather

2. AQI or air quality only:
   aqi

3. Future weather / forecast:
   forecast

4. Future weather + possible danger/risk:
   forecast,risk

5. Current weather + safety/risk:
   weather,risk

6. General weather knowledge or preparedness:
   rag

7. Satellite imagery, cloud cover,
   Sentinel-2 imagery or satellite observations:
   satellite

8. If the question requires multiple types of information,
   select multiple agents.

9. Do NOT select agents that are unnecessary.

10. Return ONLY agent names separated by commas.

11. Use ONLY these names:
    weather
    aqi
    forecast
    risk
    rag
    satellite

EXAMPLES:

Question:
What is the AQI in Pune?

Answer:
aqi

Question:
What is the weather in Pune right now?

Answer:
weather

Question:
Will it rain tomorrow in Pune?

Answer:
forecast

Question:
What will the weather be for the next 3 days?

Answer:
forecast

Question:
Will it rain this weekend? Should I be worried?

Answer:
forecast,risk

Question:
Is Pune safe today?

Answer:
weather,risk

Question:
What is flood preparedness?

Answer:
rag

Question:
What is the current weather and AQI in Pune?

Answer:
weather,aqi

Question:
Is Pune likely to have heavy rain tomorrow?

Answer:
forecast,risk

Question:
Explain heatwave preparedness.

Answer:
rag

Question:
Show satellite observations over Pune.

Answer:
satellite

Question:
Analyze cloud cover using satellite data.

Answer:
satellite

Question:
Show latest Sentinel-2 image.

Answer:
satellite

Question:
Current weather and satellite observations.

Answer:
weather,satellite

USER QUESTION:

{user_query}
"""

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": "You are a precise routing supervisor. Return only valid agent names."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    decision = response.choices[0].message.content.strip().lower()

    # ---------------------------------------
    # Clean LLM response
    # ---------------------------------------

    valid_agents = {
        "weather",
        "aqi",
        "forecast",
        "risk",
        "rag",
        "satellite"
    }

    agents = []

    for agent in decision.split(","):

        agent = agent.strip()

        if agent in valid_agents and agent not in agents:
            agents.append(agent)

    return ",".join(agents)


if __name__ == "__main__":

    while True:

        query = input("\nAsk: ")

        print("\nSelected Agents:")

        print(decide_agents(query))