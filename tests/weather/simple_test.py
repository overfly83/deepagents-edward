#!/usr/bin/env python3
"""
Simple test script to verify the weather agent is working.
"""
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from agents.weather.weather_agent import WeatherAgent

print("Testing Weather Agent...")

try:
    # Create the agent
    agent = WeatherAgent()
    print("✓ WeatherAgent created successfully")
    
    # Test with a simple weather query
    query = "What's the weather in Beijing today?"
    print(f"\nSending query: {query}")
    
    # Use stream_chat method
    print("\n--- Using stream_chat ---")
    responses = []
    for chunk in agent.stream_chat(query):
        if chunk and "messages" in chunk and chunk["messages"]:
            content = chunk["messages"][0].get("content", "")
            if content:
                responses.append(content)
                print(f"> {content}")
    
    if responses:
        print(f"\n✓ Successfully received response via stream_chat")
        print(f"Complete response: {''.join(responses)}")
    else:
        print("\n✗ No response via stream_chat")
        
    # Use chat method for comparison
    print("\n--- Using chat ---")
    response = agent.chat(query)
    if response:
        print(f"> {response}")
        print("✓ Successfully received response via chat")
    else:
        print("✗ No response via chat")
        
    print("\n✅ All tests completed!")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)