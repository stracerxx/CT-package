from typing import Dict, List, Optional, Union, Any
import os
import time
import json
import logging
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from ..models.models import SystemPrompt, User
from ..config.database import get_db
from .chat import ChatModule

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('chat_api')

class ChatAPI:
    """
    API interface for the Chat Module
    
    Handles database interactions and provides an interface for the FastAPI endpoints.
    """
    
    def __init__(self):
        """Initialize Chat API"""
        self.chat_module = ChatModule()
        logger.info("Chat API initialized")
    
    async def get_active_system_prompt(self, db: Session) -> str:
        """
        Get the active system prompt from the database
        
        Args:
            db: Database session
            
        Returns:
            System prompt content
        """
        try:
            # Query the active system prompt
            system_prompt = db.query(SystemPrompt).filter(SystemPrompt.is_active == True).first()
            
            if system_prompt:
                # Update the chat module with the active prompt
                self.chat_module.set_system_prompt(system_prompt.content)
                return system_prompt.content
            else:
                # Use default prompt if none is active
                return self.chat_module.get_system_prompt()
                
        except Exception as e:
            logger.error(f"Error getting active system prompt: {str(e)}")
            return self.chat_module.get_system_prompt()
    
    async def send_message(self, user_message: str, db: Session) -> Dict:
        """
        Send a message to the chat module
        
        Args:
            user_message: User message content
            db: Database session
            
        Returns:
            Response from the chat module
        """
        try:
            # Ensure we have the latest system prompt
            await self.get_active_system_prompt(db)
            
            # Send message to chat module
            response = await self.chat_module.send_message(user_message)
            
            return response
            
        except Exception as e:
            logger.error(f"Error sending message: {str(e)}")
            return {
                'role': 'error',
                'content': f"I'm sorry, I encountered an error: {str(e)}. Please try again.",
                'provider': self.chat_module.get_active_provider(),
                'error': str(e),
                'timestamp': time.time()
            }
    
    def get_chat_history(self, limit: int = 50) -> List[Dict]:
        """
        Get chat history
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of chat messages
        """
        return self.chat_module.get_chat_history(limit)
    
    def clear_chat_history(self) -> bool:
        """
        Clear chat history
        
        Returns:
            Success status
        """
        return self.chat_module.clear_history()
    
    async def set_ai_provider(self, provider: str, db: Session) -> Dict:
        """
        Set the active AI provider
        
        Args:
            provider: Provider name
            db: Database session
            
        Returns:
            Status and provider info
        """
        try:
            # Check if provider is valid
            success = self.chat_module.set_active_provider(provider)
            
            if success:
                return {
                    'status': 'success',
                    'provider': provider,
                    'timestamp': time.time()
                }
            else:
                return {
                    'status': 'error',
                    'message': f"Invalid provider: {provider}",
                    'timestamp': time.time()
                }
                
        except Exception as e:
            logger.error(f"Error setting AI provider: {str(e)}")
            return {
                'status': 'error',
                'message': f"Error setting AI provider: {str(e)}",
                'timestamp': time.time()
            }
    
    def get_ai_provider(self) -> str:
        """
        Get the active AI provider
        
        Returns:
            Active provider name
        """
        return self.chat_module.get_active_provider()

# Create a singleton instance
chat_api = ChatAPI()

# Function to get the ChatAPI instance
def get_chat_api():
    return chat_api
