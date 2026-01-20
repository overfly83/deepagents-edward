import sys
import os
import logging

# Add src directory to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Test the logger from utils
from src.utils.logger import get_logger, log_with_source

# Test 1: Basic logger with colored levels
print("=== Test 1: Basic Logger with Colored Levels ===")
basic_logger = get_logger('basic_logger', level=logging.DEBUG)
basic_logger.debug("This is a debug message - should be blue")
basic_logger.info("This is an info message - should be normal")
basic_logger.warning("This is a warning message - should be yellow")
basic_logger.error("This is an error message - should be red")
basic_logger.critical("This is a critical message - should be orange-red")

# Test 2: Logger with default source
print("\n=== Test 2: Logger with Default Source ===")
source_logger = get_logger('source_logger', level=logging.DEBUG, source='WEATHER_MODULE')
source_logger.debug("Debug message with source")
source_logger.info("Info message with source")
source_logger.warning("Warning message with source")
source_logger.error("Error message with source")
source_logger.critical("Critical message with source")

# Test 3: log_with_source function
print("\n=== Test 3: log_with_source Function ===")
general_logger = get_logger('general_logger', level=logging.DEBUG)
log_with_source(general_logger, logging.DEBUG, "Debug with dynamic source", source='API_HANDLER')
log_with_source(general_logger, logging.INFO, "Info with dynamic source", source='API_HANDLER')
log_with_source(general_logger, logging.WARNING, "Warning with dynamic source", source='API_HANDLER')
log_with_source(general_logger, logging.ERROR, "Error with dynamic source", source='API_HANDLER')
log_with_source(general_logger, logging.CRITICAL, "Critical with dynamic source", source='API_HANDLER')

# Test 4: Override default source
print("\n=== Test 4: Override Default Source ===")
sensor_logger = get_logger('sensor_logger', level=logging.DEBUG, source='DEFAULT_SENSOR')
sensor_logger.info("Using default source")
log_with_source(sensor_logger, logging.INFO, "Overriding with specific source", source='TEMPERATURE_SENSOR')

# Test 5: Direct source parameter in logging methods
print("\n=== Test 5: Direct Source Parameter in Logging Methods ===")
dynamic_logger = get_logger('dynamic_logger', level=logging.DEBUG)
dynamic_logger.debug("Debug message with direct source", source='DYNAMIC_DEBUG')
dynamic_logger.info("Info message with direct source", source='DYNAMIC_INFO')
dynamic_logger.warning("Warning message with direct source", source='DYNAMIC_WARNING')
dynamic_logger.error("Error message with direct source", source='DYNAMIC_ERROR')
dynamic_logger.critical("Critical message with direct source", source='DYNAMIC_CRITICAL')

# Test 6: Override default source using direct parameter
print("\n=== Test 6: Override Default Source Using Direct Parameter ===")
predefined_logger = get_logger('predefined_logger', level=logging.DEBUG, source='DEFAULT_SOURCE')
predefined_logger.info("Using logger's default source")
predefined_logger.info("Overriding with direct parameter", source='OVERRIDE_SOURCE')

print("\nLogger test completed!")