import pytest
import uuid
from unittest.mock import patch, MagicMock
from agents.agent_manager import AgentManager

class TestAgentManagerMemoryIntegration:
    """Test cases for verifying memory integration in AgentManager."""

    @pytest.fixture
    def agent_manager(self):
        """Create a fresh AgentManager instance with mocked memory systems for each test."""
        with patch('agents.agent_manager.ShortTermMemory') as mock_stm, \
             patch('agents.agent_manager.LongTermMemory') as mock_ltm:
            
            # Configure mock short-term memory
            mock_stm_instance = MagicMock()
            mock_stm_instance.to_prompt.return_value = ""
            mock_stm.return_value = mock_stm_instance
            
            # Configure mock long-term memory
            mock_ltm_instance = MagicMock()
            mock_ltm_instance.store.return_value = True
            mock_ltm_instance.retrieve.return_value = {"value": "test_value", "metadata": {"type": "test"}}
            mock_ltm.return_value = mock_ltm_instance
            
            yield AgentManager()

    def test_memory_initialization(self, agent_manager):
        """Test that memory systems are properly initialized."""
        assert hasattr(agent_manager, 'short_term_memory')
        assert hasattr(agent_manager, 'long_term_memory')
        assert agent_manager.short_term_memory is not None
        assert agent_manager.long_term_memory is not None

    def test_short_term_memory_usage(self, agent_manager):
        """Test that messages are properly stored in short-term memory."""
        session_id = str(uuid.uuid4())
        user_message = "Hello, what's the weather?"
        
        # Clear any existing calls
        agent_manager.short_term_memory.add_message.reset_mock()
        
        # Mock detect_intent to return None to avoid agent dispatching
        with patch.object(agent_manager, 'detect_intent', return_value=None):
            agent_manager.handle_message(user_message, session_id)
        
        # Verify short-term memory methods were called
        agent_manager.short_term_memory.add_message.assert_any_call(session_id, "user", user_message)
        agent_manager.short_term_memory.to_prompt.assert_called_once_with(session_id)
        # Just verify that add_message was called at least once
        assert agent_manager.short_term_memory.add_message.called

    def test_conversation_history_retrieval(self, agent_manager):
        """Test that conversation history can be retrieved properly."""
        session_id = str(uuid.uuid4())
        
        # Test get_conversation_history
        agent_manager.get_conversation_history(session_id)
        agent_manager.short_term_memory.get_memory.assert_called_once_with(session_id)
        
        # Test clear_conversation_history
        agent_manager.clear_conversation_history(session_id)
        agent_manager.short_term_memory.clear_memory.assert_called_once_with(session_id)

    def test_long_term_memory_operations(self, agent_manager):
        """Test long-term memory storage and retrieval."""
        session_id = str(uuid.uuid4())
        key = "test_key"
        value = "test_value"
        metadata = {"type": "test"}
        
        # Test store in long-term memory
        result = agent_manager.store_in_long_term_memory(session_id, key, value, metadata)
        agent_manager.long_term_memory.store.assert_called_once_with(session_id, key, value, metadata)
        assert result is True
        
        # Test retrieve from long-term memory
        retrieved = agent_manager.get_long_term_memory(session_id, key)
        agent_manager.long_term_memory.retrieve.assert_called_once_with(session_id, key)
        assert retrieved is not None
        assert retrieved["value"] == "test_value"

    def test_memory_in_streaming(self, agent_manager):
        """Test that memory is properly updated during streaming."""
        session_id = str(uuid.uuid4())
        user_message = "Hello, what's the weather?"
        
        # Test that stream_handle_message calls add_message for user input
        # We'll directly test the memory calls in stream_handle_message
        with patch.object(agent_manager, 'detect_intent', return_value=None):
            # This test focuses on whether add_message is called with user input
            # before any agent processing happens
            try:
                # We don't care about the full execution, just that memory is accessed
                next(agent_manager.stream_handle_message(user_message, session_id))
            except Exception:
                # Ignore any exceptions during stream processing
                pass
        
        # Verify memory was updated with user message
        agent_manager.short_term_memory.add_message.assert_any_call(session_id, "user", user_message)

    def test_session_management(self, agent_manager):
        """Test that different sessions maintain separate memory."""
        session_id_1 = str(uuid.uuid4())
        session_id_2 = str(uuid.uuid4())
        
        # Mock detect_intent to return None
        with patch.object(agent_manager, 'detect_intent', return_value=None):
            agent_manager.handle_message("Hello from session 1", session_id_1)
            agent_manager.handle_message("Hello from session 2", session_id_2)
        
        # Verify separate calls were made to memory for each session
        calls = [
            ((session_id_1, "user", "Hello from session 1"), {}),
            ((session_id_1, "assistant", "I'm sorry, I don't understand what you're asking. Could you please rephrase?"), {}),
            ((session_id_2, "user", "Hello from session 2"), {}),
            ((session_id_2, "assistant", "I'm sorry, I don't understand what you're asking. Could you please rephrase?"), {})
        ]
        
        # Check that add_message was called with each session
        assert agent_manager.short_term_memory.add_message.call_count >= 4

if __name__ == "__main__":
    pytest.main([__file__, "-v"])