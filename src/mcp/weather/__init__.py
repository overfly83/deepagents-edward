"""Weather MCP module containing tools and models for weather functionality."""

from .model import CurrentWeather, DailyForecast
from .weather_tools import get_current_weather, get_weather_forecast

__all__ = [
    "CurrentWeather",
    "DailyForecast",
    "get_current_weather",
    "get_weather_forecast"
]