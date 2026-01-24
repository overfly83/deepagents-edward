# Memory Management Implementation

This document describes the memory management implementation added to the deepagents-edward project.

## Features Implemented

### 1. MemoryMiddleware Integration
- **Files Modified**: `src/agents/weather/weather_agent.py`
- **Functionality**: Integrated `MemoryMiddleware` from the deepagents library with `FilesystemMiddleware` backend
- **Purpose**: Loads agent-specific memory from AGENTS.md files and injects it into the system prompt

### 2. Conversation History Management
- **Files Modified**: `src/agents/agent_manager.py`
- **Functionality**: Tracks conversation history per session ID
- **Key Features**:
  - Session ID generation and management
  - Storage of user and assistant messages
  - Context inclusion in messages sent to agents
  - Methods to get and clear conversation history

### 3. Enhanced Message Handling
- Both `handle_message` and `stream_handle_message` methods now:
  - Maintain conversation context across messages
  - Include recent conversation history (last 5 messages) in the prompt
  - Update the conversation history with each exchange

## Usage

### Conversation Context
When using the agent manager, conversations with the same session ID will maintain context:

```python
from agents.agent_manager import AgentManager

agent_manager = AgentManager()
session_id = "my-session"

# First message
response1 = agent_manager.handle_message("What's the weather in Beijing?", session_id)

# Follow-up message with context
response2 = agent_manager.handle_message("And tomorrow?", session_id)
```

### Managing Conversation History

```python
# Get conversation history
history = agent_manager.get_conversation_history(session_id)

# Clear conversation history
agent_manager.clear_conversation_history(session_id)
```

## Testing

### Pytest Tests
Run the memory management tests:
```bash
python -m pytest test/test_memory_management.py -v
```

### Manual Tests
- `test_conversation_history.py`: Direct testing of conversation history methods
- `test_memory_simple.py`: Simple test with logging

## Technical Details

### Memory Storage
- **Session-based storage**: Each conversation has its own history
- **In-memory storage**: Uses a dictionary `conversation_history` in the AgentManager
- **Limited context window**: Only the last 5 messages are included in the prompt for efficiency

### MemoryMiddleware Configuration
- **Backend**: `FilesystemMiddleware` for loading memory from AGENTS.md files
- **Sources**: Configured to load memory from the agent's directory

## Files Modified

1. **`src/agents/weather/weather_agent.py`**: Added MemoryMiddleware integration
2. **`src/agents/agent_manager.py`**: Added conversation history management
3. **`test/test_memory_management.py`**: Added pytest tests for memory functionality

## Benefits

- **Improved user experience**: Conversations feel more natural with context
- **Better agent performance**: Agents can reference previous messages
- **Scalable**: Session-based architecture allows multiple concurrent conversations
- **Maintainable**: Clean API for managing conversation history