from src.data.config import WeatherConfig
from src.data.collector import WeatherCollector


def main():
    config = WeatherConfig()

    collector = WeatherCollector(config)

    weather = collector.fetch_current_weather()

    current = weather["current"]

    print(f"Temperature : {current['temperature_2m']} °C")
    print(f"Humidity    : {current['relative_humidity_2m']} %")
    print(f"Wind Speed  : {current['wind_speed_10m']} km/h")


if __name__ == "__main__":
    main()