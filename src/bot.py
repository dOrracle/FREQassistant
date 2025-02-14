from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import asyncio
import logging
from anthropic import Anthropic
from .config_manager import FreqtradeConfigManager
from .freqai_manager import FreqAIManager
from .secure_commands import SecureCommands
from .simulated_components import SimulatedExchange, SimulatedFreqAIModel
from .error_handler import ErrorRecoveryManager
from .freqai_integration import MonitoringSystem
from cachetools import TTLCache
from .claude_controller import ClaudeFreqAIController

@dataclass
class SystemState:
    is_running: bool = False
    current_model_description: str = ""
    last_prediction: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)
    cache: TTLCache = field(default_factory=lambda: TTLCache(maxsize=100, ttl=60))

class FreqtradeAI:
    def __init__(self, api_key: str, config_path: str):
        self.claude = Anthropic(api_key=api_key)
        self.state = SystemState()
        self.error_manager = ErrorRecoveryManager(self.state)
        self.monitoring = MonitoringSystem()
        self.config_manager = FreqtradeConfigManager(api_key, config_path)
        self.config = self.config_manager.read_config()
        
        # Add ClaudeController initialization
        self.claude_controller = ClaudeFreqAIController(self.config)
        
        self.exchange = SimulatedExchange(self.config)
        self.freqai_model = SimulatedFreqAIModel(self.config)
        self.freqai_manager = FreqAIManager(self.freqai_model, self.claude, self.config_manager)
        self.command_handler = SecureCommands(self)
        self.logger = logging.getLogger(__name__)
        self.message_queue = asyncio.Queue()

    async def start(self):
        try:
            self.state.is_running = True
            await asyncio.gather(
                self._run_prediction_loop(),
                self._run_optimization_loop()
            )
        except Exception as e:
            self.logger.error(f"System error: {e}")
            self.state.is_running = False

    async def shutdown(self):
        self.state.is_running = False
        try:
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            for task in tasks:
                task.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)
            
            while not self.message_queue.empty():
                try:
                    self.message_queue.get_nowait()
                except asyncio.QueueEmpty:
                    break
            
            self.logger.info("Bot shutdown completed")
        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    async def _run_prediction_loop(self):
        while self.state.is_running:
            try:
                predictions = await self.freqai_manager.get_live_predictions()
                if isinstance(predictions, dict):
                    self.state.last_prediction = predictions
                await asyncio.sleep(60)
            except Exception as e:
                self.logger.error(f"Prediction error: {e}")
                await asyncio.sleep(60)

    async def _run_optimization_loop(self):
        while self.state.is_running:
            try:
                if self.state.performance.get('profit', 0) < 0:
                    await self.freqai_manager.optimize_strategy(
                        self.state.current_model_description
                    )
                await asyncio.sleep(3600)
            except Exception as e:
                self.logger.error(f"Optimization error: {e}")
                await asyncio.sleep(60)

    async def handle_command(self, user_id: str, command: str) -> str:
        try:
            if command.startswith('/claude'):
                # Ensure user has permission through SecureCommands
                if not self.command_handler.verify_user_permission(user_id, "claude"):
                    return "You don't have permission to use Claude commands"
                
                # Strip '/claude' and process the command
                claude_prompt = command[7:].strip()
                response = await self.claude.messages.create(
                    model="claude-3-sonnet-20240229",
                    max_tokens=1000,
                    messages=[{"role": "user", "content": claude_prompt}]
                )
                return response.content
            else:
                # Handle existing commands as before
                return await self.command_handler.process_command(user_id, command)
        except Exception as e:
            self.logger.error(f"Command error: {e}")
            return f"Error processing command: {e}"

    async def update_strategy(self, user_id: str, description: str) -> str:
        try:
            result = await self.command_handler.handle_strategy(
                user_id, 
                "/generate_strategy", 
                description
            )
            if "successfully" in result:
                self.state.current_model_description = description
            return result
        except Exception as e:
            self.logger.error(f"Strategy update failed: {e}")
            return f"Strategy update failed: {e}"

    def _get_status(self) -> Dict[str, Any]:
        return {
            "running": self.state.is_running,
            "current_model": self.state.current_model_description,
            "last_prediction": self.state.last_prediction,
            "performance": self.state.performance
        }

    def _get_help(self) -> str:
        return """
Available commands:
/status - Get current bot status
/generate_strategy <description> - Generate new trading strategy
/update_config <request> - Update bot configuration
/market_analysis - Get market analysis
/claude <prompt> - Interact with Claude AI
/help - Show this help message
    """