import pytest
from src.controllers.claude_controller import ClaudeController

@pytest.mark.asyncio
async def test_claude_strategy_generation():
    config = {"test": "config"}
    controller = ClaudeController(config)
    description = "RSI crossover strategy with MACD confirmation"
    result = await controller.generate_strategy(description)
    assert "class RSIMACDStrategy" in result

@pytest.mark.asyncio
async def test_command_parsing():
    config = {"test": "config"}
    controller = ClaudeController(config)
    command = controller.parse_command("Create a strategy using RSI and MACD")
    assert command["action"] == "create_strategy"
    assert "RSI" in command["indicators"]
    assert "MACD" in command["indicators"]