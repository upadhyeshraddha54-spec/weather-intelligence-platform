from src.weather.live_weather import get_live_weather
from src.agent.risk_agent import assess_risk


city = "Pune"

weather = get_live_weather(city)

if weather:

    print("\n🌦 LIVE WEATHER")
    print("-----------------------------")

    print("City:", weather["city"])
    print("Temperature:", weather["temperature"], "°C")
    print("Rainfall:", weather["precipitation"], "mm")
    print("Wind:", weather["wind_speed"], "km/h")

    risks = assess_risk(weather)

    print("\n🚨 RISK ASSESSMENT")
    print("-----------------------------")

    for risk in risks:
        print("•", risk)

else:
    print("City not found.")