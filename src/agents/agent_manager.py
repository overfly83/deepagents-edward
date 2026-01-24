from typing import Dict, List, Optional, Any
from agents.agent_base import AgentBase
from agents.weather.weather_agent import WeatherAgent
import re
from utils.logger import get_logger

logger = get_logger(__name__, source=__name__)


class AgentManager:
    """Manages agents and handles intent detection and task dispatching."""
    
    def __init__(self):
        """Initialize the AgentManager with available agents."""
        # Initialize all available agents
        self.agents: Dict[str, AgentBase] = {
            "weather": WeatherAgent()
        }
        
        # Intent patterns for routing
        self.intent_patterns = {
            "weather_inquiry": [
                # English keywords
                r"weather",
                r"temperature",
                r"forecast",
                r"rain",
                r"sunny",
                r"cloudy",
                r"windy",
                r"storm",
                # Chinese keywords for weather (天气)
                r"天气",
                r"温度",
                r"预报",
                r"下雨",
                r"晴天",
                r"多云",
                r"有风",
                r"风暴",
                r"阴天",
                r"小雨",
                r"大雨",
                r"雪",
                r"雾霾"
            ]
        }
    
    def detect_intent(self, message: str) -> Optional[str]:
        """Detect the intent from a user message.
        
        Args:
            message: The user's message.
            
        Returns:
            The detected intent or None if no intent is detected.
        """
        message_lower = message.lower()
        
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, message_lower):
                    return intent
        
        return None
    
    def get_agent_for_intent(self, intent: str) -> Optional[AgentBase]:
        """Get the appropriate agent for a given intent.
        
        Args:
            intent: The detected intent.
            
        Returns:
            The appropriate agent or None if no agent handles the intent.
        """
        for agent_name, agent in self.agents.items():
            if intent in agent.get_supported_intents():
                return agent_name, agent
        
        return None
    
    def handle_message(self, message: str) -> Any:
        """Handle a user message by following the standard workflow:
        1. Detect user's intent
        2. Detect result

        4. Dispatch to appropriate agent with proper logging
        
        Args:
            message: The user's message.
        """
        logger.info(f"=== Starting Standard Workflow ===")
        logger.info(f"User Message: {message}")
        
        # Store result for final response
        final_result = None

        # Step 1: Detect user's intent
        intent = self.detect_intent(message)
        logger.info(f"Step 1: Intent detected: {intent}")

        if not intent:
            final_result = {
                "response": "I'm sorry, I don't understand what you're asking. Could you please rephrase?"
            }
            logger.warning("Result: No intent detected")
            # Intent detection failed
            logger.info(f"=== Workflow Complete ===")
            return final_result
        else:
            # Step 2: Looking for appropriate agent
            logger.info("Step 2: Looking for appropriate agent...")
            agent_name, agent = self.get_agent_for_intent(intent)
            
            if not agent:
                final_result = {
                    "response": f"I'm sorry, I don't have an agent that can handle '{intent}' requests."
                }
                logger.warning(f"Result: No agent found for intent '{intent}'")
                logger.info(f"=== Workflow Complete ===")
                return final_result
            
            logger.info(f"Step 2: Found agent: {agent_name}")

            # Step 3: Plan task
            logger.info("Step 3: Planning task...")
            agent.plan_task(message)

            # Step 4: Agent processing
            logger.info("Step 4: Processing with agent...")
            response = agent.chat(message)

            # Agent logs final result
            agent.log_final_result(response)
            final_result = {"response": response}
            logger.info("Step 4: Agent processing complete")
            return final_result

    def stream_handle_message(self, message: str):
        """Handle a user message by detecting intent and routing to the appropriate agent with streaming.
        
        Args:
            message: The user's message.
            
        Yields:
            Response chunks as they are generated.
        """
        # Step 1: Detecting intent
        logger.info("Step 1: Detecting user intent...")
        
        # Detect intent
        intent = self.detect_intent(message)
        
        if not intent:
            yield {"messages": [{"content": "I'm sorry, I don't understand what you're asking. Could you please rephrase?"}]}
            return
        
        logger.info(f"Step 1: Intent detected: {intent}")
        
        # Step 2: Looking for appropriate agent
        logger.info("Step 2: Looking for appropriate agent...")
        
        # Get the appropriate agent
        agent_name, agent = self.get_agent_for_intent(intent)
        
        if not agent:
            yield {"messages": [{"content": f"I'm sorry, I don't have an agent that can handle '{intent}' requests."}]}
            return
        
        logger.info(f"Step 2: Found agent: {agent_name}")
        
        # Step 3: Plan task
        logger.info("Step 3: Planning task...")
        agent.plan_task(message)
        
        # Step 4: Agent processing
        logger.info("Step 4: Processing with agent...")
        
        # Use the agent to get a streaming response
        for chunk in agent.stream_chat(message):
            yield chunk
        
        logger.info("Step 4: Processing with agent complete")
    
    async def run_agent(self, agent_name: str, *args, **kwargs) -> Dict[str, Any]:
        """Run a specific agent with provided parameters.
        
        Args:
            agent_name: The name of the agent to run.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.
            
        Returns:
            The result of the agent's execution as a dictionary.
        """
        if agent_name not in self.agents:
            return {"error": f"Agent '{agent_name}' not found."}
        
        agent = self.agents[agent_name]
        
        # Plan task if message is provided in args or kwargs
        message = args[0] if args else kwargs.get('message', '')
        if message:
            logger.info("Planning task...")
            agent.plan_task(message)
        
        return await agent.run(*args, **kwargs)
    
    def get_available_agents(self) -> List[str]:
        """Get a list of available agents.
        
        Returns:
            A list of available agent names.
        """
        return list(self.agents.keys())