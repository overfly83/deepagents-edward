from pydantic import BaseModel
from typing import Optional, List


class CurrentWeather(BaseModel):
    """Pydantic model for current weather data"""
    temperature_2m: float
    apparent_temperature: float
    relative_humidity_2m: int
    weather_code: int
    wind_speed_10m: float
    pressure_msl: Optional[float] = None  # Optional field for air pressure

class DailyForecast(BaseModel):
    """Pydantic model for daily forecast data"""
    time: List[str]
    temperature_2m_max: List[float]
    temperature_2m_min: List[float]
    weather_code: List[int]