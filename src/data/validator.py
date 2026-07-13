class WeatherValidator:
    """
    Validates weather data received from the API.
    """

    @staticmethod
    def validate(weather: dict) -> bool:

        if "current" not in weather:
            raise ValueError("Missing 'current' weather data.")

        current = weather["current"]

        required_fields = [
            "temperature_2m",
            "relative_humidity_2m",
            "wind_speed_10m"
        ]

        for field in required_fields:
            if field not in current:
                raise ValueError(f"Missing field: {field}")

        return True