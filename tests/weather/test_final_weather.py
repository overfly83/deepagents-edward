#!/usr/bin/env python3
"""
Final test script to simulate user interaction with WeatherAgent
"""

import sys
import os

# Add the project root directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import the module directly
from agents.weather.weather_agent import WeatherAgent

def main():
    print("Testing WeatherAgent with Shanghai weather query...")
    print("=" * 60)
    
    # Initialize the agent
    agent = WeatherAgent()
    
    # Test 1: Get current weather for Shanghai
    print("\n1. Testing: What's the weather like in Shanghai today?")
    
    # Process the user query
    result = agent.chat("What's the weather like in Shanghai today?")
    
    print(f"Result: {result}")
    print("=" * 60)
    
    # Test 2: Get forecast for Shanghai
    print("\n2. Testing: What's the 3-day weather forecast for Shanghai?")
    
    # Process the user query
    result = agent.chat("What's the 3-day weather forecast for Shanghai?")
    
    print(f"Result: {result}")
    print("=" * 60)

if __name__ == "__main__":
    main()