def classify_rainfall(rainfall):

    if rainfall < 5:
        return "Light Rain"

    elif rainfall < 20:
        return "Moderate Rain"

    elif rainfall < 50:
        return "Heavy Rain"

    elif rainfall < 100:
        return "Very Heavy Rain"

    return "Extreme Rain"


def classify_temperature(temp):

    if temp >= 40:
        return "Heatwave Risk"

    return "Normal"


def classify_wind(wind):

    if wind >= 60:
        return "Strong Wind Risk"

    return "Normal"


def analyze_forecast(forecast):

    results = []

    for day in forecast:

        results.append({
            "date": day["date"],
            "max_temp": day["max_temp"],
            "min_temp": day["min_temp"],
            "rainfall": day["rainfall"],
            "wind": day["wind"],
            "rainfall_class": classify_rainfall(day["rainfall"]),
            "temperature_class": classify_temperature(day["max_temp"]),
            "wind_class": classify_wind(day["wind"])
        })

    return results