"""Todo List Middleware for managing tasks within agent conversations."""

from typing import Dict, List, Optional, Any
from utils.logger import get_logger


class TodoListMiddleware:
    """Middleware for managing todo lists in agent conversations.
    
    This middleware provides functionality to add, remove, list, and update todo items
    in a conversation context. It can be integrated with agents without modifying their
    core implementation.
    """

    def __init__(self):
        """Initialize the Todo List Middleware with empty todo lists."""
        self.name = "todo_list_middleware"
        self.logger = get_logger(self.__class__.__name__, source=self.__class__.__name__)
        self.todo_lists: Dict[str, List[Dict[str, Any]]] = {}
        self.logger.info("TodoListMiddleware initialized")

    def add_todo(self, conversation_id: str, task: str, priority: str = "medium") -> Dict[str, Any]:
        """Add a new todo item to the conversation's todo list.
        
        Args:
            conversation_id: Unique identifier for the conversation
            task: The todo item description
            priority: Priority level (low, medium, high)
            
        Returns:
            The created todo item with id, task, priority, and status
        """
        # Ensure conversation has a todo list
        if conversation_id not in self.todo_lists:
            self.todo_lists[conversation_id] = []
            self.logger.info(f"Created new todo list for conversation: {conversation_id}")
        
        # Create new todo item
        todo_id = len(self.todo_lists[conversation_id]) + 1
        new_todo = {
            "id": todo_id,
            "task": task,
            "priority": priority.lower(),
            "status": "pending",
            "created_at": "now"
        }
        
        self.todo_lists[conversation_id].append(new_todo)
        self.logger.info(f"Added todo to conversation {conversation_id}: {task}")
        
        return new_todo

    def remove_todo(self, conversation_id: str, todo_id: int) -> bool:
        """Remove a todo item from the conversation's todo list.
        
        Args:
            conversation_id: Unique identifier for the conversation
            todo_id: The id of the todo item to remove
            
        Returns:
            True if the item was removed, False otherwise
        """
        if conversation_id not in self.todo_lists:
            return False
        
        original_length = len(self.todo_lists[conversation_id])
        self.todo_lists[conversation_id] = [
            todo for todo in self.todo_lists[conversation_id] 
            if todo["id"] != todo_id
        ]
        
        removed = len(self.todo_lists[conversation_id]) < original_length
        if removed:
            self.logger.info(f"Removed todo {todo_id} from conversation {conversation_id}")
        else:
            self.logger.warning(f"Todo {todo_id} not found in conversation {conversation_id}")
            
        return removed

    def update_todo(self, conversation_id: str, todo_id: int, **kwargs) -> Optional[Dict[str, Any]]:
        """Update a todo item in the conversation's todo list.
        
        Args:
            conversation_id: Unique identifier for the conversation
            todo_id: The id of the todo item to update
            **kwargs: Fields to update (task, priority, status)
            
        Returns:
            The updated todo item if found, None otherwise
        """
        if conversation_id not in self.todo_lists:
            return None
        
        for todo in self.todo_lists[conversation_id]:
            if todo["id"] == todo_id:
                # Update only valid fields
                valid_fields = ["task", "priority", "status"]
                for key, value in kwargs.items():
                    if key in valid_fields:
                        todo[key] = value.lower() if key in ["priority", "status"] else value
                
                self.logger.info(f"Updated todo {todo_id} in conversation {conversation_id}: {kwargs}")
                return todo
        
        self.logger.warning(f"Todo {todo_id} not found for update in conversation {conversation_id}")
        return None

    def list_todos(self, conversation_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all todo items for a conversation, optionally filtered by status.
        
        Args:
            conversation_id: Unique identifier for the conversation
            status: Optional filter by status (pending, completed)
            
        Returns:
            List of todo items
        """
        if conversation_id not in self.todo_lists:
            return []
        
        todos = self.todo_lists[conversation_id]
        
        if status:
            todos = [todo for todo in todos if todo["status"] == status.lower()]
        
        self.logger.info(f"Retrieved {len(todos)} todos for conversation {conversation_id}")
        return todos

    def clear_todos(self, conversation_id: str) -> bool:
        """Clear all todo items for a conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if the todo list was cleared, False otherwise
        """
        if conversation_id in self.todo_lists:
            self.todo_lists[conversation_id] = []
            self.logger.info(f"Cleared all todos for conversation {conversation_id}")
            return True
        
        return False

    # Required method for DeepAgents compatibility
    def wrap_tool_call(self, agent, tool_call, **kwargs):
        """Wrap tool call - required by DeepAgents."""
        return tool_call

    # Required async method for DeepAgents compatibility
    async def awrap_tool_call(self, agent, tool_call, **kwargs):
        """Async wrap tool call - required by DeepAgents."""
        return tool_call

    # Required method for DeepAgents compatibility
    def process_tool_call(self, agent, tool_call, **kwargs):
        """Process tool call - required by DeepAgents."""
        return tool_call

    # Required async method for DeepAgents compatibility
    async def aprocess_tool_call(self, agent, tool_call, **kwargs):
        """Async process tool call - required by DeepAgents."""
        return tool_call

    def process_message(self, conversation_id: str, message: str) -> Optional[Dict[str, Any]]:
        """Process user message for todo commands.
        
        Args:
            conversation_id: Unique identifier for the conversation
            message: User message to process
            
        Returns:
            Result of the todo command if detected, None otherwise
        """
        # This is a simple command detection - can be enhanced with NLP later
        message_lower = message.lower()
        
        if "add todo" in message_lower:
            # Extract task from message
            task = message_lower.replace("add todo", "").strip()
            if task:
                todo = self.add_todo(conversation_id, task)
                return {
                    "action": "add_todo",
                    "success": True,
                    "todo": todo,
                    "message": f"Added todo: {task}"
                }
        
        elif "list todos" in message_lower:
            todos = self.list_todos(conversation_id)
            return {
                "action": "list_todos",
                "success": True,
                "todos": todos,
                "count": len(todos)
            }
        
        elif "complete todo" in message_lower:
            try:
                # Extract todo ID
                todo_id = int(message_lower.split("complete todo")[1].strip())
                todo = self.update_todo(conversation_id, todo_id, status="completed")
                if todo:
                    return {
                        "action": "complete_todo",
                        "success": True,
                        "todo": todo,
                        "message": f"Completed todo {todo_id}"
                    }
            except (IndexError, ValueError):
                self.logger.warning(f"Invalid todo ID format in message: {message}")
                return {
                    "action": "complete_todo",
                    "success": False,
                    "message": "Please provide a valid todo ID"
                }
        
        elif "remove todo" in message_lower:
            try:
                # Extract todo ID
                todo_id = int(message_lower.split("remove todo")[1].strip())
                removed = self.remove_todo(conversation_id, todo_id)
                return {
                    "action": "remove_todo",
                    "success": removed,
                    "message": f"Removed todo {todo_id}" if removed else "Todo not found"
                }
            except (IndexError, ValueError):
                self.logger.warning(f"Invalid todo ID format in message: {message}")
                return {
                    "action": "remove_todo",
                    "success": False,
                    "message": "Please provide a valid todo ID"
                }
        
        # Return None if no todo command was detected
        return None