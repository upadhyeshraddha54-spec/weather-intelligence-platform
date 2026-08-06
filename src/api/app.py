from fastapi import FastAPI
import joblib
import pandas as pd
from src.api.schema import WeatherInput

app = FastAPI()

model = joblib.load("best_weather_model.pkl")

@app.post("/predict")
def predict(data: WeatherInput):

    input_data = pd.DataFrame([{
        "humidity": data.humidity,
        "precip": data.precip,
        "Month": data.month,
        "Day": data.day,
        "DayOfWeek": data.dayofweek,
        "Season": data.season
    }])

    prediction = model.predict(input_data)

    return {
        "Predicted Temperature": round(prediction[0], 2)
    }