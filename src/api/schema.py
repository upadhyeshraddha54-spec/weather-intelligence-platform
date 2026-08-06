from pydantic import BaseModel

class WeatherInput(BaseModel):
    humidity: float
    precip: float
    month: int
    day: int
    dayofweek: int
    season: int