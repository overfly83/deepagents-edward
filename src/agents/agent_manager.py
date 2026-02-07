import uuid
from typing import Dict, List, Optional, Any, Tuple
from deepagents import create_deep_agent
from deepagents.backends import FilesystemBackend, CompositeBackend
from middleware.todo_list_middleware import TodoListMiddleware
from langchain_core.messages import HumanMessage

from utils.logger import get_logger
from utils.llm import get_llm
from tools.weather.weather_tools import get_current_weather, get_weather_forecast
from agents.weather.weather_agent import WeatherAgent

from deepagents.middleware.subagents import SubAgentMiddleware


logger = get_logger(__name__, source=__name__)


class AgentManager:
    """A generic agent manager built on DeepAgents framework with advanced capabilities:
    - Planning and task decomposition using todo lists
    - Context management with file system tools
    - Subagent spawning for specialized tasks
    - Long-term memory across sessions
    - Open intent detection not limited to specific agent intents
    """
    
    def __init__(self, model: str = "glm-4-flash", temperature: float = 0.1):
        """Initialize the AgentManager with DeepAgents framework and advanced capabilities."""
        
        # Initialize LLM for the agent manager
        self.llm = get_llm(provider="zhipu", model=model, temperature=temperature)
        
        # Initialize filesystem backend
        filesystem_backend = FilesystemBackend(root_dir=".agent_manager_filesystem")
        
        # Create CompositeBackend for handling different backend operations
        self.composite_backend = CompositeBackend(
            default=filesystem_backend,
            routes={
                "/memories/": filesystem_backend,
                "/files/": filesystem_backend
            }
        )
        
        # Initialize subagent middleware for spawning specialized agents
        self.subagent_middleware = SubAgentMiddleware(default_model=self.llm)
        
        # Initialize todo list middleware for planning capabilities
        self.todo_middleware = TodoListMiddleware()

        # Define available tools including weather tools and filesystem operations
        self.tools = [
            get_current_weather,
            get_weather_forecast
        ]
        
        # Initialize all available specialized agents
        self.agents: Dict[str, Any] = {
            "weather": WeatherAgent()
        }
        
        # System prompt for the generic agent manager
        self.system_prompt = """
        You are a helpful and capable agent manager. Your core capabilities include:
        
        1. Planning and Task Decomposition
        - Use the todo list system to break down complex tasks into discrete steps
        - Track progress and adapt plans as new information emerges
        - Use commands like: add todo, list todos, complete todo, update todo
        
        2. Context Management
        - Use file system tools (ls, read_file, write_file, edit_file) to manage context
        - Offload large context to memory to prevent context window overflow
        - Work with variable-length tool results efficiently
        
        3. Subagent Spawning
        - Use the task tool to spawn specialized subagents for specific tasks
        - Keep your context clean while delegating to experts
        - Examples: task("weather", "What's the weather in Beijing tomorrow?")
        
        5. Intent Detection
        - Analyze user messages to understand their intent
        - Determine if you can handle it directly or need to delegate to a specialized agent
        - Be flexible and don't limit yourself to predefined intents
        
        When users ask questions, first understand what they need, then decide on the best approach:
        - If it's a simple request you can handle directly, do so
        - If it's complex, break it down into steps using the todo list
        - If it requires specialized knowledge, spawn a subagent
        - If you need to work with files, use the filesystem tools
        - Always keep track of important information in memory
        
        Be conversational, helpful, and guide users through the process of achieving their goals.
        """
        
        # Convert agents dict to the format expected by deepagents (list of dicts with name, description, and system_prompt)
        formatted_subagents = []
        for name, agent in self.agents.items():
            # Extract the first line from system_prompt as description
            description = agent.system_prompt.split('\n')[0].strip()
            formatted_subagents.append({
                'name': name,
                'description': description,
                'system_prompt': agent.system_prompt
            })
        
        logger.debug(f"Formatted subagents: {formatted_subagents}")
        logger.debug(f"Type of formatted_subagents: {type(formatted_subagents)}")
        if formatted_subagents:
            logger.debug(f"First subagent type: {type(formatted_subagents[0])}")
            logger.debug(f"First subagent keys: {list(formatted_subagents[0].keys()) if isinstance(formatted_subagents[0], dict) else 'N/A'}")
        
        # Create the Deep Agent with all middleware and capabilities
        self.deep_agent = create_deep_agent(
            model=self.llm,
            system_prompt=self.system_prompt,
            subagents=formatted_subagents,
        )
        
        logger.info("AgentManager initialized with DeepAgents framework")
        logger.info("Enabled capabilities: Planning, Context Management, Subagent Spawning")

    def _format_todo_list(self, todos: List[Dict[str, Any]]) -> str:
        if not todos:
            return "No todo items yet."

        lines = []
        for todo in todos:
            todo_id = todo.get("id", "?")
            status = todo.get("status", "pending")
            task = todo.get("task", "")
            priority = todo.get("priority", "medium")
            lines.append(f"{todo_id}. [{status}] {task} ({priority})")

        return "\n".join(lines)

    
    def _process_message(self, message: str, session_id: str) -> dict:
        """Process the message and return the result.
        
        Args:
            message: The user's message.
            session_id: The session ID.
            
        Returns:
            The processed result as a dictionary.
        """
        try:
            # Step 2: Handle message using DeepAgents framework
            logger.info("Step 2: Processing with DeepAgents framework...")
            
            # Use the DeepAgent to process the message directly with correct input format
            response = self.deep_agent.invoke({"messages": [HumanMessage(content=message)]})
            
            logger.info("Step 3: DeepAgent response generated")
            logger.info(f"Final Result: {response[:100]}...")
            
            # Extract text from response dictionary if needed
            if isinstance(response, dict):
                response = response.get("output", response.get("content", str(response)))
            
            return {
                "response": response,
                "session_id": session_id
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            
            return {
                "response": f"I'm sorry, there was an error processing your request: {str(e)}",
                "error": str(e),
                "session_id": session_id
            }
    
    def handle_message(self, message: str, session_id: Optional[str] = None, return_steps: bool = False) -> Any:
        """Handle a user message using the DeepAgents framework with advanced capabilities.
        
        Args:
            message: The user's message.
            session_id: Optional session ID to maintain context.
            return_steps: Whether to return step-by-step updates as a generator.
            
        Returns:
            If return_steps is True: A generator yielding step-by-step updates.
            Otherwise: The response to the user's message as a dictionary.
        """
        logger.info(f"=== Starting DeepAgents Workflow ===")
        logger.info(f"User Message: {message}")
        
        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session ID: {session_id}")
        
        # Handle step-by-step mode
        if return_steps:
            return self._handle_message_with_steps(message, session_id)
        
        # Normal return mode
        final_result = self._process_message(message, session_id)
        logger.info(f"=== Workflow Completed ===")
        return final_result
        
    def _handle_message_with_steps(self, message: str, session_id: str) -> Generator[dict, None, None]:
        """Handle a message and return step-by-step updates as a generator.
        
        Args:
            message: The user's message.
            session_id: The session ID.
            
        Yields:
            Step-by-step updates as dictionaries.
        """
        # Step 1: Yield initialization
        yield {
            "step_number": 1,
            "step_name": "init",
            "step_description": "Initializing message processing",
            "type": "step",
            "debug": {"session_id": session_id, "message": message[:50] + "..."}
        }
        
        # Step 2: Yield processing start
        yield {
            "step_number": 2,
            "step_name": "deep_agent_processing",
            "step_description": "Processing message with DeepAgent",
            "type": "step",
            "debug": {"status": "started"}
        }
        
        # Process the message
        final_result = self._process_message(message, session_id)
        
        # Step 3: Yield completion
        yield {
            "step_number": 3,
            "step_name": "complete",
            "step_description": "Message processing complete",
            "type": "complete",
            "result": final_result
        }
        
    def stream_handle_message(self, message: str, session_id: Optional[str] = None):
        """Handle a user message and stream the response using the DeepAgents framework.
        
        Args:
            message: The user's message.
            session_id: Optional session ID to maintain context.
            
        Yields:
            Response chunks as dictionary objects with appropriate structure for the server.
        """
        logger.info(f"=== Starting DeepAgents Streaming Workflow ===")
        logger.info(f"User Message: {message}")
        
        # Generate a session ID if not provided
        if not session_id:
            session_id = str(uuid.uuid4())
            logger.info(f"Generated new session ID: {session_id}")
        
        try:
            todo_result = self.todo_middleware.process_message(session_id, message)
            todo_items = self.todo_middleware.list_todos(session_id)
            todo_text = self._format_todo_list(todo_items)
            if todo_result:
                todo_message = todo_result.get("message", "Updated todo list.")
                yield {
                    "type": "thought",
                    "content": f"{todo_message}\n{todo_text}"
                }
            else:
                yield {
                    "type": "thought",
                    "content": todo_text
                }

            # Stream response from the DeepAgent directly with correct input format
            full_response = ""
            for chunk in self.deep_agent.stream({"messages": [HumanMessage(content=message)]}):
                logger.debug(f"Raw chunk received: {chunk}")
                
                if isinstance(chunk, dict):
                    # Categorize the chunk based on its content
                    if any(key.endswith('.before_agent') or key.endswith('.after_agent') for key in chunk):
                        # This is a middleware thought/processing message
                        middleware_key = list(chunk.keys())[0]
                        thought_content = chunk[middleware_key]
                        if thought_content:
                            yield {
                                "type": "thought",
                                "content": f"{middleware_key}: {thought_content}"
                            }
                        else:
                            yield {
                                "type": "thought",
                                "content": todo_text
                            }
                    elif 'model' in chunk:
                        # This is a model response (could include tool calls)
                        model_data = chunk['model']
                        if 'messages' in model_data:
                            for msg in model_data['messages']:
                                if hasattr(msg, 'tool_calls') and msg.tool_calls:
                                    # This is a tool call message
                                    tool_call_info = []
                                    for tool_call in msg.tool_calls:
                                        if hasattr(tool_call, 'name') and hasattr(tool_call, 'args'):
                                            tool_call_info.append(f"{tool_call.name}({tool_call.args})")
                                    if tool_call_info:
                                        yield {
                                            "type": "tool_call",
                                            "content": f"Tool calls: {', '.join(tool_call_info)}"
                                        }
                                elif hasattr(msg, 'content') and msg.content:
                                    # This is a regular model response with content
                                    chunk_text = msg.content
                                    full_response += chunk_text
                                    yield {
                                        "type": "chunk",
                                        "content": chunk_text
                                    }
                    elif 'tools' in chunk:
                        # This is a tool response
                        tool_data = chunk['tools']
                        yield {
                            "type": "tool_response",
                            "content": f"Tool response: {tool_data}"
                        }
                    elif 'output' in chunk or 'content' in chunk:
                        # This is a direct output/content chunk
                        chunk_text = chunk.get("output", chunk.get("content", str(chunk)))
                        full_response += chunk_text
                        yield {
                            "type": "chunk",
                            "content": chunk_text
                        }
                    else:
                        # Fallback for other dictionary chunks
                        chunk_text = str(chunk)
                        full_response += chunk_text
                        yield {
                            "type": "chunk",
                            "content": chunk_text
                        }
                else:
                    # Fallback for non-dictionary chunks
                    chunk_text = str(chunk)
                    full_response += chunk_text
                    yield {
                        "type": "chunk",
                        "content": chunk_text
                    }
            
            logger.info(f"Step 3: Streaming completed")
            logger.info(f"Final Result: {full_response[:100]}...")
            
            # Yield final result message
            if full_response:
                yield {
                    "type": "result",
                    "content": full_response
                }
            
        except Exception as e:
            logger.error(f"Error streaming response: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            error_response = f"I'm sorry, there was an error processing your request: {str(e)}"
            
            # Yield error message
            yield {
                "type": "error",
                "content": error_response
            }
        
        logger.info(f"=== Streaming Workflow Completed ===")


    def get_available_agents(self) -> List[str]:
        """Get a list of available agents.
        
        Returns:
            A list of available agent names.
        """
        return list(self.agents.keys())


    def get_todos(self, session_id: str, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get the todo list for a session.
        
        Args:
            session_id: The session ID.
            status: Optional filter by status (pending, completed).
            
        Returns:
            List of todo items.
        """
        return self.todo_middleware.list_todos(session_id, status)
    
    def add_todo(self, session_id: str, task: str, priority: str = "medium") -> Dict[str, Any]:
        """Add a todo item to the session's todo list.
        
        Args:
            session_id: The session ID.
            task: The task description.
            priority: The priority level (low, medium, high).
            
        Returns:
            The created todo item.
        """
        return self.todo_middleware.add_todo(session_id, task, priority)
    
    def complete_todo(self, session_id: str, todo_id: str) -> bool:
        """Mark a todo item as completed.
        
        Args:
            session_id: The session ID.
            todo_id: The ID of the todo item to complete.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.todo_middleware.update_todo_status(session_id, todo_id, "completed")
    
    def update_todo(self, session_id: str, todo_id: str, task: Optional[str] = None, 
                   priority: Optional[str] = None, status: Optional[str] = None) -> bool:
        """Update a todo item.
        
        Args:
            session_id: The session ID.
            todo_id: The ID of the todo item to update.
            task: Optional updated task description.
            priority: Optional updated priority.
            status: Optional updated status.
            
        Returns:
            True if successful, False otherwise.
        """
        return self.todo_middleware.update_todo(session_id, todo_id, task, priority, status)
