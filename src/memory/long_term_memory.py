"""Long Term Memory implementation using DeepAgents FilesystemBackend."""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json
import os
from utils.logger import get_logger
from deepagents.backends import FilesystemBackend


class LongTermMemory:
    """Long-term memory for storing important conversation information persistently using DeepAgents FilesystemBackend.
    
    This class provides persistent storage capabilities for important conversation
    information that should be retained across sessions. It uses DeepAgents FilesystemBackend
    and supports structured data retrieval and organization.
    """

    def __init__(self, storage_path: str = ".long_term_memory"):
        """Initialize Long Term Memory with a specified storage path.
        
        Args:
            storage_path: Path where memory data will be stored persistently
        """
        self.logger = get_logger(self.__class__.__name__, source=self.__class__.__name__)
        
        # Initialize DeepAgents FilesystemBackend for persistent storage
        self.backend = FilesystemBackend(root_dir=storage_path)
        
        # Ensure metadata file exists
        if not self.backend.read("metadata.json"):
            self.backend.write("metadata.json", json.dumps({"conversation_ids": []}))
        
        self.logger.info(f"LongTermMemory initialized with storage path: {storage_path}")

    def store(self, conversation_id: str, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Store a piece of information in long-term memory.
        
        Args:
            conversation_id: Unique identifier for the conversation
            key: Key to identify the stored information
            value: The actual information to store
            metadata: Optional metadata about the stored information
            
        Returns:
            True if storage was successful, False otherwise
        """
        try:
            # Get existing conversation data or create new
            file_content = self.backend.read(f"{conversation_id}.json")
            conversation_data = json.loads(file_content) if file_content else {
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat(),
                "memory_items": {}
            }
            
            if not file_content:
                self.logger.info(f"Created new memory entry for conversation: {conversation_id}")
                
                # Update metadata with conversation ID
                metadata_content = self.backend.read("metadata.json")
                metadata_dict = json.loads(metadata_content)
                if conversation_id not in metadata_dict["conversation_ids"]:
                    metadata_dict["conversation_ids"].append(conversation_id)
                    self.backend.write("metadata.json", json.dumps(metadata_dict))
            
            # Create memory item
            memory_item = {
                "value": value,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            if metadata:
                memory_item["metadata"] = metadata
            
            # Store the item
            conversation_data["memory_items"][key] = memory_item
            conversation_data["updated_at"] = datetime.now().isoformat()
            
            # Persist to storage
            self.backend.write(f"{conversation_id}.json", json.dumps(conversation_data))
            
            self.logger.info(f"Stored memory item '{key}' for conversation {conversation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to store memory item for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def retrieve(self, conversation_id: str, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve a piece of information from long-term memory.
        
        Args:
            conversation_id: Unique identifier for the conversation
            key: Key to identify the stored information
            
        Returns:
            The memory item if found, None otherwise
        """
        try:
            file_content = self.backend.read(f"{conversation_id}.json")
            conversation_data = json.loads(file_content) if file_content else {}
            
            if "memory_items" in conversation_data and key in conversation_data["memory_items"]:
                self.logger.info(f"Retrieved memory item '{key}' for conversation {conversation_id}")
                return conversation_data["memory_items"][key]
            
            self.logger.info(f"Memory item '{key}' not found for conversation {conversation_id}")
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to retrieve memory item for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def update(self, conversation_id: str, key: str, value: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update an existing memory item.
        
        Args:
            conversation_id: Unique identifier for the conversation
            key: Key to identify the stored information
            value: The updated information
            metadata: Optional metadata to update (will merge with existing)
            
        Returns:
            True if update was successful, False otherwise
        """
        try:
            file_content = self.backend.read(f"{conversation_id}.json")
            conversation_data = json.loads(file_content) if file_content else {}
            
            if "memory_items" in conversation_data and key in conversation_data["memory_items"]:
                memory_item = conversation_data["memory_items"][key]
                memory_item["value"] = value
                memory_item["updated_at"] = datetime.now().isoformat()
                
                if metadata:
                    if "metadata" not in memory_item:
                        memory_item["metadata"] = {}
                    memory_item["metadata"].update(metadata)
                
                conversation_data["updated_at"] = datetime.now().isoformat()
                
                # Persist to storage
                self.backend.write(f"{conversation_id}.json", json.dumps(conversation_data))
                
                self.logger.info(f"Updated memory item '{key}' for conversation {conversation_id}")
                return True
            
            self.logger.warning(f"Cannot update non-existent memory item '{key}' for conversation {conversation_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to update memory item for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def delete(self, conversation_id: str, key: str) -> bool:
        """Delete a memory item.
        
        Args:
            conversation_id: Unique identifier for the conversation
            key: Key to identify the stored information
            
        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            file_content = self.backend.read(f"{conversation_id}.json")
            conversation_data = json.loads(file_content) if file_content else {}
            
            if "memory_items" in conversation_data and key in conversation_data["memory_items"]:
                del conversation_data["memory_items"][key]
                conversation_data["updated_at"] = datetime.now().isoformat()
                
                # Persist to storage
                self.backend.write(f"{conversation_id}.json", json.dumps(conversation_data))
                
                self.logger.info(f"Deleted memory item '{key}' for conversation {conversation_id}")
                return True
            
            self.logger.warning(f"Cannot delete non-existent memory item '{key}' for conversation {conversation_id}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to delete memory item for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def get_all_memory_items(self, conversation_id: str) -> Dict[str, Any]:
        """Retrieve all memory items for a conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Dictionary of all memory items for the conversation
        """
        try:
            file_content = self.backend.read(f"{conversation_id}.json")
            conversation_data = json.loads(file_content) if file_content else {}
            return conversation_data.get("memory_items", {})
        except Exception as e:
            self.logger.error(f"Failed to get all memory items for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {}

    def search(self, conversation_id: str, query: str) -> List[Dict[str, Any]]:
        """Search for memory items containing a specific query.
        
        Args:
            conversation_id: Unique identifier for the conversation
            query: Search term to look for in memory items
            
        Returns:
            List of memory items matching the search query
        """
        try:
            results = []
            memory_items = self.get_all_memory_items(conversation_id)
            
            # Simple keyword search in values and metadata
            for key, item in memory_items.items():
                # Check value
                if isinstance(item["value"], str) and query.lower() in item["value"].lower():
                    results.append(item)
                    continue
                
                # Check metadata if present
                if "metadata" in item:
                    for meta_key, meta_value in item["metadata"].items():
                        if isinstance(meta_value, str) and query.lower() in meta_value.lower():
                            results.append(item)
                            break
            
            self.logger.info(f"Found {len(results)} matching items for query '{query}' in conversation {conversation_id}")
            return results
            
        except Exception as e:
            self.logger.error(f"Failed to search memory for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def get_conversation_ids(self) -> List[str]:
        """Get all conversation IDs with long-term memory.
        
        Returns:
            List of conversation IDs
        """
        try:
            metadata_content = self.backend.read("metadata.json")
            metadata_dict = json.loads(metadata_content)
            return metadata_dict.get("conversation_ids", [])
        except Exception as e:
            self.logger.error(f"Failed to get conversation IDs: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []

    def clear_conversation(self, conversation_id: str) -> bool:
        """Clear all memory items for a specific conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            True if clearing was successful, False otherwise
        """
        try:
            # Check if conversation exists
            file_content = self.backend.read(f"{conversation_id}.json")
            if file_content:
                # Delete the conversation file
                self.backend.delete(f"{conversation_id}.json")
                
                # Update metadata
                metadata_content = self.backend.read("metadata.json")
                metadata_dict = json.loads(metadata_content)
                if conversation_id in metadata_dict["conversation_ids"]:
                    metadata_dict["conversation_ids"].remove(conversation_id)
                    self.backend.write("metadata.json", json.dumps(metadata_dict))
                
                self.logger.info(f"Cleared all memory items for conversation {conversation_id}")
                return True
            
            self.logger.warning(f"Conversation {conversation_id} not found in long-term memory")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to clear conversation memory {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return False

    def get_memory_stats(self) -> Dict[str, Any]:
        """Get statistics about the long-term memory usage.
        
        Returns:
            Dictionary containing memory statistics
        """
        try:
            conversation_ids = self.get_conversation_ids()
            total_items = 0
            
            for conv_id in conversation_ids:
                items = self.get_all_memory_items(conv_id)
                total_items += len(items)
            
            stats = {
                "total_conversations": len(conversation_ids),
                "total_memory_items": total_items
            }
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get memory stats: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return {"total_conversations": 0, "total_memory_items": 0}

    def get_conversation_metadata(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get metadata about a conversation's long-term memory.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            Dictionary with conversation memory metadata
        """
        try:
            file_content = self.backend.read(f"{conversation_id}.json")
            conversation_data = json.loads(file_content) if file_content else {}
            
            if conversation_data:
                return {
                    "created_at": conversation_data.get("created_at"),
                    "updated_at": conversation_data.get("updated_at"),
                    "item_count": len(conversation_data.get("memory_items", {}))
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Failed to get conversation metadata for {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return None

    def list_items(self, conversation_id: str) -> List[str]:
        """List all memory item keys for a conversation.
        
        Args:
            conversation_id: Unique identifier for the conversation
            
        Returns:
            List of memory item keys
        """
        try:
            memory_items = self.get_all_memory_items(conversation_id)
            return list(memory_items.keys())
        except Exception as e:
            self.logger.error(f"Failed to list memory items for conversation {conversation_id}: {e}")
            import traceback
            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return []