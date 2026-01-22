"""
Weather Searching Agent

A conversational agent that can search for weather information using OpenWeatherMap API.
"""

import os
import requests
from typing import Optional, Dict, Any, Tuple
from functools import lru_cache
from dotenv import load_dotenv

# Import custom logger utility
from utils.logger import get_logger
from agents.weather.model import CurrentWeather, DailyForecast
from agents.agent_base import AgentBase

# Setup logger with blue debug formatting and default source
logger = get_logger(__name__, source='WEATHER_AGENT')

from langchain_core.tools import tool
from langchain_community.chat_models import ChatZhipuAI
from deepagents import create_deep_agent

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))

# API Configuration - Load from environment variables
BASE_WEATHER_URL = os.getenv("BASE_WEATHER_URL")
GEOCODING_URL = os.getenv("GEOCODING_URL")
API_TIMEOUT = int(os.getenv("API_TIMEOUT"))
CACHE_EXPIRY = int(os.getenv("CACHE_EXPIRY"))  # 5 minutes cache

# Country code validation (simplified for common countries)
VALID_COUNTRY_CODES = {"US", "UK", "CA", "AU", "DE", "FR", "IT", "JP", "CN", "IN", "BR", "RU", "ES", "MX", "KR"}

# Helper function for API requests
def _make_api_request(url: str, params: Dict[str, Any]) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Make an API request to the weather/geocoding API and handle errors.
    
    Args:
        url: API endpoint URL
        params: Request parameters
    
    Returns:
        Tuple of (data if successful, error message if failed)
    """
    try:
        logger.info(f"Making API request to: {url}")
        logger.debug(f"Request params: {params}")
        logger.debug(f"Timeout: {API_TIMEOUT} seconds")
        
        # Make the request with the specified timeout
        response = requests.get(url, params=params, timeout=API_TIMEOUT)
        response.raise_for_status()
        
        logger.info(f"API request successful! Status: {response.status_code}")
        logger.debug(f"Final URL: {response.url}")
        
        # Try to parse the response
        data = response.json()
        logger.debug(f"Response data type: {type(data)}")
        
        return data, ""
    except requests.exceptions.HTTPError as e:
        status_code = e.response.status_code if hasattr(e.response, 'status_code') else "unknown"
        logger.error(f"HTTP Error {status_code}: {e}")
        if status_code == 404:
            return None, f"City not found. Please check the city name and try again."
        return None, f"HTTP Error: {e}"
    except requests.exceptions.Timeout:
        logger.error(f"API request timed out after {API_TIMEOUT} seconds")
        return None, f"API request timed out. Please try again later."
    except requests.exceptions.ConnectionError:
        logger.error("Network connection error")
        return None, "Network connection error. Please check your internet connection."
    except requests.exceptions.RequestException as e:
        logger.error(f"Request Exception: {e}")
        return None, f"Network Error: {e}"
    except ValueError as e:
        logger.error(f"Error parsing JSON response: {e}")
        return None, f"Error parsing response: {e}"
    except Exception as e:
        logger.error(f"Unexpected error in API request: {e}", exc_info=True)
        return None, f"Unexpected error: {e}"


@lru_cache(maxsize=1000)
def _get_coordinates(city: str, country_code: Optional[str]) -> Tuple[Optional[Tuple[float, float]], str]:
    """
    Get geographic coordinates (latitude, longitude) for a city.
    
    Args:
        city: City name
        country_code: Optional country code
    
    Returns:
        Tuple of ((latitude, longitude) if successful, error message if failed)
    """
    logger.info(f"Getting coordinates for city: {city}, country_code: {country_code}")
    
    # Prepare geocoding API request
    params = {
        "name": city,
        "count": 1,
        "language": "en",
        "format": "json"
    }
    
    if country_code:
        params["country"] = country_code
    
    # Make API request to get coordinates
    data, error = _make_api_request(GEOCODING_URL, params)
    
    if error:
        logger.error(f"Error getting coordinates: {error}")
        return None, f"Failed to get coordinates: {error}"
    
    if not data or "results" not in data or not data["results"]:
        logger.error(f"No results found for city: {city}")
        return None, f"City '{city}' not found. Please check the city name."
    
    try:
        # Extract latitude and longitude from the response
        result = data["results"][0]
        lat = result["latitude"]
        lon = result["longitude"]
        logger.info(f"Found coordinates for {city}: ({lat}, {lon})")
        return (lat, lon), ""
    except KeyError as e:
        logger.error(f"Error parsing coordinates: {e}")
        return None, f"Error parsing coordinates: {e}"
    except Exception as e:
        logger.error(f"Unexpected error getting coordinates: {e}", exc_info=True)
        return None, f"Unexpected error: {e}"


@lru_cache(maxsize=1000)
def _get_weather_data(city: str, country_code: Optional[str], units: str) -> Tuple[Optional[Dict[str, Any]], str]:
    """
    Get weather data from Open-Meteo API with caching.
    
    Args:
        city: City name
        country_code: Optional country code
        units: Temperature units (metric/imperial)
    
    Returns:
        Tuple of (data if successful, error message if failed)
    """
    logger.info(f"Getting weather data for {city}, country: {country_code}, units: {units}")
    
    # First, get coordinates for the city
    coordinates, error = _get_coordinates(city, country_code)
    if error:
        logger.error(f"Failed to get coordinates: {error}")
        return None, error
    
    if not coordinates:
        logger.error(f"No coordinates found for {city}")
        return None, f"Could not find coordinates for {city}"
    
    lat, lon = coordinates
    
    # Prepare weather API request parameters
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "apparent_temperature", "relative_humidity_2m", "wind_speed_10m", "weather_code"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "weather_code"],
        "timezone": "Asia/Shanghai",  # Default to Asia/Shanghai timezone
        "forecast_days": 5
    }
    
    # Make API request to get weather data
    data, error = _make_api_request(BASE_WEATHER_URL, params)
    
    if error:
        logger.error(f"Error getting weather data: {error}")
        return None, f"Failed to get weather data: {error}"
    
    logger.info(f"Successfully retrieved weather data for {city}")
    return data, ""


def _validate_input(city: str, country_code: Optional[str] = None, days: Optional[int] = None) -> str:
    """
    Validate input parameters.
    
    Args:
        city: City name
        country_code: Optional country code
        days: Optional number of forecast days
    
    Returns:
        Empty string if valid, error message otherwise
    """
    if not city or not city.strip():
        return "Error: City name cannot be empty."
    
    if country_code:
        country_code = country_code.strip().upper()
        if len(country_code) != 2:
            return "Error: Country code must be a 2-letter ISO 3166 code."
        if country_code not in VALID_COUNTRY_CODES:
            return f"Error: Country code '{country_code}' is not recognized."
    
    if days is not None:
        if days < 1 or days > 5:
            return "Error: Forecast days must be between 1 and 5."
    
    return ""


# Weather code mapping for Open-Meteo API
WEATHER_CODE_MAPPING = {
    0: "clear sky",
    1: "mainly clear",
    2: "partly cloudy",
    3: "overcast",
    45: "fog",
    48: "depositing rime fog",
    51: "light drizzle",
    53: "moderate drizzle",
    55: "dense drizzle",
    56: "light freezing drizzle",
    57: "dense freezing drizzle",
    61: "slight rain",
    63: "moderate rain",
    65: "heavy rain",
    66: "light freezing rain",
    67: "heavy freezing rain",
    71: "slight snow fall",
    73: "moderate snow fall",
    75: "heavy snow fall",
    77: "snow grains",
    80: "slight rain showers",
    81: "moderate rain showers",
    82: "violent rain showers",
    85: "slight snow showers",
    86: "heavy snow showers",
    95: "thunderstorm",
    96: "thunderstorm with slight hail",
    99: "thunderstorm with heavy hail"
}

@tool
def get_current_weather(city: str, country_code: Optional[str] = None, units: str = "metric") -> str:
    """
    Get the current weather for a specified city.
    
    Args:
        city: The name of the city to get weather for (e.g., "London", "New York")
        country_code: Optional two-letter country code (e.g., "US", "UK", "CN")
        units: Temperature units ("metric" for Celsius, "imperial" for Fahrenheit)
    
    Returns:
        A string containing the current weather information
    """
    # Validate input
    validation_error = _validate_input(city, country_code)
    if validation_error:
        return validation_error
    
    # Get weather data with caching
    data, error = _get_weather_data(city.strip(), country_code.strip().upper() if country_code else None, units)
    
    if error:
        return error
    
    if not data:
        return "Error: Failed to retrieve weather data."
    
    try:
        # Get city name from geocoding if needed
        city_name = city
        country = country_code if country_code else ""
        
        # Extract and validate weather information using Pydantic
        current = CurrentWeather(**data["current"])
        weather_info = {
            "city": city_name,
            "country": country,
            "temperature": current.temperature_2m,
            "feels_like": current.apparent_temperature,
            "humidity": current.relative_humidity_2m,
            "weather_code": current.weather_code,
            "wind_speed": current.wind_speed_10m,
            "pressure": current.pressure_msl or "N/A",
        }
        
        # Get weather description
        weather_description = WEATHER_CODE_MAPPING.get(weather_info["weather_code"], "unknown")
        
        # Determine temperature unit symbol
        unit_symbol = "°C" if units == "metric" else "°F"
        
        result = f"""
Weather in {weather_info['city']}{f", {weather_info['country']}" if weather_info['country'] else ""}:
- Temperature: {weather_info['temperature']}{unit_symbol} (feels like {weather_info['feels_like']}{unit_symbol})
- Condition: {weather_description.capitalize()}
- Humidity: {weather_info['humidity']}%
- Wind Speed: {weather_info['wind_speed']} m/s
- Pressure: {weather_info['pressure']} hPa
"""
        return result.strip()
        
    # except KeyError as e:
    #     logger.warning(f"KeyError while parsing weather data: {e}")
        # return f"Error parsing weather data: Missing field {e}"
    except Exception as e:
        logger.error(f"Unexpected error processing weather data: {e}")
        return f"Unexpected error processing weather data: {e}"


@tool
def get_weather_forecast(city: str, days: int = 5, country_code: Optional[str] = None, units: str = "metric") -> str:
    """
    Get the weather forecast for a specified city.
    
    Args:
        city: The name of the city to get forecast for
        days: Number of days to forecast (1-5, default 5)
        country_code: Optional two-letter country code
        units: Temperature units ("metric" for Celsius, "imperial" for Fahrenheit)
    
    Returns:
        A string containing the weather forecast
    """
    # Validate input
    validation_error = _validate_input(city, country_code, days)
    if validation_error:
        return validation_error
    
    # Get forecast data with caching
    data, error = _get_weather_data(city.strip(), country_code.strip().upper() if country_code else None, units)
    
    if error:
        return error
    
    if not data:
        return "Error: Failed to retrieve forecast data."
    
    try:
        # Get city name from geocoding if needed
        city_name = city
        country = country_code if country_code else ""
        
        # Determine temperature unit symbol
        unit_symbol = "°C" if units == "metric" else "°F"
        
        # Validate forecast data using Pydantic
        daily_data = DailyForecast(**data["daily"])
        forecast_lines = [f"Weather Forecast for {city_name}{f", {country}" if country else ""}:"]
        
        # Process forecast for the requested number of days
        for i in range(min(days, len(daily_data.time))):
            date = daily_data.time[i]
            max_temp = daily_data.temperature_2m_max[i]
            min_temp = daily_data.temperature_2m_min[i]
            weather_code = daily_data.weather_code[i]
            weather_description = WEATHER_CODE_MAPPING.get(weather_code, "unknown")
            
            forecast_lines.append(f"\n{date}:")
            forecast_lines.append(f"  - Temperature: {min_temp}{unit_symbol} to {max_temp}{unit_symbol}")
            forecast_lines.append(f"  - Condition: {weather_description.capitalize()}")
        
        return "\n".join(forecast_lines)
        
    # except KeyError as e:
    #     return f"Error parsing forecast data: Missing field {e}"
    except Exception as e:
        return f"Unexpected error processing forecast data: {e}"


class WeatherAgent(AgentBase):
    """
    A weather searching agent that can answer questions about current weather
    and forecasts for cities around the world.
    """
    
    def __init__(self, model: str = "glm-4-flash", temperature: float = 0, test_mode: bool = False):
        """
        Initialize the weather agent.
        
        Args:
            model: The ZhipuAI model to use (default: glm-4-flash)
            temperature: The temperature for the model (default: 0)
            test_mode: If True, use a mock API key and skip validation (for testing purposes)
        """
        super().__init__()  # Initialize the base class with logging capabilities
        
        if not test_mode:
            # Validate ZhipuAI API key is available
            zhipu_api_key = os.getenv("ZHIPU_API_KEY")
            if not zhipu_api_key:
                raise ValueError("Error: ZHIPU_API_KEY not found in environment variables. Please set it in your .env file.")
        else:
            # Use a mock API key for testing purposes
            zhipu_api_key = "mock_api_key_for_testing"
        
        self.llm = ChatZhipuAI(model=model, temperature=temperature, api_key=zhipu_api_key)
        self.tools = [get_current_weather, get_weather_forecast]
        
        # System prompt for the agent
        self.system_prompt = """You are a helpful weather assistant. You can help users with:
        1. Getting the current weather for any city in the world
        2. Getting weather forecasts for up to 5 days

        When users ask about weather, use the appropriate tools to fetch the information.
        Always be friendly and provide helpful weather-related advice based on the conditions.
        If a city name is ambiguous, ask the user to specify the country.
        You can use either metric (Celsius) or imperial (Fahrenheit) units - default to metric unless user specifies otherwise.
        """
        
        # Create the Deep Agent
        self.agent = create_deep_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt
        )
    
    def plan_task(self, message: str) -> Dict[str, Any]:
        """
        Create a weather-specific task plan based on the user's message.
        
        Args:
            message: The user's message/question
            
        Returns:
            A dictionary containing the weather task plan with steps.
        """
        plan = {
            "task": f"Process weather request: {message[:50]}...",
            "steps": [
                "Analyze weather-related query",
                "Extract location and time parameters",
                "Fetch weather data from API",
                "Process and format weather information",
                "Generate user-friendly response"
            ]
        }
        self.logger.info(f"Weather Task Plan: {plan}")
        return plan

    def chat(self, message: str) -> str:
        """
        Send a message to the weather agent and get a response with detailed logging.
        
        Args:
            message: The user's message/question
            
        Returns:
            The agent's response
        """
        try:
            # Log the action of processing the chat request
            self.log_action("Processing chat request", message)
            
            # Prepare the input with proper message format
            input_data = {"messages": [("user", message)]}
            self.logger.info(f"Agent input: {input_data}")
            
            # Invoke the agent with detailed logging
            self.logger.info("Invoking agent...")
            result = self.agent.invoke(input_data)
            self.logger.info(f"Agent invocation successful. Result type: {type(result)}")
            self.logger.debug(f"Raw agent result: {result}")
            
            # Get the last message from the response
            if isinstance(result, dict):
                if "messages" in result:
                    messages = result["messages"]
                    self.logger.info(f"Found {len(messages)} messages in response")
                    
                    if messages:
                        last_message = messages[-1]
                        self.logger.info(f"Last message type: {type(last_message)}")
                        
                        if hasattr(last_message, "content"):
                            response_content = last_message.content
                            self.logger.info(f"Extracted response content: {response_content[:100]}...")
                            self.log_final_result(response_content)
                            return response_content
                        else:
                            self.logger.error(f"Last message has no content attribute: {last_message}")
                    else:
                        self.logger.error("No messages in agent response")
                else:
                    self.logger.error("No 'messages' key in agent response")
            else:
                error_msg = f"Unexpected result type from agent: {type(result)}"
                self.logger.error(error_msg)
                
            return "Sorry, I couldn't process your request."
        except Exception as e:
            self.logger.error(f"Error in chat: {e}", exc_info=True)
            return "Sorry, I encountered an error while processing your request."
    
    def stream_chat(self, message: str):
        """
        Send a message to the weather agent and stream the response.
        
        Args:
            message: The user's message/question
            
        Yields:
            Response chunks in the format expected by the WebSocket server
        """
        try:
            self.logger.info(f"Starting stream_chat with message: {message}")
            
            # Process the message through the non-streaming chat method first
            # This ensures the weather request is actually sent and we get a complete response
            response = self.chat(message)
            self.logger.info(f"Chat response obtained: {response[:100]}...")
            
            # Stream the response in chunks for compatibility with the WebSocket server
            if response:
                # Split the response into chunks of reasonable size
                chunk_size = 100
                for i in range(0, len(response), chunk_size):
                    chunk_content = response[i:i+chunk_size]
                    self.logger.debug(f"Yielding chunk: {chunk_content}")
                    yield {"messages": [{"content": chunk_content}]}
            else:
                self.logger.warning("No response from chat method")
                # Yield an error message
                yield {"messages": [{"content": "I'm sorry, I couldn't retrieve the weather information."}]}
                
            self.logger.info("Stream completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in stream_chat: {e}", exc_info=True)
            # Yield an error response
            error_msg = "I'm sorry, I encountered an error while processing your request."
            yield {"messages": [{"content": error_msg}]}
    
    async def run(self, location: str, date: Optional[str] = None, additional_info: Optional[str] = None) -> Dict[str, Any]:
        """
        Run the weather agent with specific parameters.
        
        Args:
            location: The location to get weather for
            date: Optional date for forecast
            additional_info: Optional additional information
            
        Returns:
            The result of the agent's execution as a dictionary.
        """
        # Format the message based on provided parameters
        if date:
            if additional_info:
                message = f"What's the weather in {location} on {date}? {additional_info}"
            else:
                message = f"What's the weather in {location} on {date}?"
        else:
            if additional_info:
                message = f"What's the weather in {location}? {additional_info}"
            else:
                message = f"What's the weather in {location}?"
        
        # Use the chat method to get the response
        response = self.chat(message)
        return {"response": response}
    
    def get_supported_intents(self) -> list[str]:
        """
        Get the list of intents supported by this agent.
        
        Returns:
            A list of supported intent strings.
        """
        return ["weather_inquiry", "forecast_inquiry", "temperature_check", "weather_conditions"]


def main():
    """Main function to run the weather agent interactively."""
    print("=" * 50)
    print("Weather Searching Agent")
    print("=" * 50)
    print("\nHello! I'm your weather assistant.")
    print("I can help you with current weather and forecasts.")
    print("Type 'quit' or 'exit' to end the conversation.\n")
    
    try:
        logger.debug("Initializing WeatherAgent...")
        agent = WeatherAgent()
        logger.debug("WeatherAgent initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing WeatherAgent: {e}")
        import traceback
        traceback.print_exc()
        return
    
    try:
        while True:
            try:
                user_input = input("You: ").strip()
                logger.debug(f"User input: '{user_input}'")
                
                if not user_input:
                    continue
                
                if user_input.lower() in ["quit", "exit", "bye", "goodbye"]:
                    print("\nGoodbye! Stay weather-aware! 🌤️")
                    break
                
                print("\nAssistant: ", end="")
                response = agent.chat(user_input)
                print(response)
                print()
            except KeyboardInterrupt:
                print("\n\nGoodbye! Stay weather-aware! 🌤️")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                import traceback
                traceback.print_exc()
    except Exception as e:
        logger.debug(f"Unexpected error in main function: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()