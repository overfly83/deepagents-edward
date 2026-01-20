from abc import ABC, abstractmethod
from typing import Dict, Optional, Any, List
from utils.logger import get_logger


class AgentBase(ABC):
    """Base class for all agents, defining the required interface with task planning and action logging."""

    def __init__(self):
        """Initialize the agent with logging capabilities."""
        self.logger = get_logger(self.__class__.__name__, source=self.__class__.__name__)

    @abstractmethod
    def chat(self, message: str) -> str:
        """Send a message to the agent and get a response.
        
        Args:
            message: The user's message/question
            
        Returns:
            The agent's response
        """
        pass

    @abstractmethod
    def stream_chat(self, message: str):
        """Send a message to the agent and stream the response.
        
        Args:
            message: The user's message/question
            
        Yields:
            Response chunks as they are generated
        """
        pass

    @abstractmethod
    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        """Run the agent with specific parameters.
        
        Args:
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            The result of the agent's execution as a dictionary.
        """
        pass

    @abstractmethod
    def get_supported_intents(self) -> list[str]:
        """Get the list of intents supported by this agent.
        
        Returns:
            A list of supported intent strings.
        """
        pass

    def plan_task(self, message: str) -> Dict[str, Any]:
        """Plan the task based on the user's message.
        
        Args:
            message: The user's message/question
            
        Returns:
            A dictionary containing the task plan with steps.
        """
        plan = {
            "task": f"Process user request: {message[:50]}...",
            "steps": [
                "Analyze user input",
                "Determine required actions",
                "Execute actions",
                "Generate response"
            ]
        }
        self.logger.info(f"Task Plan: {plan}")
        return plan

    def log_action(self, action: str, result: Any) -> None:
        """Log an action and its result.
        
        Args:
            action: The action being performed
            result: The result of the action
        """
        self.logger.info(f"Action: {action}")
        self.logger.info(f"Result: {result}")

    def log_final_result(self, result: str) -> None:
        """Log the final result of the task.
        
        Args:
            result: The final result to log
        """
        self.logger.info(f"Final Result: {result}")