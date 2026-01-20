#!/usr/bin/env python3
"""
Test just the weather tools without the agent framework.
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Set up logging
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

from agents.weather.weather_agent import get_current_weather, get_weather_forecast

print("Testing Weather Tools Directly...")
print("=" * 50)

# Test get_current_weather
try:
    print("\n1. Testing get_current_weather...")
    result = get_current_weather("Beijing", "CN")
    if result:
        print("✅ Success!")
        print(result)
    else:
        print("❌ Failed to get weather")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Test get_weather_forecast
try:
    print("\n2. Testing get_weather_forecast...")
    result = get_weather_forecast("Shanghai", days=2, country_code="CN")
    if result:
        print("✅ Success!")
        print(result)
    else:
        print("❌ Failed to get forecast")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 50)
print("Weather Tool Tests Complete!")