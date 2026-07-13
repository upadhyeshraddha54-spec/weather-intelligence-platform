from src.data.config import WeatherConfig
from src.data.collector import WeatherCollector
from src.data.validator import WeatherValidator
from src.data.storage import WeatherStorage


def main():
    config = WeatherConfig()
    collector = WeatherCollector(config)

    # Fetch weather data
    weather = collector.fetch_current_weather()

    # Validate weather data
    WeatherValidator.validate(weather)
    print("Weather data is valid!")

    # Save weather data
    WeatherStorage.save(weather)
    print(" Weather data saved successfully!")

    # Display weather information
    current = weather["current"]

    print(f"Temperature : {current['temperature_2m']} °C")
    print(f"Humidity    : {current['relative_humidity_2m']} %")
    print(f"Wind Speed  : {current['wind_speed_10m']} km/h")


if __name__ == "__main__":
    main()