from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import time

from ..config.database import get_db
from ..models.models import User
from ..schemas.chat import ChatMessageCreate, ChatMessageResponse, ChatHistoryResponse, ProviderResponse
from ..chat_module.api.chat_api import get_chat_api
from ..auth.auth_utils import get_current_active_user

router = APIRouter()

@router.post("/message", response_model=ChatMessageResponse)
async def send_message(
    message: ChatMessageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Send a message to the AI assistant
    """
    chat_api = get_chat_api()
    response = await chat_api.send_message(message.content, db)
    
    return {
        "role": response.get("role", "assistant"),
        "content": response.get("content", ""),
        "provider": response.get("provider", ""),
        "timestamp": response.get("timestamp", time.time())
    }

@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get chat history
    """
    chat_api = get_chat_api()
    history = chat_api.get_chat_history(limit)
    
    return {
        "messages": [
            {
                "role": msg.get("role", ""),
                "content": msg.get("content", ""),
                "timestamp": msg.get("timestamp", 0)
            }
            for msg in history
        ],
        "count": len(history)
    }

@router.post("/clear", status_code=status.HTTP_204_NO_CONTENT)
async def clear_chat_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Clear chat history
    """
    chat_api = get_chat_api()
    success = chat_api.clear_chat_history()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to clear chat history"
        )
    
    return None

@router.post("/provider/{provider}", response_model=ProviderResponse)
async def set_ai_provider(
    provider: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Set the active AI provider
    """
    chat_api = get_chat_api()
    result = await chat_api.set_ai_provider(provider, db)
    
    if result.get("status") == "error":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result.get("message", f"Invalid provider: {provider}")
        )
    
    return {
        "provider": result.get("provider", ""),
        "timestamp": result.get("timestamp", time.time())
    }

@router.get("/provider", response_model=ProviderResponse)
async def get_ai_provider(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get the active AI provider
    """
    chat_api = get_chat_api()
    provider = chat_api.get_ai_provider()
    
    return {
        "provider": provider,
        "timestamp": time.time()
    }
