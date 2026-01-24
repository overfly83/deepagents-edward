import os
import sys
from dotenv import load_dotenv

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Load environment variables
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Import custom logger
from utils.logger import get_logger

logger = get_logger(__name__, source='WEATHER_AGENT_TEST')

from agents.weather.weather_agent import WeatherAgent

def test_conversation_context():
    """
    Test that the WeatherAgent maintains conversation context between messages.
    Scenario:
    1. User asks: "北京明天天气如何"
    2. Agent responds asking for temperature unit
    3. User replies: "摄氏度"
    4. Agent should remember the original query and provide weather for Beijing
    """
    logger.info("=== Testing Weather Agent Conversation Context ===")
    
    try:
        # Initialize the weather agent
        agent = WeatherAgent()
        logger.info("✓ WeatherAgent initialized")
        
        # Step 1: User asks about tomorrow's weather in Beijing
        logger.info("\n1. User: 北京明天天气如何")
        response1 = agent.chat("北京明天天气如何")
        logger.info(f"   Agent: {response1}")
        
        # Step 2: User specifies temperature unit
        logger.info("\n2. User: 摄氏度")
        response2 = agent.chat("摄氏度")
        logger.info(f"   Agent: {response2}")
        
        # Verify that the agent remembered the context
        if "北京" in response2 or "Beijing" in response2:
            logger.info("\n✅ SUCCESS: Agent maintained conversation context!")
            logger.info("   The agent remembered the user was asking about Beijing's weather.")
            return True
        else:
            logger.warning("\n❌ WARNING: Agent may not have maintained full context.")
            logger.info("   The response doesn't explicitly mention Beijing.")
            logger.info(f"   Response: {response2}")
            return False
            
    except Exception as e:
        logger.error(f"\n❌ ERROR: Test failed with exception: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    logger.info("Starting weather agent conversation context test...")
    
    success = test_conversation_context()
    
    if success:
        logger.info("\n🎉 All tests completed successfully!")
        sys.exit(0)
    else:
        logger.info("\n⚠️  Test completed with warnings or failures.")
        sys.exit(1)