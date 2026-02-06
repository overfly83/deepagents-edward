"""Short Term Memory implementation using DeepAgents FilesystemBackend."""

from typing import Dict, List, Tuple, Optional, Any
import json
import os
from utils.logger import get_logger
from deepagents.backends import FilesystemBackend


class ShortTermMemory:
    """Short-term memory for managing conversation history using DeepAgents FilesystemBackend.
    
    This class provides a temporary storage for conversation history that can be
    used by agents to maintain context during interactions. It automatically
    manages memory size by removing older entries when capacity is exceeded.
    """

    def __init__(self, capacity: int = 20):
        """Initialize Short Term Memory with a specified capacity.
        
        Args:
            capacity: Maximum number of message pairs to store per conversation
        """
        self.logger = get_logger(self.__class__.__name__, source=self.__class__.__name__)
        self.capacity = capacity
        
        # Initialize DeepAgents FilesystemBackend for storage
        self.backend = FilesystemBackend(root_dir=".short_term_memory")
        
        # Ensure conversation IDs file exists
        if not self.backend.read("conversation_ids.json"):
            self.backend.write("conversation_ids.json", json.dumps([]))
        
        self.logger.info(f"ShortTermMemory initialized with capacity: {capacity}")

    def add_message(self, conversation_id: str, role: str, content: str) -> None:
        """Add a message to the conversation memory.
        
        Args:
            conversation_id: Unique identifier for the conversation
            role: Role of the message sender (user, agent)
            content: Content of the message
        """
        try:
            # Get current messages for the conversation
            file_content = self.backend.read(f"{conversation_id}.json")
            try:
                messages = json.loads(file_content) if file_content else []
            except json.JSONDecodeError:
                self.logger.warning(f"Corrupt JSON file for conversation {conversation_id}, resetting memory")
                messages = []
            
            if not messages:
                self.logger.info(f"Created new memory entry for conversation: {conversation_id}")
                
                # Add conversation ID to the tracking list
                conv_ids_content = self.backend.read("conversation_ids.json")
                try:
                    conversation_ids = json.loads(conv_ids_content) if conv_ids_content else []
                except json.JSONDecodeError:
                    self.logger.warning("Corrupt conversation_ids.json file, resetting list")
                    conversation_ids = []
                if conversation_id not in conversation_ids:
                    conversation_ids.append(conversation_id)
                    self.backend.write("conversation_ids.json", json.dumps(conversation_ids))
            
            # Add the message to memory as a list (JSON doesn't support tuples)
            messages.append([role, content])
            
            # Enforce capacity by removing older entries if needed
            if len(messages) > self.capacity:
                removed_count = len(messages) - self.capacity
                messages = messages[removed_count:]
                self.logger.info(f"Trimmed {removed_count} messages from conversation {conversation_id}")
            
            # Save updated messages back to the backend
            self.backend.write(f"{conversation_id}.json", json.dumps(messages))
            self.logger.debug(f"Added message to conversation {conversation_id}: {role} - {content[:50]}...")
            
        except Exception as e:
            self.logger.error(f"Failed to add message to conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def get_memory(self, conversation_id: str, max_messages: Optional[int] = None) -> List[Tuple[str, str]]:
        """Retrieve conversation history for a given conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            max_messages: Maximum number of message pairs to retrieve (most recent first)
            
        Returns:
            List of (role, content) tuples representing the conversation history
        """
        try:
            file_content = self.backend.read(f"{conversation_id}.json")
            try:
                messages = json.loads(file_content) if file_content else []
            except json.JSONDecodeError:
                self.logger.warning(f"Corrupt JSON file for conversation {conversation_id}, returning empty memory")
                messages = []
            
            if not messages:
                self.logger.info(f"No memory found for conversation: {conversation_id}")
                return []
            
            if max_messages and max_messages < len(messages):
                result = messages[-max_messages:]
                self.logger.info(f"Retrieved last {max_messages} messages for conversation {conversation_id}")
            else:
                result = messages
                self.logger.info(f"Retrieved all {len(messages)} messages for conversation {conversation_id}")
            
            # Convert lists back to tuples for the API contract
            return [tuple(msg) for msg in result]
            
        except Exception as e:
            self.logger.error(f"Failed to get memory for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def get_last_message(self, conversation_id: str) -> Optional[Tuple[str, str]]:
        """Get the last message in the conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Last (role, content) tuple or None if no conversation found
        """
        try:
            file_content = self.backend.read(f"{conversation_id}.json")
            messages = json.loads(file_content) if file_content else []
            
            if messages:
                # Convert list back to tuple for the API contract
                return tuple(messages[-1])
            
            self.logger.info(f"No messages found for conversation: {conversation_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get last message for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def clear_memory(self, conversation_id: str) -> bool:
        """Clear all memory for a specific conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if memory was cleared, False otherwise
        """
        try:
            # Check if conversation exists
            file_content = self.backend.read(f"{conversation_id}.json")
            if file_content:
                # Clear the messages
                self.backend.write(f"{conversation_id}.json", json.dumps([]))
                
                # Remove conversation ID from the tracking list
                conv_ids_content = self.backend.read("conversation_ids.json")
                try:
                    conversation_ids = json.loads(conv_ids_content) if conv_ids_content else []
                except json.JSONDecodeError:
                    self.logger.warning("Corrupt conversation_ids.json file, resetting list")
                    conversation_ids = []
                if conversation_id in conversation_ids:
                    conversation_ids.remove(conversation_id)
                    self.backend.write("conversation_ids.json", json.dumps(conversation_ids))
                
                self.logger.info(f"Cleared memory for conversation: {conversation_id}")
                return True
            
            self.logger.warning(f"Attempted to clear memory for non-existent conversation: {conversation_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to clear memory for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def get_conversation_ids(self) -> List[str]:
        """Get all conversation IDs with stored memory.
        
        Returns:
            List of conversation IDs
        """
        try:
            conv_ids_content = self.backend.read("conversation_ids.json")
            try:
                return json.loads(conv_ids_content) if conv_ids_content else []
            except json.JSONDecodeError:
                self.logger.warning("Corrupt conversation_ids.json file, returning empty list")
                return []
        except Exception as e:
            self.logger.error(f"Failed to get conversation IDs: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def get_memory_size(self, conversation_id: str) -> int:
        """Get the current size of a conversation's memory.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Number of messages in memory for the conversation
        """
        try:
            file_content = self.backend.read(f"{conversation_id}.json")
            messages = json.loads(file_content) if file_content else []
            return len(messages)
        except Exception as e:
            self.logger.error(f"Failed to get memory size for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return 0

    def update_capacity(self, new_capacity: int) -> None:
        """Update the memory capacity and trim existing memories if needed.
        
        Args:
            new_capacity: New maximum number of message pairs per conversation
        """
        try:
            if new_capacity <= 0:
                self.logger.warning(f"Invalid capacity: {new_capacity}, using default value 20")
                new_capacity = 20
            
            old_capacity = self.capacity
            self.capacity = new_capacity
            
            if new_capacity < old_capacity:
                # Trim existing memories to new capacity
                conv_ids_content = self.backend.read("conversation_ids.json")
                try:
                    conversation_ids = json.loads(conv_ids_content) if conv_ids_content else []
                except json.JSONDecodeError:
                    self.logger.warning("Corrupt conversation_ids.json file, skipping memory trimming")
                    conversation_ids = []
                for conversation_id in conversation_ids:
                    file_content = self.backend.read(f"{conversation_id}.json")
                    try:
                        messages = json.loads(file_content) if file_content else []
                    except json.JSONDecodeError:
                        self.logger.warning(f"Corrupt JSON file for conversation {conversation_id}, skipping memory trimming")
                        messages = []
                    if len(messages) > new_capacity:
                        removed_count = len(messages) - new_capacity
                        messages = messages[-new_capacity:]
                        self.backend.write(f"{conversation_id}.json", json.dumps(messages))
                        self.logger.info(f"Trimmed {removed_count} messages from conversation {conversation_id} to new capacity")
            
            self.logger.info(f"Updated memory capacity to: {new_capacity}")
            
        except Exception as e:
            self.logger.error(f"Failed to update capacity: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")

    def to_prompt(self, conversation_id: str, max_messages: Optional[int] = None) -> str:
        """Convert conversation memory to a formatted prompt string.
        
        Args:
            conversation_id: Unique identifier for the conversation
            max_messages: Maximum number of message pairs to include
            
        Returns:
            Formatted prompt string with conversation history
        """
        try:
            messages = self.get_memory(conversation_id, max_messages)
            prompt_parts = []
            
            for role, content in messages:
                role_label = "User:" if role.lower() == "user" else "Agent:" if role.lower() == "agent" else role.capitalize() + ":"
                prompt_parts.append(f"{role_label} {content}")
            
            prompt = "\n".join(prompt_parts)
            self.logger.debug(f"Generated prompt from memory: {prompt[:100]}...")
            
            return prompt
        except Exception as e:
            self.logger.error(f"Failed to generate prompt for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return ""