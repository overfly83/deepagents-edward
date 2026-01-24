#!/usr/bin/env python3
"""
Test script to verify MCP integration with Weather Agent.
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agents.weather.weather_agent import WeatherAgent


def test_mcp_integration():
    """Test that the Weather Agent can use the MCP tools."""
    print("Testing MCP Integration with Weather Agent...")
    
    try:
        # Initialize the weather agent in test mode
        agent = WeatherAgent(test_mode=True)
        
        # Verify the tools are imported correctly
        print(f"\nAvailable tools: {[tool.name for tool in agent.tools]}")
        
        # Verify the tool references are correct
        assert len(agent.tools) == 2
        assert agent.tools[0].name == "get_current_weather"
        assert agent.tools[1].name == "get_weather_forecast"
        
        print("\nTool verification passed!")
        print("Test completed successfully! MCP integration is working.")
        return True
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_mcp_integration()
    sys.exit(0 if success else 1)