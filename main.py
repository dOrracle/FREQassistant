import asyncio
import logging
import os
import json
from typing import Dict, Any
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from src.bot import FreqtradeAI
from src.freqai_integration import FreqAIIntegration
from src.claude_controller import ClaudeFreqAIController

# Initialize FastAPI
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the React app
app.mount("/", StaticFiles(directory="frontend/build", html=True))

def load_config(config_path: str = "claude_config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Override API key from environment if available
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            config['anthropic']['api_key'] = api_key
            
        return config
    except Exception as e:
        logging.error(f"Error loading config: {e}")
        raise

async def main():
    # Load configuration
    config = load_config()
    
    # Validate API key
    if not config['anthropic']['api_key']:
        raise ValueError("Error: ANTHROPIC_API_KEY not found in environment or config")
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, config['logging']['level']),
        format=config['logging']['format']
    )
    
    # Initialize components
    bot = FreqtradeAI(
        config['anthropic']['api_key'],
        config['freqtrade']['config_path']
    )
    
    claude_controller = ClaudeFreqAIController(config)
    freqai_integration = FreqAIIntegration(config)
    
    # Add controller to bot
    bot.claude_controller = claude_controller
    
    try:
        # Start bot and API server
        await asyncio.gather(
            bot.start(),
            app.start()
        )
    except Exception as e:
        logging.error(f"System error: {e}")
        raise
    finally:
        await bot.shutdown()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        exit(1)