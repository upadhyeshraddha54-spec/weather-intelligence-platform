import csv
import os


class WeatherStorage:
    """
    Saves validated weather data into a CSV file.
    """

    FILE_NAME = "weather_data.csv"

    @staticmethod
    def save(weather: dict):

        current = weather["current"]

        file_exists = os.path.isfile(WeatherStorage.FILE_NAME)

        with open(WeatherStorage.FILE_NAME,
                  mode="a",
                  newline="") as file:

            writer = csv.writer(file)

            if not file_exists:
                writer.writerow([
                    "Time",
                    "Temperature",
                    "Humidity",
                    "Wind Speed"
                ])

            writer.writerow([
                current["time"],
                current["temperature_2m"],
                current["relative_humidity_2m"],
                current["wind_speed_10m"]
            ])