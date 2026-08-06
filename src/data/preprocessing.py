import pandas as pd


class WeatherPreprocessor:

    INPUT_FILE = "weather_data.csv"
    OUTPUT_FILE = "processed_weather_data.csv"

    @staticmethod
    def get_part_of_day(hour):
        if 5 <= hour < 12:
            return "Morning"
        elif 12 <= hour < 17:
            return "Afternoon"
        elif 17 <= hour < 21:
            return "Evening"
        else:
            return "Night"
    @staticmethod
    def preprocess():

        df = pd.read_csv(WeatherPreprocessor.INPUT_FILE)

        print("Original Dataset")
        print(df.head())

        df.drop_duplicates(inplace=True)

        df["Time"] = pd.to_datetime(df["Time"])

        df["Hour"] = df["Time"].dt.hour
        df["Day"] = df["Time"].dt.day
        df["Month"] = df["Time"].dt.month
        df["Year"] = df["Time"].dt.year
        df["DayOfWeek"] = df["Time"].dt.dayofweek
        # derive part of day
        df["PartOfDay"] = df["Hour"].apply(WeatherPreprocessor.get_part_of_day)
        df["Season"] = df["Month"].apply(
    WeatherPreprocessor.get_season
) 
        df["IsMonsoon"] = df["Season"] == "Monsoon"
        df["TemperatureCategory"] = df["Temperature"].apply(
    WeatherPreprocessor.get_temperature_category
)
        df["HumidityCategory"] = df["Humidity"].apply(
    WeatherPreprocessor.get_humidity_category
) 
        df["WindCategory"] = df["Wind Speed"].apply(
    WeatherPreprocessor.get_wind_category
)
        df.to_csv(
            WeatherPreprocessor.OUTPUT_FILE,
            index=False
        )

        print("\nProcessed Dataset")
        print(df.head())

        print("\nDataset preprocessing completed!")
    @staticmethod
    def get_season(month):

      if month in [3, 4, 5]:
        return "Summer"

      elif month in [6, 7, 8, 9]:
        return "Monsoon"

      elif month in [10, 11]:
        return "Post-Monsoon"

      else:
        return "Winter"
    @staticmethod
    def get_temperature_category(temp):

     if temp < 15:
        return "Cold"

     elif temp < 30:
        return "Moderate"

     else:
        return "Hot" 
    @staticmethod
    def get_humidity_category(humidity):

     if humidity < 40:
        return "Low"

     elif humidity < 70:
        return "Medium"

     else:
        return "High"
    @staticmethod
    def get_wind_category(speed):

     if speed < 10:
        return "Calm"

     elif speed < 20:
        return "Breezy"

     else:
        return "Windy"