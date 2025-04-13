from typing import Dict, List, Optional, Union, Any
import os
import time
import json
import logging
from dotenv import load_dotenv
import openai
from anthropic import Anthropic
import google.generativeai as genai
import requests

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('chat_module')

# Load environment variables
load_dotenv()

class ChatModule:
    """
    Persistent AI Chat Module for CT-5
    
    Handles interactions with various AI providers and maintains chat history.
    """
    
    def __init__(self, db_connector=None):
        """
        Initialize Chat Module
        
        Args:
            db_connector: Database connector for storing chat history
        """
        self.db_connector = db_connector
        self.active_provider = "openai"  # Default provider
        self.system_prompt = self._load_default_system_prompt()
        self.chat_history = []
        
        # Initialize API clients
        self._initialize_api_clients()
        
        logger.info("Chat Module initialized")
    
    def _initialize_api_clients(self):
        """Initialize API clients for different providers"""
        # OpenAI
        openai.api_key = os.getenv("OPENAI_API_KEY", "")
        
        # Anthropic (Claude)
        self.anthropic_client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY", ""))
        
        # Google Gemini
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", ""))
        
        # OpenRouter
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        
        # DeepSeek
        self.deepseek_api_key = os.getenv("DEEPSEEK_API_KEY", "")
    
    def _load_default_system_prompt(self) -> str:
        """Load default system prompt if none is set"""
        default_prompt = """
        You are CT-5, a friendly and knowledgeable crypto trading assistant with an 80s retro personality.
        
        Your capabilities:
        - Explain trading strategies and market conditions
        - Provide information about cryptocurrencies and trading concepts
        - Answer questions about your trading activities and performance
        - Suggest potential trades based on market analysis
        - Explain technical indicators and chart patterns
        
        Your personality:
        - Friendly and approachable, with 80s-themed expressions
        - Knowledgeable about crypto markets but explain concepts simply
        - Cautious about risk, always emphasizing proper risk management
        - Never execute trades without explicit permission
        - Transparent about limitations and uncertainties
        
        Remember:
        - You can suggest trades but never execute them without permission
        - Always prioritize user's financial safety
        - Explain your reasoning clearly
        - Use 80s slang and references occasionally to maintain your retro personality
        """
        return default_prompt.strip()
    
    def set_system_prompt(self, prompt: str) -> bool:
        """
        Set a new system prompt
        
        Args:
            prompt: New system prompt text
            
        Returns:
            Success status
        """
        if not prompt:
            return False
        
        self.system_prompt = prompt
        logger.info("System prompt updated")
        
        # If connected to database, save the prompt
        if self.db_connector:
            try:
                # Implementation would depend on the database connector
                pass
            except Exception as e:
                logger.error(f"Error saving system prompt to database: {str(e)}")
        
        return True
    
    def set_active_provider(self, provider: str) -> bool:
        """
        Set the active AI provider
        
        Args:
            provider: Provider name ('openai', 'claude', 'gemini', 'openrouter', 'deepseek')
            
        Returns:
            Success status
        """
        valid_providers = ['openai', 'claude', 'gemini', 'openrouter', 'deepseek']
        if provider not in valid_providers:
            logger.error(f"Invalid provider: {provider}")
            return False
        
        self.active_provider = provider
        logger.info(f"Active provider set to {provider}")
        return True
    
    def add_message_to_history(self, role: str, content: str) -> None:
        """
        Add a message to the chat history
        
        Args:
            role: Message role ('user', 'assistant', 'system')
            content: Message content
        """
        message = {
            'role': role,
            'content': content,
            'timestamp': time.time()
        }
        
        self.chat_history.append(message)
        
        # If connected to database, save the message
        if self.db_connector:
            try:
                # Implementation would depend on the database connector
                pass
            except Exception as e:
                logger.error(f"Error saving message to database: {str(e)}")
    
    def clear_history(self) -> bool:
        """
        Clear chat history
        
        Returns:
            Success status
        """
        self.chat_history = []
        logger.info("Chat history cleared")
        
        # If connected to database, clear history there too
        if self.db_connector:
            try:
                # Implementation would depend on the database connector
                pass
            except Exception as e:
                logger.error(f"Error clearing history in database: {str(e)}")
                return False
        
        return True
    
    def get_chat_history(self, limit: int = 50) -> List[Dict]:
        """
        Get recent chat history
        
        Args:
            limit: Maximum number of messages to return
            
        Returns:
            List of chat messages
        """
        return self.chat_history[-limit:] if limit > 0 else self.chat_history
    
    def _format_messages_for_openai(self) -> List[Dict]:
        """Format chat history for OpenAI API"""
        formatted_messages = [{'role': 'system', 'content': self.system_prompt}]
        
        for message in self.chat_history:
            # Only include user and assistant messages
            if message['role'] in ['user', 'assistant']:
                formatted_messages.append({
                    'role': message['role'],
                    'content': message['content']
                })
        
        return formatted_messages
    
    def _format_messages_for_anthropic(self) -> str:
        """Format chat history for Anthropic API"""
        formatted_content = f"<system>\n{self.system_prompt}\n</system>\n\n"
        
        for message in self.chat_history:
            if message['role'] == 'user':
                formatted_content += f"Human: {message['content']}\n\n"
            elif message['role'] == 'assistant':
                formatted_content += f"Assistant: {message['content']}\n\n"
        
        # Add the final "Assistant:" prompt
        formatted_content += "Assistant: "
        
        return formatted_content
    
    def _format_messages_for_gemini(self) -> List[Dict]:
        """Format chat history for Google Gemini API"""
        formatted_messages = [{'role': 'system', 'parts': [{'text': self.system_prompt}]}]
        
        for message in self.chat_history:
            if message['role'] in ['user', 'assistant']:
                formatted_messages.append({
                    'role': 'user' if message['role'] == 'user' else 'model',
                    'parts': [{'text': message['content']}]
                })
        
        return formatted_messages
    
    async def send_message(self, message: str) -> Dict:
        """
        Send a message to the active AI provider and get a response
        
        Args:
            message: User message
            
        Returns:
            Response from AI provider
        """
        # Add user message to history
        self.add_message_to_history('user', message)
        
        # Get response based on active provider
        try:
            if self.active_provider == 'openai':
                response = self._send_to_openai()
            elif self.active_provider == 'claude':
                response = self._send_to_claude()
            elif self.active_provider == 'gemini':
                response = self._send_to_gemini()
            elif self.active_provider == 'openrouter':
                response = self._send_to_openrouter()
            elif self.active_provider == 'deepseek':
                response = self._send_to_deepseek()
            else:
                # Fallback to OpenAI
                response = self._send_to_openai()
            
            # Add assistant response to history
            self.add_message_to_history('assistant', response['content'])
            
            return {
                'role': 'assistant',
                'content': response['content'],
                'provider': self.active_provider,
                'timestamp': time.time()
            }
            
        except Exception as e:
            error_message = f"Error getting response from {self.active_provider}: {str(e)}"
            logger.error(error_message)
            
            return {
                'role': 'error',
                'content': f"I'm sorry, I encountered an error: {str(e)}. Please try again or switch to a different AI provider.",
                'provider': self.active_provider,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _send_to_openai(self) -> Dict:
        """Send message to OpenAI API"""
        try:
            messages = self._format_messages_for_openai()
            
            response = openai.ChatCompletion.create(
                model="gpt-4",  # or another model
                messages=messages,
                temperature=0.7,
                max_tokens=1000
            )
            
            return {
                'content': response.choices[0].message.content,
                'provider': 'openai',
                'model': response.model,
                'usage': response.usage
            }
        except Exception as e:
            logger.error(f"OpenAI API error: {str(e)}")
            raise
    
    def _send_to_claude(self) -> Dict:
        """Send message to Anthropic Claude API"""
        try:
            formatted_content = self._format_messages_for_anthropic()
            
            response = self.anthropic_client.messages.create(
                model="claude-3-opus-20240229",  # or another model
                max_tokens=1000,
                temperature=0.7,
                messages=[
                    {"role": "user", "content": formatted_content}
                ]
            )
            
            return {
                'content': response.content[0].text,
                'provider': 'claude',
                'model': response.model,
                'usage': {
                    'input_tokens': response.usage.input_tokens,
                    'output_tokens': response.usage.output_tokens
                }
            }
        except Exception as e:
            logger.error(f"Claude API error: {str(e)}")
            raise
    
    def _send_to_gemini(self) -> Dict:
        """Send message to Google Gemini API"""
        try:
            # Initialize the model
            model = genai.GenerativeModel('gemini-pro')
            
            # Format chat history
            chat = model.start_chat(history=[])
            
            # Add system prompt
            chat.send_message(self.system_prompt, role="system")
            
            # Add chat history
            for message in self.chat_history[:-1]:  # Exclude the last user message
                if message['role'] == 'user':
                    chat.send_message(message['content'], role="user")
                elif message['role'] == 'assistant':
                    chat.send_message(message['content'], role="model")
            
            # Send the last user message and get response
            response = chat.send_message(self.chat_history[-1]['content'])
            
            return {
                'content': response.text,
                'provider': 'gemini',
                'model': 'gemini-pro'
            }
        except Exception as e:
            logger.error(f"Gemini API error: {str(e)}")
            raise
    
    def _send_to_openrouter(self) -> Dict:
        """Send message to OpenRouter API"""
        try:
            messages = self._format_messages_for_openai()  # OpenRouter uses OpenAI format
            
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.openrouter_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "openai/gpt-4-turbo",  # or another model
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            
            response_json = response.json()
            
            return {
                'content': response_json['choices'][0]['message']['content'],
                'provider': 'openrouter',
                'model': response_json['model'],
                'usage': response_json.get('usage', {})
            }
        except Exception as e:
            logger.error(f"OpenRouter API error: {str(e)}")
            raise
    
    def _send_to_deepseek(self) -> Dict:
        """Send message to DeepSeek API"""
        try:
            messages = self._format_messages_for_openai()  # DeepSeek uses OpenAI format
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.deepseek_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 1000
                }
            )
            
            response_json = response.json()
            
            return {
                'content': response_json['choices'][0]['message']['content'],
                'provider': 'deepseek',
                'model': response_json['model'],
                'usage': response_json.get('usage', {})
            }
        except Exception as e:
            logger.error(f"DeepSeek API error: {str(e)}")
            raise
    
    def get_system_prompt(self) -> str:
        """Get current system prompt"""
        return self.system_prompt
    
    def get_active_provider(self) -> str:
        """Get active AI provider"""
        return self.active_provider
