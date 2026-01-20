#!/usr/bin/env python3
"""
Test the weather functions directly without the LLM agent.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.weather.weather_agent import get_current_weather, get_weather_forecast
from langchain_core.tools import StructuredTool
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_weather_functions():
    """Test the weather functions directly."""
    logger.info("Testing weather functions directly...")
    
    # Test current weather
    logger.info("\n--- Testing get_current_weather ---")
    try:
        # Since these are StructuredTool objects, we need to use the invoke method
        if isinstance(get_current_weather, StructuredTool):
            # Get the function from the tool
            weather_func = get_current_weather.func
            result = weather_func(city="Beijing", country_code="CN", units="metric")
            logger.info(f"Current weather for Beijing: {result}")
        else:
            # Fallback if it's a direct function
            result = get_current_weather(city="Beijing", country_code="CN", units="metric")
            logger.info(f"Current weather for Beijing: {result}")
    except Exception as e:
        logger.error(f"Error in get_current_weather: {e}", exc_info=True)
    
    # Test weather forecast
    logger.info("\n--- Testing get_weather_forecast ---")
    try:
        if isinstance(get_weather_forecast, StructuredTool):
            # Get the function from the tool
            forecast_func = get_weather_forecast.func
            result = forecast_func(city="Shanghai", country_code="CN", days=3, units="metric")
            logger.info(f"3-day forecast for Shanghai: {result}")
        else:
            # Fallback if it's a direct function
            result = get_weather_forecast(city="Shanghai", country_code="CN", days=3, units="metric")
            logger.info(f"3-day forecast for Shanghai: {result}")
    except Exception as e:
        logger.error(f"Error in get_weather_forecast: {e}", exc_info=True)

if __name__ == "__main__":
    test_weather_functions()