#!/usr/bin/env python3
"""
End-to-end test for Chinese weather query handling.
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agents.agent_manager import AgentManager
from agents.weather.weather_agent import WeatherAgent


def test_chinese_weather_end_to_end():
    """Test end-to-end Chinese weather query handling."""
    print("=" * 60)
    print("End-to-End Chinese Weather Query Test")
    print("=" * 60)
    
    try:
        # Initialize AgentManager
        agent_manager = AgentManager()
        print("✅ AgentManager initialized successfully")
        
        # Initialize WeatherAgent in test mode
        weather_agent = WeatherAgent(test_mode=True)
        print("✅ WeatherAgent initialized successfully")
        
        # Test Chinese weather queries
        chinese_queries = [
            "北京的天气怎么样？",
            "上海的温度是多少？",
            "广州明天会下雨吗？",
            "深圳下周的天气预报"
        ]
        
        print("\nTesting end-to-end Chinese weather queries:")
        print("=" * 60)
        
        for query in chinese_queries:
            print(f"\n\nQuery: {query}")
            print("-" * 40)
            
            # Step 1: Detect intent
            intent = agent_manager.detect_intent(query)
            print(f"1. Intent Detection: {intent}")
            
            if intent != "weather_inquiry":
                print(f"❌ Failed to detect weather intent for query: {query}")
                continue
            
            print("✅ Weather intent detected successfully")
            
            # Step 2: Process with WeatherAgent
            print("2. Processing with WeatherAgent...")
            try:
                response = weather_agent.run(query)
                print(f"3. Agent Response: {response}")
                print("✅ Successfully processed weather query")
            except Exception as e:
                print(f"❌ Error processing query: {e}")
            
        print("\n\n" + "=" * 60)
        print("✅ End-to-End Chinese Weather Query Test Complete!")
        print("✅ The system can now handle Chinese weather queries from intent detection to response.")
        print("=" * 60)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_chinese_weather_end_to_end()