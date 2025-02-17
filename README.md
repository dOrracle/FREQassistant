# FREQassistant

An AI-powered assistant for FreqTrade that uses Claude AI to help manage, optimize, and automate your cryptocurrency trading strategies.

## Prerequisites

- Python 3.9+
- Node.js 16+
- npm 8+
- FreqTrade installed and configured
- Anthropic API key

## Environment Setup

1. Create a `.env` file in the project root:
    ```bash
    ANTHROPIC_API_KEY=your_api_key_here
    PORT=8000
    LOG_LEVEL=info
    ```

## Installation

1. Clone the repository into your FreqTrade user_data directory:
    ```bash
    cd freqtrade/user_data
    git clone https://github.com/yourusername/FREQassistant.git
    cd FREQassistant
    ```

2. Create and activate virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3. Install Python dependencies:
    ```bash
    pip install -r requirements.txt
    ```

4. Build the React frontend:
    ```bash
    cd frontend
    npm install
    npm run build
    cd ..
    ```

5. Configure the application:
    - Copy `config.example.json` to `config.json`
    - Copy `claude_config.example.json` to `claude_config.json`
    ```bash
    cp src/config.example.json src/config.json
    cp src/claude_config.example.json src/claude_config.json
    ```

6. Update configuration files with your settings:
    - Edit `src/config.json` with your FreqTrade settings
    - Edit `src/claude_config.json` with your Claude AI preferences

## Running the Application

1. Start the FastAPI server:
    ```bash
    python main.py
    ```

2. Access the dashboard:
    - Open `http://localhost:8000` in your web browser
    - Default credentials: admin/password (change these in production)

## Features

### AI Assistant Capabilities
- Natural language trading strategy generation
- Configuration management
- Automated backtesting
- Performance analysis
- Real-time trading monitoring

### Dashboard Features
- Real-time metrics visualization
- Strategy management interface
- Configuration editor
- Backtesting results viewer
- ML model training interface

## API Documentation

### REST Endpoints
- `GET /health` - System health check
- `POST /api/v1/claude/message` - Send message to Claude AI
- `GET /api/v1/claude/metrics` - Get ML metrics
- `POST /api/v1/claude/clear-history` - Clear chat history
- `POST /api/v1/claude/start-training` - Start ML training

## Development

1. Start frontend in development mode:
    ```bash
    cd frontend
    npm start
    ```

2. Start backend in development mode:
    ```bash
    uvicorn main:app --reload
    ```

## Testing

1. Run backend tests:
    ```bash
    pytest tests/
    ```

2. Run frontend tests:
    ```bash
    cd frontend
    npm test
    ```

## Troubleshooting

### Common Issues

1. **Connection Error**:
    ```bash
    # Check if FreqTrade is running
    curl http://localhost:8000/health
    ```

2. **Authentication Error**:
    - Verify ANTHROPIC_API_KEY in .env
    - Check FreqTrade API permissions

3. **Frontend Build Fails**:
    ```bash
    # Clear npm cache
    npm clean-cache --force
    ```

## Security

- Change default credentials
- Use HTTPS in production
- Keep API keys secure
- Regular security updates

## Contributing

1. Fork the repository
2. Create feature branch
3. Submit pull request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

- Cross your fingers harder next time.  Eat a snack.  Drink more beer. 

## Acknowledgments

- FreqTrade Team
- Anthropic Claude AI
- Contributors
