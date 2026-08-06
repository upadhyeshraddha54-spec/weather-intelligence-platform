from src.weather.live_weather import get_live_weather

weather = get_live_weather("Pune")

if weather:
    print("\n🌦 Live Weather")
    print("-----------------------------")
    print("City:", weather["city"])
    print("Temperature:", weather["temperature"], "°C")
    print("Humidity:", weather["humidity"], "%")
    print("Precipitation:", weather["precipitation"], "mm")
    print("Wind Speed:", weather["wind_speed"], "km/h")
    print("Pressure:", weather["pressure"], "hPa")
    print("Cloud Cover:", weather["cloud_cover"], "%")
else:
    print("City not found.")