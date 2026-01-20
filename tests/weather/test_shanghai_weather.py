#!/usr/bin/env python3
"""
Test script to check Shanghai weather without manual interaction
"""

import sys
import os

# Add the project root directory to the Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import the module directly
from agents.weather_agent import (
    get_current_weather, 
    get_weather_forecast,
    _get_coordinates,
    _get_weather_data
)

def main():
    print("Testing Shanghai weather functionality...")
    print("=" * 50)
    
    # Test 1: Get coordinates for Shanghai
    print("\n1. Testing coordinates for Shanghai:")
    coords, error = _get_coordinates("Shanghai", "CN")
    if error:
        print(f"Error getting coordinates: {error}")
    else:
        print(f"Got coordinates: {coords}")
    
    # Test 2: Get weather data
    print("\n2. Testing weather data for Shanghai:")
    data, error = _get_weather_data("Shanghai", "CN", "metric")
    if error:
        print(f"Error getting weather data: {error}")
    else:
        print(f"Success! Weather data received.")
        if "current" in data:
            print(f"Current temperature: {data['current'].get('temperature_2m')}°C")
            print(f"Weather code: {data['current'].get('weather_code')}")
    
    # Test 3: Get current weather
    print("\n3. Testing get_current_weather function:")
    result = get_current_weather.invoke({"city": "Shanghai", "country_code": "CN"})
    print(f"Result: {result}")
    
    # Test 4: Get weather forecast
    print("\n4. Testing get_weather_forecast function:")
    result = get_weather_forecast.invoke({"city": "Shanghai", "days": 2, "country_code": "CN"})
    print(f"Result: {result}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    main()