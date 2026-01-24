# Weather Searching Agent

A conversational AI agent that provides current weather information and forecasts for cities around the world using the OpenWeatherMap API.

## Features

- **Current Weather**: Get real-time weather conditions for any city
- **Weather Forecasts**: Get 5-day weather forecasts with temperature, humidity, and conditions
- **Conversational Interface**: Natural language interaction with the agent
- **Country Code Support**: Specify country codes for ambiguous city names (e.g., Paris, FR vs Paris, US)
- **Error Handling**: Robust error handling for invalid cities and API issues

## Setup

### Prerequisites

1. **Python 3.8+** installed on your system
2. **OpenAI API Key** - Sign up at [platform.openai.com](https://platform.openai.com/api-keys)
3. **OpenWeatherMap API Key** - Get a free API key at [openweathermap.org/api](https://openweathermap.org/api)

### Installation

1. Clone this repository or ensure you have the weather agent files
2. Install dependencies (if not already installed):
   ```bash
   pip install -r requirements.txt
   ```

3. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

4. Edit `.env` and add your API keys:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   OPENWEATHERMAP_API_KEY=your_openweathermap_api_key_here
   ```

## Usage

### Interactive Mode

Run the weather agent in interactive mode:

```bash
python -m src.deepagents_demo.agents.weather_agent
```

Example conversation:
```
Weather Searching Agent
==================================================

Hello! I'm your weather assistant.
I can help you with current weather and forecasts.
Type 'quit' or 'exit' to end the conversation.

You: What's the weather like in London?
Assistant: The agent will fetch and display current weather information for London.

You: What about the forecast for Tokyo?
Assistant: The agent will provide a 5-day forecast for Tokyo.
```

### Programmatic Usage

```python
from src.deepagents_demo.agents import WeatherAgent

# Initialize the agent
agent = WeatherAgent()

# Get weather information
response = agent.chat("What's the weather like in New York?")
print(response)

# Use tools directly
from src.deepagents_demo.agents import get_current_weather, get_weather_forecast

# Current weather
weather = get_current_weather("London", "UK")
print(weather)

# Weather forecast
forecast = get_weather_forecast("Tokyo", 3)
print(forecast)
```

### API Examples

The agent can handle various weather-related queries:

- "What's the weather in Paris?"
- "Give me the forecast for London for the next 3 days"
- "Is it raining in Sydney?"
- "What's the temperature in Tokyo right now?"
- "Will it be sunny in Miami tomorrow?"

## Available Tools

### `get_current_weather(city, country_code=None)`

Gets current weather conditions for a specified city.

**Parameters:**
- `city` (str): City name (e.g., "London", "New York")
- `country_code` (str, optional): Two-letter country code (e.g., "US", "UK", "CN")

**Returns:** Formatted string with temperature, conditions, humidity, wind speed, and pressure.

### `get_weather_forecast(city, days=5, country_code=None)`

Gets weather forecast for a specified city.

**Parameters:**
- `city` (str): City name
- `days` (int): Number of days to forecast (1-5, default 5)
- `country_code` (str, optional): Two-letter country code

**Returns:** Formatted string with daily forecasts including temperature, conditions, and humidity.

## Testing

Run the test suite to verify the agent works correctly:

```bash
python test_weather_agent.py
```

The tests verify:
- Agent initialization
- Tool functionality
- Error handling for missing API keys
- Response structure

## API Limits and Costs

- **OpenWeatherMap**: Free tier allows 1,000 calls/day. Paid plans available for higher limits.
- **OpenAI**: Costs depend on model usage. gpt-4o-mini is relatively inexpensive for conversational tasks.

## Troubleshooting

### Common Issues

1. **"OPENWEATHERMAP_API_KEY not found"**
   - Ensure you've copied `.env.example` to `.env`
   - Add your OpenWeatherMap API key to the `.env` file

2. **"City not found"**
   - Check spelling of city name
   - Try adding country code (e.g., "Paris, FR")

3. **OpenAI API errors**
   - Verify your OpenAI API key is valid and has credits
   - Check your internet connection

4. **Module import errors**
   - Ensure you're running from the project root directory
   - Check that all dependencies are installed

### Getting Help

If you encounter issues:
1. Run the test suite: `python test_weather_agent.py`
2. Check the error messages for specific guidance
3. Verify your API keys are correctly configured

## Architecture

The WeatherAgent uses:
- **LangChain**: For tool integration and conversational flow
- **LangGraph**: For ReAct agent implementation
- **OpenAI GPT-4o-mini**: For natural language understanding
- **OpenWeatherMap API**: For weather data
- **Python requests**: For HTTP API calls

The agent follows a tool-calling architecture where user queries are interpreted and appropriate weather tools are invoked automatically.
