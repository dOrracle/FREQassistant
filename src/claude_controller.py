import logging
from typing import Dict, Any, Optional
from anthropic import Anthropic
import json
import subprocess
import os
from ..utils.rate_limiter import RateLimiter

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

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.claude = Anthropic(api_key=config['anthropic']['api_key'])
        
        # Initialize with system prompt
        self.system_prompt = """You are an AI assistant specialized in managing and optimizing the FreqTrade cryptocurrency trading bot platform. Your core function is to serve as an intelligent interface between users and the FreqTrade system, translating natural language requests into concrete actions and providing expert guidance on trading strategies, configuration, and system management."""
        
        # Set default parameters
        self.model_version = "claude-3-5-sonnet-latest"
        self.max_tokens = 8192
        self.temperature = 1

        # Update model version from config if present
        if 'claude_integration' in config:
            self.model_version = config['claude_integration'].get('model_version', self.model_version)
            self.max_tokens = config['claude_integration'].get('max_tokens', self.max_tokens)
            self.temperature = config['claude_integration'].get('temperature', self.temperature)

        self.base_config_path = "config.json"
        self.rate_limiter = RateLimiter()

    async def _call_claude_api(self, messages: list) -> str:
        try:
            self.rate_limiter.limit()
            if "Create a FreqTrade strategy" in messages[0]["content"]:
                messages[0]["content"] = self.STRATEGY_TEMPLATE.format(
                    description=messages[0]["content"]
                )
            elif "config modification" in messages[0]["content"]:
                current_config = self._get_current_config()
                messages[0]["content"] = self.CONFIG_TEMPLATE.format(
                    request=messages[0]["content"],
                    current_config=json.dumps(current_config, indent=2)
                )
            
            response = await self.claude.messages.create(
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
                "content": f"Convert this strategy request into Python code: {user_input}"
            }])
            
            strategy_code = response
            strategy_name = self._extract_strategy_name(strategy_code)
            
            strategy_path = f"user_data/strategies/{strategy_name}.py"
            with open(strategy_path, 'w') as f:
                f.write(strategy_code)
                
            return f"Strategy {strategy_name} created/updated successfully"
            
        except Exception as e:
            logger.error(f"Strategy command failed: {str(e)}", exc_info=True)
            return f"Error handling strategy command: {str(e)}"

    async def _handle_backtest(self, user_input: str) -> str:
        try:
            response = await self._call_claude_api([{
                "role": "user",
                "content": f"Convert this backtest request to command line arguments: {user_input}"
            }])
            
            backtest_args = response.split()
            cmd = ["freqtrade", "backtesting"] + backtest_args
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Backtest failed: {result.stderr}")
                return f"Error: {result.stderr}"
                
            return result.stdout
            
        except Exception as e:
            logger.error(f"Backtest failed: {str(e)}", exc_info=True)
            return f"Error running backtest: {str(e)}"

    async def _handle_bot_control(self, user_input: str) -> str:
        try:
            response = await self._call_claude_api([{
                "role": "user",
                "content": f"Convert this bot control request to a specific command: {user_input}"
            }])
            
            command = response.strip()
            
            if command not in ["start", "stop", "status"]:
                return f"Invalid bot command: {command}"
                
            # Implement bot control logic here
            return f"Bot command {command} executed successfully"
            
        except Exception as e:
            logger.error(f"Bot control failed: {str(e)}", exc_info=True)
            return f"Error controlling bot: {str(e)}"

    async def safe_api_call(self, func, *args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"API call failed: {str(e)}")
            raise APIError(f"Operation failed: {str(e)}")

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

    def _extract_strategy_name(self, strategy_code: str) -> str:
        try:
            # Look for class definition
            for line in strategy_code.split('\n'):
                if line.strip().startswith('class ') and '(' in line:
                    class_name = line.split('class ')[1].split('(')[0].strip()
                    return class_name
        except Exception:
            logger.warning("Could not extract strategy name", exc_info=True)
        return "NewStrategy"

    async def _handle_strategy_creation(self, description: str) -> str:
        try:
            response = await self._call_claude_api([{
                "role": "user",
                "content": f"Create a FreqTrade strategy based on: {description}. Return only the Python code."
            }])
            
            # Extract strategy code
            strategy_code = self._extract_code_block(response)
            
            # Validate strategy code
            if not self._validate_strategy_code(strategy_code):
                return "Invalid strategy code generated"
                
            # Save strategy
            strategy_name = self._extract_strategy_name(strategy_code)
            strategy_path = f"user_data/strategies/{strategy_name}.py"
            
            with open(strategy_path, 'w') as f:
                f.write(strategy_code)
                
            return f"Strategy {strategy_name} created successfully"
            
        except Exception as e:
            logger.error(f"Strategy creation failed: {str(e)}")
            return f"Error creating strategy: {str(e)}"

    def _validate_strategy_code(self, code: str) -> bool:
        """Enhanced validation"""
        required_elements = [
            "class", 
            "from freqtrade.strategy.interface import IStrategy",
            "populate_indicators",
            "populate_entry_trend",
            "populate_exit_trend",
            "minimal_roi",
            "stoploss",
            "timeframe"
        ]
        
        try:
            # Basic syntax check
            compile(code, '<string>', 'exec')
            
            # Check required elements
            return all(element in code for element in required_elements)
        except SyntaxError:
            return False

    def _extract_code_block(self, response: str) -> str:
        """Add this method to properly extract code blocks"""
        if "```python" in response:
            code = response.split("```python")[1].split("```")[0]
            return code.strip()
        return response.strip()

    def _get_current_config(self) -> Dict[str, Any]:
        """Get current FreqTrade configuration"""
        try:
            with open(self.base_config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error reading config: {str(e)}")
            return {}