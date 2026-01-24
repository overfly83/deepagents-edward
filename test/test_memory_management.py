#!/usr/bin/env python3
"""
Pytest test file for memory management functionality.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'src'))

import pytest
from agents.agent_manager import AgentManager

def test_conversation_history_initialization():
    """Test that conversation history is properly initialized."""
    agent_manager = AgentManager()
    session_id = "test-initialization"
    
    # Should return empty list for non-existent session
    history = agent_manager.get_conversation_history(session_id)
    assert history == []
    assert session_id not in agent_manager.conversation_history

def test_message_adding_to_history():
    """Test that messages are properly added to conversation history."""
    agent_manager = AgentManager()
    session_id = "test-message-adding"
    
    # Simulate what handle_message does internally
    if session_id not in agent_manager.conversation_history:
        agent_manager.conversation_history[session_id] = []
    
    # Add user message
    agent_manager.conversation_history[session_id].append(("user", "Hello world"))
    
    # Add assistant message
    agent_manager.conversation_history[session_id].append(("assistant", "Hi there!"))
    
    history = agent_manager.get_conversation_history(session_id)
    assert len(history) == 2
    assert history[0] == ("user", "Hello world")
    assert history[1] == ("assistant", "Hi there!")

def test_clear_conversation_history():
    """Test that conversation history can be cleared."""
    agent_manager = AgentManager()
    session_id = "test-clear-history"
    
    # Add some messages
    agent_manager.conversation_history[session_id] = [
        ("user", "First message"),
        ("assistant", "First response")
    ]
    
    # Verify history exists
    assert session_id in agent_manager.conversation_history
    
    # Clear history
    agent_manager.clear_conversation_history(session_id)
    
    # Verify history is cleared
    assert session_id not in agent_manager.conversation_history
    assert agent_manager.get_conversation_history(session_id) == []

def test_multiple_sessions():
    """Test that different sessions have separate conversation histories."""
    agent_manager = AgentManager()
    session1 = "test-session-1"
    session2 = "test-session-2"
    
    # Add messages to session 1
    agent_manager.conversation_history[session1] = [("user", "Message for session 1")]
    
    # Add messages to session 2
    agent_manager.conversation_history[session2] = [("user", "Message for session 2")]
    
    # Get histories
    history1 = agent_manager.get_conversation_history(session1)
    history2 = agent_manager.get_conversation_history(session2)
    
    # Verify they are different
    assert len(history1) == 1
    assert len(history2) == 1
    assert history1[0] != history2[0]
    assert history1[0][1] == "Message for session 1"
    assert history2[0][1] == "Message for session 2"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])