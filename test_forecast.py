from src.forecast.live_forecast import get_forecast

forecast = get_forecast("Pune")

for day in forecast:
    print(day)