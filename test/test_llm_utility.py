#!/usr/bin/env python3
"""
Test file for LLM utility module.
"""

import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Import custom logger
from utils.logger import get_logger
logger = get_logger(__name__, source='LLM_UTILITY_TEST')

def test_llm_creation():
    """Test that LLM utility can create LLM instances."""
    logger.info("Testing LLM utility module...")
    
    from utils.llm import get_llm, LLMFactory
    
    # Test 1: Create ZhipuAI LLM in test mode
    logger.info("1. Testing ZhipuAI LLM creation in test mode")
    try:
        llm = get_llm(provider="zhipu", model="glm-4-flash", test_mode=True)
        logger.info("✓ Successfully created ZhipuAI LLM in test mode")
    except Exception as e:
        logger.error(f"✗ Failed to create ZhipuAI LLM in test mode: {e}")
        return False
    
    # Test 2: Test LLMFactory directly
    logger.info("\n2. Testing LLMFactory directly")
    try:
        llm_factory = LLMFactory()
        llm = llm_factory.create_zhipu_llm(model="glm-4", temperature=0.7, test_mode=True)
        logger.info("✓ Successfully created LLM via factory in test mode")
    except Exception as e:
        logger.error(f"✗ Failed to create LLM via factory: {e}")
        return False
    
    # Test 3: Test parameter passing
    logger.info("\n3. Testing parameter passing")
    try:
        llm = get_llm(
            provider="zhipu", 
            model="glm-4", 
            temperature=0.5, 
            test_mode=True
        )
        logger.info("✓ Parameters correctly passed to LLM")
    except Exception as e:
        logger.error(f"✗ Parameter passing test failed: {e}")
        return False
    
    logger.info("\n✅ All LLM utility tests passed!")
    return True

def test_llm_error_handling():
    """Test LLM utility error handling."""
    logger.info("\nTesting LLM utility error handling...")
    
    from utils.llm import get_llm
    
    # Test unsupported provider
    logger.info("1. Testing unsupported provider")
    try:
        llm = get_llm(provider="unsupported_provider", test_mode=True)
        logger.error("✗ Should have raised ValueError for unsupported provider")
        return False
    except ValueError as e:
        logger.info(f"✓ Correctly raised ValueError: {e}")
    except Exception as e:
        logger.error(f"✗ Wrong exception type raised: {e}")
        return False
    
    logger.info("✅ Error handling tests passed!")
    return True

if __name__ == "__main__":
    try:
        success1 = test_llm_creation()
        success2 = test_llm_error_handling()
        
        if success1 and success2:
            logger.info("\n🎉 All tests completed successfully!")
            sys.exit(0)
        else:
            logger.error("\n❌ Some tests failed!")
            sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)