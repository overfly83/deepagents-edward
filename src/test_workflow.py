#!/usr/bin/env python3
"""
Test script in the src directory to verify the standard workflow implementation.
"""

import os
import sys

# Current directory is src, so imports should work directly
from agents.agent_manager import AgentManager

print("=== Testing Standard Workflow ===")

# Create an instance
agent_manager = AgentManager()
print("AgentManager initialized!")

# Test with a weather query
test_query = "What's the weather like in Beijing?"
print(f"\nProcessing query: {test_query}")

# Process the query
result = agent_manager.handle_message(test_query)

# Print results
print(f"\nResponse: {result['response']}")

if 'debug' in result:
    print(f"\nDebug Info:")
    for key, value in result['debug'].items():
        print(f"  {key}: {value}")

print("\n=== Test Complete ===")