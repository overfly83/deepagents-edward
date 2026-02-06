"""Example demonstrating how to integrate TodoListMiddleware, ShortTermMemory,
and LongTermMemory with the existing agent framework without modifying existing files.
"""

import uuid
from agents.agent_manager import AgentManager
from middleware.todo_list_middleware import TodoListMiddleware
from memory.short_term_memory import ShortTermMemory
from memory.long_term_memory import LongTermMemory
from utils.logger import get_logger


logger = get_logger(__name__, source=__name__)


def example_integration():
    """Example showing how to integrate new components with existing framework."""
    logger.info("Starting middleware and memory integration example")
    
    # Generate a unique conversation ID
    conversation_id = str(uuid.uuid4())
    logger.info(f"Generated conversation ID: {conversation_id}")
    
    # Initialize existing AgentManager
    agent_manager = AgentManager()
    
    # Initialize new components separately
    todo_middleware = TodoListMiddleware()
    short_term_memory = ShortTermMemory(capacity=10)
    long_term_memory = LongTermMemory()
    
    # Example 1: Using TodoListMiddleware
    logger.info("=== Example 1: Using TodoListMiddleware ===")
    
    # Process a todo list command
    todo_message = "add todo buy groceries"
    todo_result = todo_middleware.process_message(conversation_id, todo_message)
    
    if todo_result:
        logger.info(f"Todo command result: {todo_result}")
        
    # List todos
    todos = todo_middleware.list_todos(conversation_id)
    logger.info(f"Current todos: {todos}")
    
    # Example 2: Using ShortTermMemory for conversation context
    logger.info("\n=== Example 2: Using ShortTermMemory ===")
    
    # Add some conversation history
    short_term_memory.add_message(conversation_id, "user", "Hello, what's the weather like in Beijing?")
    short_term_memory.add_message(conversation_id, "agent", "Let me check the weather in Beijing for you.")
    
    # Get memory as prompt context
    prompt_context = short_term_memory.to_prompt(conversation_id)
    logger.info(f"Conversation context for prompt:\n{prompt_context}")
    
    # Example 3: Using LongTermMemory for persistent storage
    logger.info("\n=== Example 3: Using LongTermMemory ===")
    
    # Store user preferences
    long_term_memory.store(
        conversation_id=conversation_id,
        key="user_preferences",
        value={"location": "Beijing", "temperature_unit": "Celsius"},
        metadata={"type": "preferences", "importance": "high"}
    )
    
    # Retrieve user preferences
    preferences = long_term_memory.retrieve(conversation_id, "user_preferences")
    if preferences:
        logger.info(f"Retrieved user preferences: {preferences['value']}")
    
    # Example 4: Integrating all components in a conversation flow
    logger.info("\n=== Example 4: Complete Conversation Flow ===")
    
    # Simulate a complete conversation with integrated components
    conversation_history = [
        ("user", "Hi, what's the weather in Beijing tomorrow?"),
        ("agent", "I'll check the weather for you.")
    ]
    
    for role, message in conversation_history:
        # Add to short-term memory for context
        short_term_memory.add_message(conversation_id, role, message)
        
        # Process through middleware if it's a user message
        if role == "user":
            # Check if it's a todo command
            todo_result = todo_middleware.process_message(conversation_id, message)
            
            if todo_result:
                # Handle todo command
                logger.info(f"Middleware handled todo command: {todo_result['message']}")
            else:
                # Let agent manager handle it
                logger.info(f"Passing to AgentManager: {message}")
                
                # Get intent
                intent = agent_manager.detect_intent(message)
                logger.info(f"Detected intent: {intent}")
                
                # Get conversation context from short-term memory
                context = short_term_memory.to_prompt(conversation_id)
                
                # Here you would typically call the appropriate agent
                # with the context
                
    # Example 5: Saving conversation summary to long-term memory
    logger.info("\n=== Example 5: Saving Conversation Summary ===")
    
    conversation_summary = {
        "conversation_id": conversation_id,
        "intent_count": 1,
        "todo_items": len(todo_middleware.list_todos(conversation_id)),
        "messages_exchanged": short_term_memory.get_memory_size(conversation_id)
    }
    
    long_term_memory.store(
        conversation_id=conversation_id,
        key="conversation_summary",
        value=conversation_summary,
        metadata={"type": "summary", "timestamp": "2024-01-01T12:00:00Z"}
    )
    
    # Example 6: Retrieving all memory for a conversation
    logger.info("\n=== Example 6: Retrieving All Memory ===")
    
    logger.info(f"Short-term memory messages: {short_term_memory.get_memory_size(conversation_id)}")
    logger.info(f"Long-term memory items: {long_term_memory.list_items(conversation_id)}")
    logger.info(f"Todo items: {len(todo_middleware.list_todos(conversation_id))}")
    
    logger.info("\n=== Integration Example Complete ===")
    
    # Clean up
    short_term_memory.clear_memory(conversation_id)
    long_term_memory.clear_conversation(conversation_id)
    todo_middleware.clear_todos(conversation_id)
    
    logger.info("Cleaned up all memory and todos")


if __name__ == "__main__":
    try:
        example_integration()
    except Exception as e:
        logger.error(f"Error in example integration: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")