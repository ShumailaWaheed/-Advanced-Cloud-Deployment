"""Chat API routes for the todo chatbot application."""

import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from src.api.auth_middleware import get_current_user_id
from src.chat.command_parser import CommandParser
from src.chat.command_handlers import CommandHandlers

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1)


@router.post("/process")
async def process_chat(
    body: ChatRequest,
    user_id: str = Depends(get_current_user_id),
):
    """POST /api/v1/chat/process - Process a chat command."""
    try:
        command = CommandParser.parse(body.message)
        result = await CommandHandlers.handle(command, user_id)
        return result
    except Exception as e:
        logger.error(f"Error processing chat command: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
