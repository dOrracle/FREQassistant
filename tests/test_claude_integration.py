import pytest
from unittest.mock import Mock, patch

@pytest.fixture
def mock_claude():
    return Mock()

async def test_claude_commands():
    controller = ClaudeFreqAIController(test_config)
    result = await controller.handle_command("modify max_open_trades to 5")
    assert "Configuration updated successfully" in result

async def test_strategy_generation(mock_claude):
    controller = ClaudeFreqAIController(test_config)
    controller.claude = mock_claude
    result = await controller.handle_command("create RSI strategy")
    assert "strategy" in result.lower()