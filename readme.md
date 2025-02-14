# FreqTrade-Claude AI Integration

## Quick Setup

1. Install FreqTrade prerequisites:
```bash
git clone https://github.com/freqtrade/freqtrade.git
cd freqtrade
./setup.sh -i
```

2. Install Claude Integration:
```bash
# In your freqtrade directory
mkdir -p user_data/claude_ai
cd user_data/claude_ai

# Copy files to these locations:
freqtrade/
├── user_data/
│   ├── claude_ai/
│   │   ├── claude_controller.py
│   │   ├── secure_commands.py
│   │   ├── freqai_manager.py
│   │   ├── config_manager.py
│   │   └── error_manager.py
│   ├── strategies/
│   └── config.json

# Install required packages
pip install -r requirements.txt
```

3. Configure API Keys:
```bash
# Create config.json in user_data/claude_ai/
{
    "anthropic": {
        "api_key": "YOUR_API_KEY"
    },
    "claude_integration": {
        "model_version": "claude-3-sonnet-20240229",
        "max_tokens": 4096,
        "temperature": 0.7
    }
}
```

## Usage

1. Start the bot:
```bash
freqtrade trade --config user_data/claude_ai/config.json
```

2. Available Commands:
```
/status - Check bot status
/generate_strategy <description> - Create new strategy
/market_analysis - Get market analysis
/update_config <request> - Modify configuration
/help - Show all commands
```

3. Example Commands:
```
# Generate Strategy
/generate_strategy Create a strategy using RSI and MACD for BTC/USDT

# Update Config
/update_config Change max_open_trades to 5 and stake_amount to 100

# Market Analysis
/market_analysis BTC/USDT trend analysis
```

## File Structure Details

1. `claude_controller.py`: Main Claude AI integration
- Handles command processing
- Manages API communication
- Validates outputs

2. `secure_commands.py`: Security layer
- Command validation
- Rate limiting
- Permission management

3. `freqai_manager.py`: FreqAI integration
- Model management
- Performance tracking
- Strategy optimization

4. `config_manager.py`: Configuration handler
- Config file management
- Validation
- Safe updates

5. `error_manager.py`: Error handling
- Error recovery
- Logging
- State management

## Troubleshooting

1. API Connection Issues:
```bash
# Check API key
export ANTHROPIC_API_KEY="your-key"
python -m freqtrade.main check-config
```

2. Strategy Generation Issues:
```bash
# Verify strategy format
freqtrade test-preds -s GeneratedStrategy
```

3. Common Fixes:
- Clear cache: `rm -rf user_data/claude_ai/__pycache__`
- Update Claude: `pip install --upgrade anthropic`
- Check logs: `tail -f user_data/logs/freqtrade.log`

## Security Notes

1. API Key Protection:
- Store in environment variables
- Never commit to version control
- Use secure permissions

2. Rate Limiting:
- Default: 20 requests/minute
- Configurable in `config.json`

3. File Permissions:
```bash
chmod 600 user_data/claude_ai/config.json
chmod 644 user_data/claude_ai/*.py
```

## Updates and Maintenance

1. Update FreqTrade:
```bash
git pull
./setup.sh -u
```

2. Update Claude Integration:
```bash
pip install --upgrade anthropic
```

For more information, visit:
- FreqTrade Docs: https://www.freqtrade.io/en/stable/
- Claude API Docs: https://docs.anthropic.com/claude/