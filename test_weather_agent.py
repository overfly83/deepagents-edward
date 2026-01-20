#!/usr/bin/env python3
"""
Test script to verify the weather agent functionality.
"""
import sys
import os
import logging

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.weather.weather_agent import WeatherAgent

def setup_logging():
    """Configure logging to see agent activity"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def test_weather_agent():
    """Test the weather agent with a sample query"""
    setup_logging()
    
    print("=== Weather Agent Test ===")
    print("Creating WeatherAgent instance...")
    
    # Create weather agent instance
    agent = WeatherAgent()
    
    print("\nTesting stream_chat method...")
    print("Query: What's the weather in Beijing today?")
    
    # Test stream_chat method
    try:
        responses = []
        for chunk in agent.stream_chat("What's the weather in Beijing today?"):
            if chunk and "messages" in chunk and chunk["messages"]:
                content = chunk["messages"][0].get("content", "")
                if content:
                    responses.append(content)
                    print(f"Received: {content}")
        
        print("\n=== Test Complete ===")
        print(f"Total responses received: {len(responses)}")
        print(f"Complete response: {''.join(responses)}")
        
        if not responses:
            print("ERROR: No response was received from the weather agent!")
            return False
        
        return True
        
    except Exception as e:
        print(f"ERROR during test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_chat_method():
    """Test the non-streaming chat method"""
    print("\n=== Testing non-streaming chat method ===")
    
    agent = WeatherAgent()
    
    try:
        response = agent.chat("What's the weather in Shanghai today?")
        print(f"Response: {response}")
        
        if not response:
            print("ERROR: No response from non-streaming chat!")
            return False
        
        return True
        
    except Exception as e:
        print(f"ERROR during chat test: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Running weather agent tests...\n")
    
    stream_success = test_weather_agent()
    chat_success = test_chat_method()
    
    print("\n=== Test Results ===")
    print(f"stream_chat test: {'PASSED' if stream_success else 'FAILED'}")
    print(f"chat test: {'PASSED' if chat_success else 'FAILED'}")
    
    if stream_success and chat_success:
        print("\n✅ All tests PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Some tests FAILED!")
        sys.exit(1)