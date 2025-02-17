import logging
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
from .controllers.claude_controller import ClaudeFreqAIController

logger = logging.getLogger(__name__)

router = APIRouter()

class MessageRequest(BaseModel):
    content: str

class MetricsResponse(BaseModel):
    accuracy: float
    loss: float

def get_claude_controller():
    if not hasattr(router, "claude_controller"):
        router.claude_controller = ClaudeFreqAIController()
    return router.claude_controller

@router.post("/api/v1/claude/message")
async def handle_message(
    message: MessageRequest,
    controller: ClaudeFreqAIController = Depends(get_claude_controller)
) -> Dict[str, str]:
    try:
        response = await controller.handle_command(message.content)
        return {"response": response}
    except Exception as e:
        logger.error(f"Message handling failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/v1/claude/metrics")
async def get_metrics(
    controller: ClaudeFreqAIController = Depends(get_claude_controller)
) -> MetricsResponse:
    try:
        return MetricsResponse(
            accuracy=controller.get_current_accuracy(),
            loss=controller.get_current_loss()
        )
    except Exception as e:
        logger.error(f"Metrics retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/claude/clear-history")
async def clear_history(
    controller: ClaudeFreqAIController = Depends(get_claude_controller)
) -> Dict[str, str]:
    try:
        await controller.clear_history()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"History clear failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/v1/claude/start-training")
async def start_training(
    controller: ClaudeFreqAIController = Depends(get_claude_controller)
) -> Dict[str, str]:
    try:
        await controller.start_training()
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Training start failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/api/metrics")
async def get_metrics():
    # Connect to FreqAIIntegration metrics
    return freqai_integration.get_current_metrics()

@router.post("/api/message")
async def send_message(message: str):
    # Forward to ClaudeFreqAIController
    return await claude_controller.handle_command(message)

@router.post("/api/clear-history")
async def clear_history():
    # Clear chat history
    return {"status": "success"}

@router.post("/api/start-training")
async def start_training():
    # Trigger FreqAI training
    return {"status": "success"}