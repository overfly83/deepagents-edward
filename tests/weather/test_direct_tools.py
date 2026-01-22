#!/usr/bin/env python3
"""
Test the weather tools directly without the LLM agent.
"""
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.weather.weather_agent import _get_weather_data, _validate_input
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_weather_tools():
    """Test the weather data retrieval directly."""
    logger.info("Testing weather tools directly...")
    
    # Test validation function
    logger.info("Testing _validate_input...")
    city = "Beijing"
    country_code = "CN"
    validation_error = _validate_input(city, country_code, 3)
    if validation_error:
        logger.error(f"Validation failed: {validation_error}")
    else:
        logger.info("Validation passed!")
    
    # Test weather data retrieval
    logger.info("Testing _get_weather_data...")
    try:
        data, error = _get_weather_data(city, country_code, "metric")
        
        if error:
            logger.error(f"Weather data retrieval failed: {error}")
        elif data:
            logger.info(f"Weather data retrieval successful!")
            logger.debug(f"Data structure: {list(data.keys())}")
            
            if "current" in data:
                logger.info(f"Current weather data: {data['current'].keys()}")
            if "daily" in data:
                logger.info(f"Daily forecast data: {data['daily'].keys()}")
        else:
            logger.warning("No data returned from weather API")
            
    except Exception as e:
        logger.error(f"Exception in _get_weather_data: {e}", exc_info=True)

if __name__ == "__main__":
    test_weather_tools()