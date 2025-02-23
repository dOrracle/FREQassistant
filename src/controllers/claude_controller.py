import logging
import json
import os
from typing import Dict, Any, Optional
from anthropic import Anthropic

logger = logging.getLogger(__name__)

class APIError(Exception):
    """Custom exception for API related errors"""
    pass

class ClaudeFreqAIController:
    """
    Controller class to integrate Claude with FreqTrade/FreqAI functionality
    """
    STRATEGY_TEMPLATE = """
    Create a complete FreqTrade trading strategy:
    {description}

    Requirements:
    1. Valid FreqTrade strategy class
    2. Proper indicator configuration
    3. Entry/exit signals
    4. Risk management parameters
    5. Hyperopt space definition

    Return ONLY executable Python code.
    """
    
    CONFIG_TEMPLATE = """
    Modify FreqTrade configuration:
    {request}

    Current config:
    {current_config}

    Return ONLY valid JSON for config changes.
    """

    BACKTEST_TEMPLATE = """
    Convert this backtest request into FreqTrade CLI arguments:
    {request}

    Return ONLY the argument string.
    """

    def __init__(self, config: Dict[str, Any], client: Anthropic):
        self.config = config
        self.client = client

        # Initialize with system prompt
        self.system_prompt = """You are an AI assistant specialized in managing and optimizing the FreqTrade cryptocurrency trading bot platform. Your core function is to serve as an intelligent interface between users and the FreqTrade system, translating natural language requests into concrete actions and providing expert guidance on trading strategies, configuration, and system management."""
        
        # Set default parameters
        self.model_version = config['claude_integration'].get('model_version', "claude-3-5-sonnet-latest")
        self.max_tokens = config['claude_integration'].get('max_tokens', 8192)
        self.temperature = config['claude_integration'].get('temperature', 1)

        self.base_config_path = "config.json"
        self.conversation_history = []
        self.current_metrics = {"accuracy": 0.0, "loss": 0.0}

    async def _call_claude_api(self, messages: list) -> str:
        try:
            response = await self.client.messages.create(
                model=self.model_version,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                system=self.system_prompt,
                messages=messages
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Claude API call failed: {str(e)}", exc_info=True)
            raise

    async def handle_command(self, user_input: str) -> str:
        """
        Process natural language commands and convert to FreqTrade actions
        """
        try:
            logger.info(f"Processing command: {user_input}")
            response = await self._call_claude_api([{
                "role": "user", 
                "content": f"Convert this FreqTrade command to specific action: {user_input}"
            }])
            
            command_type = self._parse_command_type(response)
            
            handlers = {
                "modify_config": self._handle_config_modification,
                "strategy": self._handle_strategy_command,
                "backtest": self._handle_backtest,
                "bot_control": self._handle_bot_control
            }
            
            handler = handlers.get(command_type)
            if handler:
                return await handler(user_input)
            return f"Unsupported command type: {command_type}"
                
        except Exception as e:
            logger.error(f"Command failed: {str(e)}", exc_info=True)
            return f"Error processing command: {str(e)}"

    async def _handle_config_modification(self, user_input: str) -> str:
        try:
            response = await self._call_claude_api([{
                "role": "user",
                "content": f"Convert this config modification request to specific JSON changes: {user_input}"
            }])
            
            config_changes = json.loads(response)
            
            with open(self.base_config_path, 'r') as f:
                current_config = json.load(f)
                
            self._update_nested_dict(current_config, config_changes)
            
            backup_path = f"{self.base_config_path}.backup"
            os.rename(self.base_config_path, backup_path)
            
            with open(self.base_config_path, 'w') as f:
                json.dump(current_config, f, indent=4)
                
            return "Configuration updated successfully"
            
        except Exception as e:
            logger.error(f"Config modification failed: {str(e)}", exc_info=True)
            return f"Error modifying config: {str(e)}"

    async def _handle_strategy_command(self, user_input: str) -> str:
        try:
            response = await self._call_claude_api([{
                "role": "user",
                "content": f"Create a FreqTrade strategy based on this description: {user_input}"
            }])
            return response
        except Exception as e:
            logger.error(f"Strategy command failed: {str(e)}", exc_info=True)
            return f"Error processing strategy command: {str(e)}"

    async def _handle_backtest(self, user_input: str) -> str:
        try:
            response = await self._call_claude_api([{
                "role": "user",
                "content": f"Convert this backtest request into FreqTrade CLI arguments: {user_input}"
            }])
            return response
        except Exception as e:
            logger.error(f"Backtest command failed: {str(e)}", exc_info=True)
            return f"Error processing backtest command: {str(e)}"

    async def _handle_bot_control(self, user_input: str) -> str:
        try:
            response = await self._call_claude_api([{
                "role": "user",
                "content": f"Convert this bot control request into specific actions: {user_input}"
            }])
            return response
        except Exception as e:
            logger.error(f"Bot control command failed: {str(e)}", exc_info=True)
            return f"Error processing bot control command: {str(e)}"

    def _update_nested_dict(self, d: Dict, u: Dict) -> Dict:
        for k, v in u.items():
            if isinstance(v, dict):
                d[k] = self._update_nested_dict(d.get(k, {}), v)
            else:
                d[k] = v
        return d

    def _parse_command_type(self, claude_response: str) -> str:
        # Add logic to determine command type
        if "config" in claude_response.lower():
            return "modify_config"
        elif "strategy" in claude_response.lower():
            return "strategy"
        elif "backtest" in claude_response.lower():
            return "backtest"
        elif any(cmd in claude_response.lower() for cmd in ["start", "stop", "status"]):
            return "bot_control"
        return "unknown"

    async def clear_history(self) -> None:
        self.conversation_history = []

    def get_current_accuracy(self) -> float:
        return self.current_metrics["accuracy"]

    def get_current_loss(self) -> float:
        return self.current_metrics["loss"]

    async def start_training(self) -> None:
        # Implement FreqAI training initialization here
        pass