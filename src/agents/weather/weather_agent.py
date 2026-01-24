"""
Weather Searching Agent

A conversational agent that can search for weather information using OpenWeatherMap API.
"""

import os
from typing import Any, Dict, Optional
from dotenv import load_dotenv

# Import custom logger utility
from utils.logger import get_logger
from mcp.weather.weather_tools import get_current_weather, get_weather_forecast
from agents.agent_base import AgentBase

# Setup logger with blue debug formatting and default source
logger = get_logger(__name__, source='WEATHER_AGENT')

from langchain_core.tools import tool
from langchain_community.chat_models import ChatZhipuAI
from deepagents import create_deep_agent

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))


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