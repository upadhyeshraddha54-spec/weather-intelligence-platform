def get_aqi_category(aqi):
    """Classify US AQI."""

    if aqi is None:
        return "AQI data unavailable"

    if aqi <= 50:
        return "Good"

    elif aqi <= 100:
        return "Moderate"

    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups"

    elif aqi <= 200:
        return "Unhealthy"

    elif aqi <= 300:
        return "Very Unhealthy"

    else:
        return "Hazardous"


def assess_risk(weather):
    """
    Assess weather and air-quality risks.
    """

    temperature = weather["temperature"]
    rainfall = weather["precipitation"]
    wind_speed = weather["wind_speed"]
    aqi = weather["aqi"]

    risks = []

    # -------------------------
    # Weather risks
    # -------------------------

    if temperature >= 40:
        risks.append("High Heatwave Risk")

    if rainfall >= 150:
        risks.append("Heavy Rain Alert")

    if rainfall >= 250:
        risks.append("Flood Warning")

    if wind_speed >= 60:
        risks.append("Strong Wind Warning")

    # -------------------------
    # Air quality risk
    # -------------------------

    aqi_category = get_aqi_category(aqi)

    if aqi_category == "Unhealthy for Sensitive Groups":
        risks.append("Air Quality Alert")

    elif aqi_category == "Unhealthy":
        risks.append("Unhealthy Air Quality")

    elif aqi_category == "Very Unhealthy":
        risks.append("Very Unhealthy Air Quality")

    elif aqi_category == "Hazardous":
        risks.append("Hazardous Air Quality")

    # -------------------------
    # No major risk
    # -------------------------

    if not risks:
        risks.append("No Major Weather or Air Quality Risk")

    return risks