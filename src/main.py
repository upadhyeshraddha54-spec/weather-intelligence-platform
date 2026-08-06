from src.data.config import WeatherConfig
from src.data.collector import WeatherCollector
from src.data.validator import WeatherValidator
from src.data.storage import WeatherStorage
from src.data.analysis import WeatherAnalysis
from src.data.preprocessing import WeatherPreprocessor
from src.data.model import WeatherModel

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
    print("Weather data saved successfully!")

    # Analyze the dataset
    WeatherAnalysis.analyze()
    WeatherPreprocessor.preprocess()
    WeatherModel.train()

    # Display current weather
    current = weather["current"]

    print(f"Temperature : {current['temperature_2m']} °C")
    print(f"Humidity    : {current['relative_humidity_2m']} %")
    print(f"Wind Speed  : {current['wind_speed_10m']} km/h")


if __name__ == "__main__":
    main()