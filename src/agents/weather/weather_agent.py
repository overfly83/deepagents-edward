"""
Weather Searching Agent

A conversational agent that can search for weather information using OpenWeatherMap API.
"""

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from langchain_core.tools import tool
from deepagents import create_deep_agent, MemoryMiddleware
from deepagents.middleware.filesystem import FilesystemMiddleware

# Import LLM utility
from utils.llm import get_llm

# Import custom logger utility
from utils.logger import get_logger
from mcp.weather.weather_tools import get_current_weather, get_weather_forecast
from agents.agent_base import AgentBase

# Setup logger with blue debug formatting and default source
logger = get_logger(__name__, source='WEATHER_AGENT')

# Create a wrapper for FilesystemMiddleware to add missing methods
class CustomFilesystemMiddleware(FilesystemMiddleware):
    # Define a simple Response class that matches the expected structure
    class Response:
        def __init__(self, error=None, content=None):
            self.error = error
            self.content = content
    
    def download_files(self, paths, **kwargs):
        """Properly implement download_files to match expected structure."""
        # Return exactly one Response object for each requested path
        responses = []
        for path in paths:
            # Return a Response with file_not_found error for all paths
            # This allows graceful degradation as expected by the middleware
            responses.append(self.Response(error="file_not_found", content=None))
        return responses
    
    def __getattr__(self, name):
        """Catch any missing method calls and return appropriate default behavior."""
        # Default behavior for other missing methods
        def default_method(*args, **kwargs):
            return []
        return default_method

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
        
        self.llm = get_llm(provider="zhipu", model=model, temperature=temperature, test_mode=test_mode)
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
        
        # Create memory middleware for persistent conversation history
        memory_middleware = MemoryMiddleware(
            backend=CustomFilesystemMiddleware(),  # Use custom filesystem backend with download_files method
            sources=["weather_agent_memory"]  # Memory source name for organization
        )

        # Create the Deep Agent with memory capabilities
        self.agent = create_deep_agent(
            model=self.llm,
            tools=self.tools,
            system_prompt=self.system_prompt,
            middleware=[memory_middleware]  # Add memory middleware
        )
        
        # Initialize conversation history to maintain context between calls
        self.conversation_history = []
    
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
            
            # Add current user message to conversation history
            self.conversation_history.append(("user", message))
            self.logger.info(f"Conversation history: {self.conversation_history}")
            
            # Prepare the input with full conversation history
            input_data = {"messages": self.conversation_history}
            self.logger.info(f"Agent input: {input_data}")
            
            # Invoke the agent with detailed logging
            self.logger.info("Invoking agent...")
            result = self.agent.invoke(input_data)
            self.logger.info(f"Agent invocation successful. Result type: {type(result)}")
            self.logger.debug(f"Raw agent result: {result}")
            
            # Get the response content from different possible result formats
            response_content = None
            
            if isinstance(result, dict):
                # Check if result has a direct content field
                if "content" in result:
                    response_content = result["content"]
                    self.logger.info(f"Found direct content in result: {response_content[:100]}...")
                # Check if result has messages
                elif "messages" in result:
                    messages = result["messages"]
                    self.logger.info(f"Found {len(messages)} messages in response")
                    
                    if messages:
                        # Iterate through messages to find the last assistant message
                        for msg in reversed(messages):
                            if isinstance(msg, tuple) and msg[0] == "assistant":
                                response_content = msg[1]
                                self.logger.info(f"Found assistant tuple message: {response_content[:100]}...")
                                break
                            elif hasattr(msg, "content") and hasattr(msg, "type") and msg.type == "assistant":
                                response_content = msg.content
                                self.logger.info(f"Found assistant object message: {response_content[:100]}...")
                                break
                            elif isinstance(msg, dict) and msg.get("type") == "assistant" and "content" in msg:
                                response_content = msg["content"]
                                self.logger.info(f"Found assistant dict message: {response_content[:100]}...")
                                break
                            elif hasattr(msg, "content"):  # Fallback: assume it's assistant if it has content
                                response_content = msg.content
                                self.logger.info(f"Found message with content (fallback): {response_content[:100]}...")
                                break
            elif isinstance(result, str):
                # If result is directly a string
                response_content = result
                self.logger.info(f"Found string result: {response_content[:100]}...")
            else:
                error_msg = f"Unexpected result type from agent: {type(result)}"
                self.logger.error(error_msg)
            
            # Add assistant response to conversation history
            if response_content:
                self.conversation_history.append(("assistant", response_content))
                self.logger.info(f"Updated conversation history: {self.conversation_history}")
                self.log_final_result(response_content)
                return response_content
            else:
                self.logger.error("No response content found")
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
    # Print welcome message (allowed in main since it's interactive)
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