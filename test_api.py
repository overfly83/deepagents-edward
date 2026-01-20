#!/usr/bin/env python3
"""
Test the weather API functionality directly.
"""
import sys
import os
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.weather.weather_agent import WeatherAgent
from agents.weather.weather_agent import get_current_weather

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('WeatherAPITest')

def test_api_directly():
    """Test the API directly without the agent wrapper."""
    print("=== Testing Weather API Directly ===")
    
    try:
        # Test coordinate retrieval
        print("1. Testing coordinate retrieval for Beijing...")
        agent = WeatherAgent()
        lat, lon = agent._get_coordinates("Beijing")
        print(f"   Beijing coordinates: {lat}, {lon}")
        
        # Test API request
        print("2. Testing direct API request...")
        url = "https://api.openweathermap.org/data/2.5/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": agent.weather_api_key,
            "units": "metric",
            "lang": "en"
        }
        
        response = agent._make_api_request(url, params)
        print(f"   API response status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   API response data: {data.keys()}")
            print(f"   Weather: {data.get('weather', [{}])[0].get('description')}")
            print(f"   Temperature: {data.get('main', {}).get('temp')}°C")
        else:
            print(f"   API error: {response.text}")
            return False
            
        # Test get_current_weather function
        print("3. Testing get_current_weather function...")
        weather_info = get_current_weather("Beijing", agent.weather_api_key)
        print(f"   Weather info: {weather_info}")
        
        return True
        
    except Exception as e:
        print(f"ERROR during API test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_tool_use():
    """Test if the agent can use the weather tool."""
    print("\n=== Testing Agent Tool Usage ===")
    
    try:
        agent = WeatherAgent()
        
        # Test if the tool is properly registered
        print(f"Available tools: {[tool.name for tool in agent.agent.tools]}")
        
        # Try to use the tool directly
        print("\nTesting get_current_weather tool directly...")
        weather_tool = None
        for tool in agent.agent.tools:
            if tool.name == "get_current_weather":
                weather_tool = tool
                break
                
        if weather_tool:
            result = weather_tool.invoke({"city": "Beijing"})
            print(f"Tool result: {result}")
        else:
            print("ERROR: get_current_weather tool not found!")
            return False
            
        return True
        
    except Exception as e:
        print(f"ERROR during tool test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    api_success = test_api_directly()
    tool_success = test_agent_tool_use()
    
    print("\n=== Test Results ===")
    print(f"API direct test: {'PASSED' if api_success else 'FAILED'}")
    print(f"Agent tool test: {'PASSED' if tool_success else 'FAILED'}")
    
    if api_success and tool_success:
        print("✅ All API tests PASSED!")
        sys.exit(0)
    else:
        print("❌ Some API tests FAILED!")
        sys.exit(1)