import asyncio
import logging  # This was missing from some code paths
import os
import json
from typing import Dict, Any, Optional
import uvicorn
import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from src.bot import FreqtradeAI
from src.freqai_integration import FreqAIIntegration
from src.controllers.claude_controller import ClaudeFreqAIController
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Global bot instance for proper shutdown management
bot: Optional[FreqtradeAI] = None

# Initialize FastAPI and configure logging
app = FastAPI(title="FreqAssistant API", version="1.0.0")
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

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

# Add health check endpoint
@app.get("/health")
async def health_check():
    return JSONResponse({"status": "healthy"})

def validate_config(config: Dict[str, Any]) -> None:
    """Validate required configuration values"""
    required_keys = {
        'anthropic': ['api_key'],
        'freqtrade': ['config_path'],
        'claude_integration': ['model_version']
    }
    
    for section, keys in required_keys.items():
        if section not in config:
            raise ValueError(f"Missing required section: {section}")
        for key in keys:
            if key not in config[section]:
                raise ValueError(f"Missing required key: {section}.{key}")

def load_config(config_path: str = "claude_config.json") -> Dict[str, Any]:
    """Load configuration from JSON file"""
    if not os.path.exists(config_path):
        logger.error(f"Config file not found: {config_path}")
        raise FileNotFoundError(f"Config file not found: {config_path}")
        
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Override API key from environment if available
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if api_key:
            config.setdefault('anthropic', {})['api_key'] = api_key
        
        # Validate config
        validate_config(config)    
        return config
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in config file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error loading config: {e}")
        raise

async def initialize_bot(config: Dict[str, Any]) -> Optional[FreqtradeAI]:
    """Initialize bot with configuration"""
    global bot
    try:
        client = anthropic.Anthropic(api_key=config['anthropic']['api_key'])
        bot = FreqtradeAI(
            config['anthropic']['api_key'],
            config['freqtrade']['config_path']
        )
        
        claude_controller = ClaudeFreqAIController(config, client)
        freqai_integration = FreqAIIntegration(config, client)
        
        bot.claude_controller = claude_controller
        return bot
    except Exception as e:
        logger.error(f"Failed to initialize bot: {e}")
        return None

async def main() -> None:
    """Main application entry point"""
    try:
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        if not config['anthropic']['api_key']:
            raise ValueError("ANTHROPIC_API_KEY not found in environment or config")
            
        bot = await initialize_bot(config)
        logger.info("Starting FreqAssistant...")
        await bot.start()
        
    except ValueError as ve:
        logger.error(f"Configuration error: {ve}")
        raise
    except Exception as e:
        logger.error(f"System error: {e}")
        raise

async def shutdown_event() -> None:
    """Cleanup on shutdown"""
    logger.info("Shutting down FreqAssistant...")
    if bot is not None:
        try:
            await bot.shutdown()
            logger.info("Bot shutdown completed")
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")

if __name__ == "__main__":
    try:
        server = uvicorn.Server(
            uvicorn.Config(
                app,
                host="0.0.0.0",
                port=int(os.getenv('PORT', 8000)),
                log_level=os.getenv('LOG_LEVEL', 'info').upper(),
                lifespan="on"
            )
        )
        
        # Add shutdown handler before starting
        app.add_event_handler("shutdown", shutdown_event)
        
        # Create main task
        main_task = asyncio.create_task(main())
        
        # Run server with main task
        logger.info("Starting FreqAssistant server and bot...")
        asyncio.run(
            asyncio.gather(
                server.serve(),
                main_task,
                return_exceptions=True
            )
        )
    except KeyboardInterrupt:
        logger.info("Received shutdown signal...")
        if main_task and not main_task.done():
            main_task.cancel()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)
    finally:
        # Ensure clean shutdown
        try:
            if bot is not None:
                asyncio.run(shutdown_event())
        except Exception as e:
            logger.error(f"Error during final shutdown: {e}")
        logger.info("FreqAssistant shutdown complete")