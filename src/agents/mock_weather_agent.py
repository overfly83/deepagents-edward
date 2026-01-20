#!/usr/bin/env python3
"""
Mock WeatherAgent for testing WebSocket functionality
"""

import logging
import time
from typing import Any, Dict, Generator, List, Optional

from agents.agent_base import AgentBase
from utils.logger import get_logger

logger = get_logger("MockWeatherAgent")

class MockWeatherAgent(AgentBase):
    """
    Mock WeatherAgent implementation for testing WebSocket functionality
    """
    
    def __init__(self, model_name: str = "glm-4-flash") -> None:
        """
        Initialize the MockWeatherAgent.
        
        Args:
            model_name: Model name (not used in mock)
        """
        super().__init__()
        self.agent_id = "mock-weather-agent"
        logger.info(f"[{self.agent_id}] Initialized MockWeatherAgent")
    
    def get_supported_intents(self) -> List[str]:
        """
        Get the list of supported intents.
        
        Returns:
            List of supported intents
        """
        return ["weather_inquiry"]
    
    def chat(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Process a chat message synchronously.
        
        Args:
            message: User message
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        logger.info(f"[{self.agent_id}] Processing chat request: {message}")
        
        # Simulate processing time
        time.sleep(1)
        
        # Generate mock response
        response = {
            "content": f"Mock weather information for query: '{message}'. "
                      f"This is a simulated response for testing purposes.",
            "status": "success",
            "type": "answer"
        }
        
        logger.info(f"[{self.agent_id}] Chat response generated")
        return response
    
    def stream_chat(self, message: str, **kwargs: Any) -> Generator[Dict[str, Any], None, None]:
        """
        Process a chat message asynchronously with streaming.
        
        Args:
            message: User message
            **kwargs: Additional parameters
            
        Yields:
            Response chunks in the format expected by the AgentManager
        """
        logger.info(f"[{self.agent_id}] Processing stream chat request: {message}")
        
        # Mock response content
        mock_content = [
            "Mock weather information for query: ",
            f"'{message}'. ",
            "This is a simulated stream response. ",
            "It demonstrates how the WebSocket streaming works."
        ]
        
        # Send content chunks in the format expected by AgentManager
        full_content = ""
        for chunk in mock_content:
            full_content += chunk
            # Create a message-like object with content attribute
            class MessageChunk:
                def __init__(self, content):
                    self.content = content
            
            yield {
                "messages": [MessageChunk(full_content)]
            }
            time.sleep(0.5)  # Simulate network delay
        
        logger.info(f"[{self.agent_id}] Stream chat completed")
    
    def run(self, message: str, **kwargs: Any) -> Dict[str, Any]:
        """
        Run the agent (same as chat for mock).
        
        Args:
            message: User message
            **kwargs: Additional parameters
            
        Returns:
            Response dictionary
        """
        return self.chat(message, **kwargs)

# Register the mock agent
if __name__ == "__main__":
    # Test the mock agent
    agent = MockWeatherAgent()
    
    # Test chat method
    print("Testing chat method...")
    response = agent.chat("What's the weather in Beijing?")
    print(f"Response: {response}")
    
    # Test stream_chat method
    print("\nTesting stream_chat method...")
    for chunk in agent.stream_chat("What's the weather in Shanghai?"):
        print(f"Stream chunk: {chunk}")