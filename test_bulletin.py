from src.weather.live_weather import get_live_weather
from src.agent.risk_agent import assess_risk
from src.agent.bulletin_generator import generate_bulletin

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS


# --------------------------------
# 1. Get live weather + AQI
# --------------------------------

city = "Pune"

weather = get_live_weather(city)

if weather is None:
    print("City not found.")
    exit()


# --------------------------------
# 2. Risk assessment
# --------------------------------

risks = assess_risk(weather)


# --------------------------------
# 3. Load RAG database
# --------------------------------

embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

vectorstore = FAISS.load_local(
    "weather_vector_db",
    embeddings,
    allow_dangerous_deserialization=True
)


# --------------------------------
# 4. Retrieve relevant knowledge
# --------------------------------

question = f"""
Weather and air quality situation for {weather["city"]}.

Temperature:
{weather["temperature"]} °C

Rainfall:
{weather["precipitation"]} mm

Wind:
{weather["wind_speed"]} km/h

AQI:
{weather["aqi"]}

PM2.5:
{weather["pm2_5"]}

PM10:
{weather["pm10"]}

Find relevant information about weather hazards,
air pollution, climate hazards, health risks,
and recommended precautions.
"""

docs = vectorstore.similarity_search(
    question,
    k=3
)

context = "\n\n".join(
    doc.page_content
    for doc in docs
)


# --------------------------------
# 5. Generate bulletin
# --------------------------------

bulletin = generate_bulletin(
    weather,
    risks,
    context
)


# --------------------------------
# 6. Display result
# --------------------------------

print("\n================================")
print("🌦 WEATHER INTELLIGENCE BULLETIN")
print("================================")

print("\nLIVE OBSERVATIONS")
print("--------------------------------")

print("City:", weather["city"])
print("Temperature:", weather["temperature"], "°C")
print("Humidity:", weather["humidity"], "%")
print("Rainfall:", weather["precipitation"], "mm")
print("Wind:", weather["wind_speed"], "km/h")

print("\nAIR QUALITY")
print("--------------------------------")

print("US AQI:", weather["aqi"])
print("PM2.5:", weather["pm2_5"], "µg/m³")
print("PM10:", weather["pm10"], "µg/m³")

print("\nRISK ASSESSMENT")
print("--------------------------------")

for risk in risks:
    print("•", risk)

print("\n================================")
print("AI WEATHER & AIR QUALITY BULLETIN")
print("================================")

print(bulletin)