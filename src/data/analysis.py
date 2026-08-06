import pandas as pd


class WeatherAnalysis:

    FILE_NAME = "weather_data.csv"

    @staticmethod
    def analyze():

        df = pd.read_csv(WeatherAnalysis.FILE_NAME)

        print("\nDataset Preview")
        print(df)

        print("\nStatistics")
        print(df.describe())