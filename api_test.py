#!/usr/bin/env python3
"""
Test just the weather API functionality without the agent wrapper.
"""
import os
import requests
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

print("Testing Weather API Directly...")

# Test Open-Meteo API (which doesn't require API key)
try:
    print("\n1. Testing Open-Meteo Geocoding API...")
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {
        "name": "Beijing",
        "count": 1,
        "language": "en",
        "format": "json"
    }
    
    start_time = time.time()
    response = requests.get(geocoding_url, params=params, timeout=5)
    print(f"   Status: {response.status_code} (took {time.time() - start_time:.2f}s)")
    print(f"   URL: {response.url}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Response data: {data}")
        if data and "results" in data and data["results"]:
            result = data["results"][0]
            print(f"   Beijing coordinates: {result['latitude']}, {result['longitude']}")
            lat, lon = result['latitude'], result['longitude']
        else:
            print("   No results found for Beijing")
            lat, lon = 39.9042, 116.4074  # Default Beijing coordinates
    else:
        print(f"   Geocoding API error: {response.text}")
        lat, lon = 39.9042, 116.4074  # Default Beijing coordinates

except Exception as e:
    print(f"   Geocoding error: {e}")
    import traceback
    traceback.print_exc()
    lat, lon = 39.9042, 116.4074  # Default Beijing coordinates

# Test weather API
try:
    print("\n2. Testing Open-Meteo Weather API...")
    weather_url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,wind_speed_10m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,weather_code",
        "temperature_unit": "celsius",
        "timezone": "Asia/Shanghai",
        "forecast_days": 5
    }
    
    start_time = time.time()
    response = requests.get(weather_url, params=params, timeout=5)
    print(f"   Status: {response.status_code} (took {time.time() - start_time:.2f}s)")
    print(f"   URL: {response.url}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"   Response structure: {list(data.keys())}")
        if "current" in data:
            print(f"   Current temperature: {data['current']['temperature_2m']}°C")
            print(f"   Weather code: {data['current']['weather_code']}")
        if "daily" in data:
            print(f"   Daily forecast available for {len(data['daily']['time'])} days")
    else:
        print(f"   Weather API error: {response.text}")

except Exception as e:
    print(f"   Weather API error: {e}")
    import traceback
    traceback.print_exc()

print("\nAPI Tests Complete!")