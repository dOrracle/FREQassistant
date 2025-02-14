from typing import Callable, Dict, Type, Any
import logging
import traceback

class ErrorRecoveryManager:
    def __init__(self, state_manager=None):
        self.state_manager = state_manager
        self.handlers = {}
        self.logger = logging.getLogger(__name__)

    async def handle_error(self, error, context):
        if self.state_manager:
            await self.state_manager.save_state()
        handler = self.handlers.get(type(error))
        if handler:
            return await handler(error, context)
        self.logger.error(f"Unhandled error: {error}")
        raise

class ErrorHandler:
    """Centralized error handling and recovery"""
    def __init__(self):
        self.handlers: Dict[Type[Exception], Callable] = {}
        self.logger = logging.getLogger(__name__)
        self.recovery_manager = ErrorRecoveryManager()

    def register(self, exception_type: Type[Exception], handler: Callable):
        """Register an error handler for a specific exception type"""
        self.handlers[exception_type] = handler

    async def handle(self, error: Exception, context: Dict[str, Any] = None) -> Any:
        """Handle an error using registered handlers"""
        handler = self.handlers.get(type(error))
        if handler:
            try:
                return await handler(error, context)
            except Exception as e:
                self.logger.error(f"Error in handler: {e}\n{traceback.format_exc()}")
                raise
        else:
            self.logger.error(f"Unhandled error: {error}\n{traceback.format_exc()}")
            raise