"""Test file for TodoListMiddleware, ShortTermMemory, and LongTermMemory components."""

import uuid
import os
import pytest
from middleware.todo_list_middleware import TodoListMiddleware
from memory.short_term_memory import ShortTermMemory
from memory.long_term_memory import LongTermMemory


class TestTodoListMiddleware:
    """Test cases for TodoListMiddleware."""
    
    def test_add_todo(self):
        """Test adding a todo item."""
        middleware = TodoListMiddleware()
        conversation_id = str(uuid.uuid4())
        
        todo = middleware.add_todo(conversation_id, "Buy groceries")
        
        assert todo["id"] == 1
        assert todo["task"] == "Buy groceries"
        assert todo["priority"] == "medium"
        assert todo["status"] == "pending"
    
    def test_remove_todo(self):
        """Test removing a todo item."""
        middleware = TodoListMiddleware()
        conversation_id = str(uuid.uuid4())
        
        # Add a todo first
        middleware.add_todo(conversation_id, "Buy groceries")
        
        # Remove the todo
        result = middleware.remove_todo(conversation_id, 1)
        
        assert result is True
        
        # Verify it's gone
        todos = middleware.list_todos(conversation_id)
        assert len(todos) == 0
    
    def test_update_todo(self):
        """Test updating a todo item."""
        middleware = TodoListMiddleware()
        conversation_id = str(uuid.uuid4())
        
        # Add a todo first
        middleware.add_todo(conversation_id, "Buy groceries")
        
        # Update the todo
        updated_todo = middleware.update_todo(conversation_id, 1, status="completed", priority="high")
        
        assert updated_todo["status"] == "completed"
        assert updated_todo["priority"] == "high"
    
    def test_list_todos(self):
        """Test listing todo items."""
        middleware = TodoListMiddleware()
        conversation_id = str(uuid.uuid4())
        
        # Add multiple todos
        middleware.add_todo(conversation_id, "Buy groceries", "high")
        middleware.add_todo(conversation_id, "Do laundry", "medium")
        middleware.add_todo(conversation_id, "Clean house", "low")
        
        # List all todos
        todos = middleware.list_todos(conversation_id)
        
        assert len(todos) == 3
        
        # List only pending todos
        pending_todos = middleware.list_todos(conversation_id, "pending")
        assert len(pending_todos) == 3
        
        # Update one todo to completed
        middleware.update_todo(conversation_id, 1, status="completed")
        
        # List only completed todos
        completed_todos = middleware.list_todos(conversation_id, "completed")
        assert len(completed_todos) == 1
    
    def test_clear_todos(self):
        """Test clearing all todos."""
        middleware = TodoListMiddleware()
        conversation_id = str(uuid.uuid4())
        
        # Add multiple todos
        middleware.add_todo(conversation_id, "Buy groceries")
        middleware.add_todo(conversation_id, "Do laundry")
        
        # Clear all todos
        result = middleware.clear_todos(conversation_id)
        
        assert result is True
        
        # Verify all are gone
        todos = middleware.list_todos(conversation_id)
        assert len(todos) == 0
    
    def test_process_message_add_todo(self):
        """Test processing a message to add a todo."""
        middleware = TodoListMiddleware()
        conversation_id = str(uuid.uuid4())
        
        # Process a message to add a todo
        result = middleware.process_message(conversation_id, "add todo buy groceries")
        
        assert result["action"] == "add_todo"
        assert result["success"] is True
        assert "buy groceries" in result["todo"]["task"]
    
    def test_process_message_list_todos(self):
        """Test processing a message to list todos."""
        middleware = TodoListMiddleware()
        conversation_id = str(uuid.uuid4())
        
        # Add a todo first
        middleware.add_todo(conversation_id, "Buy groceries")
        
        # Process a message to list todos
        result = middleware.process_message(conversation_id, "list todos")
        
        assert result["action"] == "list_todos"
        assert result["success"] is True
        assert result["count"] == 1


class TestShortTermMemory:
    """Test cases for ShortTermMemory."""
    
    def test_add_message(self):
        """Test adding a message to memory."""
        memory = ShortTermMemory(capacity=2)
        conversation_id = str(uuid.uuid4())
        
        memory.add_message(conversation_id, "user", "Hello")
        memory.add_message(conversation_id, "agent", "Hi there!")
        
        stored_memory = memory.get_memory(conversation_id)
        
        assert len(stored_memory) == 2
        assert stored_memory[0] == ("user", "Hello")
        assert stored_memory[1] == ("agent", "Hi there!")
    
    def test_memory_capacity(self):
        """Test that memory respects capacity limits."""
        memory = ShortTermMemory(capacity=2)
        conversation_id = str(uuid.uuid4())
        
        # Add more messages than capacity
        memory.add_message(conversation_id, "user", "Message 1")
        memory.add_message(conversation_id, "agent", "Response 1")
        memory.add_message(conversation_id, "user", "Message 2")
        memory.add_message(conversation_id, "agent", "Response 2")
        
        stored_memory = memory.get_memory(conversation_id)
        
        # Should only have the last 2 messages
        assert len(stored_memory) == 2
        assert stored_memory[0] == ("user", "Message 2")
        assert stored_memory[1] == ("agent", "Response 2")
    
    def test_get_last_message(self):
        """Test getting the last message."""
        memory = ShortTermMemory()
        conversation_id = str(uuid.uuid4())
        
        memory.add_message(conversation_id, "user", "Hello")
        memory.add_message(conversation_id, "agent", "Hi there!")
        
        last_message = memory.get_last_message(conversation_id)
        
        assert last_message == ("agent", "Hi there!")
    
    def test_clear_memory(self):
        """Test clearing memory."""
        memory = ShortTermMemory()
        conversation_id = str(uuid.uuid4())
        
        memory.add_message(conversation_id, "user", "Hello")
        
        # Clear memory
        result = memory.clear_memory(conversation_id)
        
        assert result is True
        
        # Verify it's empty
        stored_memory = memory.get_memory(conversation_id)
        assert len(stored_memory) == 0
    
    def test_to_prompt(self):
        """Test converting memory to prompt format."""
        memory = ShortTermMemory()
        conversation_id = str(uuid.uuid4())
        
        memory.add_message(conversation_id, "user", "Hello")
        memory.add_message(conversation_id, "agent", "Hi there!")
        
        prompt = memory.to_prompt(conversation_id)
        
        assert "User: Hello" in prompt
        assert "Agent: Hi there!" in prompt


class TestLongTermMemory:
    """Test cases for LongTermMemory."""
    
    def setup_method(self):
        """Setup method to create a fresh memory instance for each test."""
        # Use a temporary storage path for tests
        self.temp_storage = "~/.deepagents/test_long_term_memory"
        self.memory = LongTermMemory(storage_path=self.temp_storage)
    
    def teardown_method(self):
        """Teardown method to clean up test storage."""
        # Clean up the temporary storage
        storage_path = os.path.expanduser(self.temp_storage)
        if os.path.exists(storage_path):
            for filename in os.listdir(storage_path):
                os.remove(os.path.join(storage_path, filename))
            os.rmdir(storage_path)
    
    def test_store_and_retrieve(self):
        """Test storing and retrieving a memory item."""
        conversation_id = str(uuid.uuid4())
        
        # Store an item
        result = self.memory.store(
            conversation_id=conversation_id,
            key="user_preferences",
            value={"location": "Beijing", "temperature_unit": "Celsius"}
        )
        
        assert result is True
        
        # Retrieve the item
        retrieved = self.memory.retrieve(conversation_id, "user_preferences")
        
        assert retrieved is not None
        assert retrieved["value"] == {"location": "Beijing", "temperature_unit": "Celsius"}
    
    def test_update(self):
        """Test updating a memory item."""
        conversation_id = str(uuid.uuid4())
        
        # Store an item first
        self.memory.store(
            conversation_id=conversation_id,
            key="user_preferences",
            value={"location": "Beijing"}
        )
        
        # Update the item
        result = self.memory.update(
            conversation_id=conversation_id,
            key="user_preferences",
            value={"location": "Beijing", "temperature_unit": "Celsius"}
        )
        
        assert result is True
        
        # Verify the update
        retrieved = self.memory.retrieve(conversation_id, "user_preferences")
        assert retrieved["value"]["temperature_unit"] == "Celsius"
    
    def test_delete(self):
        """Test deleting a memory item."""
        conversation_id = str(uuid.uuid4())
        
        # Store an item first
        self.memory.store(
            conversation_id=conversation_id,
            key="user_preferences",
            value={"location": "Beijing"}
        )
        
        # Delete the item
        result = self.memory.delete(conversation_id, "user_preferences")
        
        assert result is True
        
        # Verify it's gone
        retrieved = self.memory.retrieve(conversation_id, "user_preferences")
        assert retrieved is None
    
    def test_list_items(self):
        """Test listing all memory items."""
        conversation_id = str(uuid.uuid4())
        
        # Store multiple items
        self.memory.store(conversation_id, "item1", "value1")
        self.memory.store(conversation_id, "item2", "value2")
        self.memory.store(conversation_id, "item3", "value3")
        
        # List all items
        items = self.memory.list_items(conversation_id)
        
        assert len(items) == 3
        assert "item1" in items
        assert "item2" in items
        assert "item3" in items
    
    def test_clear_conversation(self):
        """Test clearing all memory for a conversation."""
        conversation_id = str(uuid.uuid4())
        
        # Store an item first
        self.memory.store(conversation_id, "item1", "value1")
        
        # Clear the conversation
        result = self.memory.clear_conversation(conversation_id)
        
        assert result is True
        
        # Verify it's gone
        items = self.memory.list_items(conversation_id)
        assert len(items) == 0


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])