from typing import Dict, List, Optional, Any
from agents.agent_base import AgentBase
from agents.weather.weather_agent import WeatherAgent
import os
from dotenv import load_dotenv
from utils.logger import get_logger
from langchain_community.chat_models import ChatZhipuAI

logger = get_logger(__name__, source=__name__)


class AgentManager:
    """Manages agents and handles intent detection and task dispatching."""
    
    def __init__(self):
        """Initialize the AgentManager with available agents."""
        # Load environment variables
        load_dotenv(os.path.join(os.path.dirname(__file__), "..", "..", ".env"))
        
        # Initialize LLM for intent detection
        self._initialize_llm()
        
        # Initialize all available agents
        self.agents: Dict[str, AgentBase] = {
            "weather": WeatherAgent()
        }
        
        # Get all supported intents from agents
        self.supported_intents = self._get_all_supported_intents()
        
        logger.info(f"AgentManager initialized with supported intents: {self.supported_intents}")
    
    def _initialize_llm(self):
        """Initialize the LLM for intent detection."""
        try:
            # Get API key from environment
            zhipu_api_key = os.getenv("ZHIPU_API_KEY")
            if not zhipu_api_key:
                logger.error("Error: ZHIPU_API_KEY not found in environment variables. Please set it in your .env file.")
                # Fallback to pattern matching if API key is missing
                self.llm_available = False
                logger.warning("Falling back to pattern-based intent detection")
                return
            
            # Initialize ChatZhipuAI for intent detection
            self.llm = ChatZhipuAI(
                model="glm-4-flash",
                temperature=0,
                api_key=zhipu_api_key
            )
            
            self.llm_available = True
            logger.info("LLM initialized for intent detection")
        except Exception as e:
            logger.error(f"Failed to initialize LLM: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Fallback to pattern matching if LLM fails
            self.llm_available = False
            logger.warning("Falling back to pattern-based intent detection")
    
    def _get_all_supported_intents(self) -> List[str]:
        """Get all supported intents from all available agents.
        
        Returns:
            List of all supported intents.
        """
        all_intents = set()
        for agent in self.agents.values():
            intents = agent.get_supported_intents()
            all_intents.update(intents)
        return list(all_intents)
    
    def detect_intent(self, message: str) -> Optional[str]:
        """Detect the intent from a user message using LLM.
        
        Args:
            message: The user's message.
            
        Returns:
            The detected intent or None if no intent is detected.
        """
        if not message:
            return None
        
        # Check if LLM is available
        if not self.llm_available:
            logger.info(f"Using fallback intent detection for message: {message}")
            return self._fallback_intent_detection(message)
        
        try:
            # Create a prompt for intent detection
            prompt = f"""
            You are an intent detection system. Your task is to determine the intent of the user's message.
            
            Available intents:
            {', '.join(self.supported_intents)}
            
            If the message doesn't match any of the above intents, return 'None'.
            
            User message: {message}
            
            Only return the intent name, nothing else.
            """
            
            logger.debug(f"Sending prompt to LLM: {prompt[:100]}...")
            
            # Get response from LLM
            response = self.llm.invoke(prompt)
            detected_intent = response.content.strip()
            
            logger.info(f"LLM intent detection - Message: {message}, Detected Intent: {detected_intent}")
            
            # Validate the detected intent
            if detected_intent in self.supported_intents:
                return detected_intent
            elif detected_intent.lower() == "none":
                return None
            else:
                logger.warning(f"LLM returned unknown intent: {detected_intent}, falling back to keyword matching")
                return self._fallback_intent_detection(message)
                
        except Exception as e:
            logger.error(f"Error during intent detection: {e}")
            logger.error(f"Error type: {type(e).__name__}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            # Fallback to basic keyword matching for robustness
            return self._fallback_intent_detection(message)
    
    def _fallback_intent_detection(self, message: str) -> Optional[str]:
        """Fallback intent detection using simple keyword matching.
        
        Args:
            message: The user's message.
            
        Returns:
            The detected intent or None if no intent is detected.
        """
        message_lower = message.lower()
        
        # Basic keyword matching as fallback
        intent_keywords = {
            "weather_inquiry": [
                "weather", "temperature", "forecast", "rain", "sunny", "cloudy", "windy", "storm",
                "天气", "温度", "预报", "下雨", "晴天", "多云", "有风", "风暴", "阴天", "小雨", "大雨", "雪", "雾霾"
            ]
        }
        
        for intent, keywords in intent_keywords.items():
            for keyword in keywords:
                if keyword in message_lower:
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