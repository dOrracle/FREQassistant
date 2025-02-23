import logging
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from anthropic import Anthropic
from .config_manager import FreqtradeConfigManager
from .freqai_manager import FreqAIManager
from .secure_commands import SecureCommands
from .error_handler import ErrorRecoveryManager
from .freqai_integration import MonitoringSystem
from cachetools import TTLCache
from .controllers.claude_controller import ClaudeFreqAIController

logger = logging.getLogger(__name__)

@dataclass
class SystemState:
    is_running: bool = False
    current_model_description: str = ""
    last_prediction: Dict[str, Any] = field(default_factory=dict)
    performance: Dict[str, Any] = field(default_factory=dict)
    cache: TTLCache = field(default_factory=lambda: TTLCache(maxsize=100, ttl=60))

@dataclass
class FreqtradeAI:
    api_key: str
    config_path: str
    config_manager: FreqtradeConfigManager = field(init=False)
    freqai_manager: FreqAIManager = field(init=False)
    secure_commands: SecureCommands = field(init=False)
    claude_controller: Optional[ClaudeFreqAIController] = field(default=None, init=False)

    def __post_init__(self):
        self.state = SystemState()
        self.config_manager = FreqtradeConfigManager(self.api_key, self.config_path)
        self.freqai_manager = FreqAIManager()
        self.secure_commands = SecureCommands(self)
        self.claude_controller = None
        self.monitoring = MonitoringSystem()

    async def start(self):
        """Start the FreqTrade AI assistant"""
        self.state.is_running = True
        logger.info("FreqTrade AI Assistant started")
        
    async def shutdown(self):
        """Shutdown the FreqTrade AI assistant"""
        self.state.is_running = False
        logger.info("FreqTrade AI Assistant shutdown")