import asyncio
import logging
import logging.config
import os
import json
from typing import Dict, Any, Optional
import uvicorn
import anthropic
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from src.bot import FreqtradeAI
from src.freqai_integration import FreqAIIntegration
from src.controllers.claude_controller import ClaudeFreqAIController
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Global bot instance for proper shutdown management
bot: Optional[FreqtradeAI] = None

# Initialize FastAPI and configure logging
app = FastAPI(
    title="FreqAssistant API",
    version="1.0.0",
    description="FastAPI backend for FreqAssistant"
)
logging.config.fileConfig('logging.conf')
logger = logging.getLogger(__name__)

# Get CORS origins from environment variable
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:8081,http://127.0.0.1:8081").split(",")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Update the static files mounting
frontend_path = os.path.join(os.getcwd(), "frontend", "build")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")

# Add a root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    logger.info("Root endpoint called")
    return {
        "message": "Welcome to FreqAssistant API",
        "version": "1.0.0",
        "status": "running"
    }

# Add health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return {"status": "healthy"}

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
        # Try in config directory
        alt_path = os.path.join('config', config_path)
        if os.path.exists(alt_path):
            config_path = alt_path
        else:
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
        # Get log level with proper fallback
        log_level = os.getenv('LOG_LEVEL', 'info').lower()
        if log_level not in ('critical', 'error', 'warning', 'info', 'debug', 'trace'):
            log_level = 'info'
            
        # Try different ports if 8000 is in use
        port = int(os.getenv('PORT', 8000))
        max_port_attempts = 10
        
        for port_attempt in range(port, port + max_port_attempts):
            try:
                config = uvicorn.Config(
                    app,
                    host="0.0.0.0",
                    port=port_attempt,
                    log_level=log_level,
                    lifespan="on"
                )
                
                server = uvicorn.Server(config)
                
                # Add shutdown handler before starting
                app.add_event_handler("shutdown", shutdown_event)
                
                # Create and run event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Create main task
                    main_task = loop.create_task(main())
                    
                    # Run server with main task
                    logger.info(f"Starting FreqAssistant server and bot on port {port_attempt}...")
                    loop.run_until_complete(
                        asyncio.gather(
                            server.serve(),
                            main_task,
                            return_exceptions=True
                        )
                    )
                    break  # If successful, exit the port attempt loop
                except OSError as e:
                    if e.errno == 98:  # Address already in use
                        logger.warning(f"Port {port_attempt} is in use, trying next port")
                        continue
                    raise
                finally:
                    loop.close()
                    
            except KeyboardInterrupt:
                logger.info("Received shutdown signal...")
                if main_task and not main_task.done():
                    main_task.cancel()
                break
                
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        exit(1)
    finally:
        # Ensure clean shutdown
        try:
            if bot is not None:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(shutdown_event())
                loop.close()
        except Exception as e:
            logger.error(f"Error during final shutdown: {e}")
        logger.info("FreqAssistant shutdown complete")