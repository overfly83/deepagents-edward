#!/usr/bin/env python3
"""
Test script to verify fixed weather functionality
"""

import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the module directly
from agents.weather.weather_agent import (
    _get_coordinates,
    _get_weather_data
)

def main():
    print("Testing fixed weather functionality...")
    print("=" * 50)
    
    # Test with Shanghai
    city = "Shanghai"
    country_code = "CN"
    
    # Test coordinates
    print(f"\n1. Getting coordinates for {city}, {country_code}:")
    coords, error = _get_coordinates(city, country_code)
    if error:
        print(f"Error: {error}")
        return
    print(f"Coordinates: {coords}")
    
    # Test weather data
    print(f"\n2. Getting weather data for {city}, {country_code}:")
    data, error = _get_weather_data(city, country_code, "metric")
    if error:
        print(f"Error: {error}")
        return
    
    print("Success! Weather data received.")
    print(f"Current temperature: {data['current'].get('temperature_2m')}°C")
    print(f"Feels like: {data['current'].get('apparent_temperature')}°C")
    print(f"Humidity: {data['current'].get('relative_humidity_2m')}%")
    print(f"Wind speed: {data['current'].get('wind_speed_10m')} m/s")
    print(f"Weather code: {data['current'].get('weather_code')}")
    
    # Test daily forecast
    print(f"\n3. Daily forecast for {city}:")
    if "daily" in data:
        dates = data['daily']['time']
        max_temps = data['daily']['temperature_2m_max']
        min_temps = data['daily']['temperature_2m_min']
        
        for date, max_temp, min_temp in zip(dates[:3], max_temps[:3], min_temps[:3]):
            print(f"  {date}: {min_temp}°C to {max_temp}°C")
    
    print("\n" + "=" * 50)
    print("All tests passed successfully!")

if __name__ == "__main__":
    main()