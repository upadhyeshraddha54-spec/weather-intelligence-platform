import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression


class WeatherModel:

    FILE_NAME = "processed_weather_data.csv"

    @staticmethod
    def train():

        df = pd.read_csv(WeatherModel.FILE_NAME)

        print("\nDataset")
        print(df.head())

        # Features (Input)
        X = df[[
            "Humidity",
            "Wind Speed",
            "Hour",
            "Month"
        ]]

        # Target (Output)
        y = df["Temperature"]

        X_train, X_test, y_train, y_test = train_test_split(
            X,
            y,
            test_size=0.2,
            random_state=42
        )

        model = LinearRegression()

        model.fit(X_train, y_train)

        print("\nModel trained successfully!")

        predictions = model.predict(X_test)

        print("\nPredictions")
        print(predictions)