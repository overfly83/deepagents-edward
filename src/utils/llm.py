#!/usr/bin/env python3
"""
LLM utility module for abstracting LLM calls across the project.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Import LLM providers
from langchain_community.chat_models import ChatZhipuAI

# Import custom logger
from utils.logger import get_logger

logger = get_logger(__name__, source='LLM_UTIL')

# Load environment variables
load_dotenv()

class LLMFactory:
    """
    Factory class for creating different types of LLMs.
    """
    
    @staticmethod
    def create_zhipu_llm(
        model: str = "glm-4-flash",
        temperature: float = 0.0,
        api_key: Optional[str] = None,
        test_mode: bool = False
    ) -> ChatZhipuAI:
        """
        Create a ZhipuAI LLM instance.
        
        Args:
            model: The ZhipuAI model to use (default: glm-4-flash)
            temperature: The temperature for the model (default: 0.0)
            api_key: Optional API key to use (if not provided, will use ZHIPU_API_KEY from env)
            test_mode: If True, use a mock API key for testing
            
        Returns:
            A configured ChatZhipuAI instance
            
        Raises:
            ValueError: If API key is not provided and not found in environment variables
        """
        if test_mode:
            logger.info(f"Creating ZhipuAI LLM in test mode: {model}")
            return ChatZhipuAI(
                model=model,
                temperature=temperature,
                api_key="mock_api_key_for_testing"
            )
        
        # Get API key from provided parameter or environment variable
        zhipu_api_key = api_key or os.getenv("ZHIPU_API_KEY")
        
        if not zhipu_api_key:
            raise ValueError(
                "Error: ZHIPU_API_KEY not found in environment variables. "
                "Please set it in your .env file or provide it explicitly."
            )
        
        logger.info(f"Creating ZhipuAI LLM: {model}")
        return ChatZhipuAI(
            model=model,
            temperature=temperature,
            api_key=zhipu_api_key
        )

def get_llm(
    provider: str = "zhipu",
    model: str = "glm-4-flash",
    temperature: float = 0.0,
    api_key: Optional[str] = None,
    test_mode: bool = False,
    **kwargs
):
    """
    Get a configured LLM instance.
    
    Args:
        provider: The LLM provider to use (default: "zhipu")
        model: The model name to use (default: "glm-4-flash" for ZhipuAI)
        temperature: The temperature for the model (default: 0.0)
        api_key: Optional API key to use (if not provided, will use from environment)
        test_mode: If True, use mock API keys for testing
        **kwargs: Additional parameters for the specific LLM provider
        
    Returns:
        A configured LLM instance
        
    Raises:
        ValueError: If an unsupported LLM provider is specified
    """
    logger.info(f"Getting LLM: provider={provider}, model={model}")
    
    if provider.lower() == "zhipu":
        return LLMFactory.create_zhipu_llm(
            model=model,
            temperature=temperature,
            api_key=api_key,
            test_mode=test_mode,
            **kwargs
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")

def get_default_llm():
    """
    Get the default LLM instance configured for the project.
    
    Returns:
        A configured LLM instance
    """
    return get_llm()