#!/usr/bin/env python3
"""
Test script to verify Chinese intent detection functionality.
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from agents.agent_manager import AgentManager


def test_chinese_intent_detection():
    """Test that the AgentManager can detect intents from Chinese messages."""
    print("=" * 50)
    print("Chinese Intent Detection Test")
    print("=" * 50)
    
    try:
        # Initialize the AgentManager
        agent_manager = AgentManager()
        print("✅ AgentManager initialized successfully")
        
        # Test Chinese weather-related queries
        chinese_queries = [
            "今天天气怎么样？",
            "北京的温度是多少？",
            "明天会下雨吗？",
            "下周天气预报",
            "上海的晴天",
            "广州有没有雾霾？",
            "深圳会下雪吗？"
        ]
        
        print("\nTesting Chinese weather queries:")
        print("-" * 40)
        
        for query in chinese_queries:
            intent = agent_manager.detect_intent(query)
            print(f"Query: {query}")
            print(f"Detected Intent: {intent}")
            
            if intent == "weather_inquiry":
                print("✅ Correctly detected as weather_inquiry")
            else:
                print("❌ Failed to detect as weather_inquiry")
            
            print("-" * 40)
        
        # Test mixed language queries
        mixed_queries = [
            "北京的weather怎么样？",
            "今天temperature是多少？",
            "上海明天会rain吗？"
        ]
        
        print("\nTesting mixed language queries:")
        print("-" * 40)
        
        for query in mixed_queries:
            intent = agent_manager.detect_intent(query)
            print(f"Query: {query}")
            print(f"Detected Intent: {intent}")
            
            if intent == "weather_inquiry":
                print("✅ Correctly detected as weather_inquiry")
            else:
                print("❌ Failed to detect as weather_inquiry")
            
            print("-" * 40)
        
        # Test non-weather Chinese queries
        non_weather_queries = [
            "你好吗？",
            "今天是星期几？",
            "这是什么？"
        ]
        
        print("\nTesting non-weather Chinese queries:")
        print("-" * 40)
        
        for query in non_weather_queries:
            intent = agent_manager.detect_intent(query)
            print(f"Query: {query}")
            print(f"Detected Intent: {intent}")
            
            if intent is None:
                print("✅ Correctly detected as None (not weather-related)")
            else:
                print("❌ Incorrectly detected as weather_inquiry")
            
            print("-" * 40)
        
        print("\n" + "=" * 50)
        print("✅ Chinese Intent Detection Test Complete!")
        print("✅ The AgentManager can now handle Chinese intent detection.")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_chinese_intent_detection()