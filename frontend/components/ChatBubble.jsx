import React, { useState, useEffect, useRef } from 'react';
import styled from 'styled-components';
import axios from 'axios';

// Styled components for the chat bubble
const ChatBubbleContainer = styled.div`
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 1000;
  font-family: 'Press Start 2P', cursive;
`;

const ChatBubbleButton = styled.button`
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background-color: #ff6b6b;
  border: 4px solid #333;
  color: white;
  font-size: 24px;
  cursor: pointer;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  
  &:hover {
    transform: scale(1.1);
    box-shadow: 0 6px 12px rgba(0, 0, 0, 0.4);
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

const ChatWindow = styled.div`
  position: absolute;
  bottom: 80px;
  right: 0;
  width: 350px;
  height: 500px;
  background-color: #222;
  border: 4px solid #ff6b6b;
  border-radius: 10px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const ChatHeader = styled.div`
  background-color: #ff6b6b;
  color: white;
  padding: 10px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
`;

const ChatMessages = styled.div`
  flex: 1;
  padding: 10px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 10px;
  background-color: #111;
  
  &::-webkit-scrollbar {
    width: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: #222;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #ff6b6b;
    border-radius: 4px;
  }
`;

const MessageBubble = styled.div`
  max-width: 80%;
  padding: 10px;
  border-radius: 8px;
  font-size: 12px;
  line-height: 1.4;
  font-family: 'VT323', monospace;
  
  ${props => props.isUser ? `
    align-self: flex-end;
    background-color: #4a6fa5;
    color: white;
    border-bottom-right-radius: 0;
  ` : `
    align-self: flex-start;
    background-color: #444;
    color: #00ff00;
    border-bottom-left-radius: 0;
  `}
`;

const ChatInputContainer = styled.div`
  padding: 10px;
  background-color: #333;
  display: flex;
  gap: 10px;
`;

const ChatInput = styled.input`
  flex: 1;
  padding: 10px;
  border: 2px solid #ff6b6b;
  border-radius: 4px;
  background-color: #222;
  color: white;
  font-family: 'VT323', monospace;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #00ff00;
  }
`;

const SendButton = styled.button`
  padding: 8px 16px;
  background-color: #ff6b6b;
  border: none;
  border-radius: 4px;
  color: white;
  cursor: pointer;
  font-family: 'Press Start 2P', cursive;
  font-size: 12px;
  
  &:hover {
    background-color: #ff8787;
  }
  
  &:active {
    transform: scale(0.95);
  }
`;

const ProviderSelector = styled.select`
  padding: 5px;
  background-color: #333;
  color: white;
  border: 2px solid #ff6b6b;
  border-radius: 4px;
  font-family: 'VT323', monospace;
  font-size: 12px;
  
  &:focus {
    outline: none;
  }
`;

const ChatBubble = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [provider, setProvider] = useState('openai');
  const messagesEndRef = useRef(null);

  // Scroll to bottom of messages
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Fetch chat history when opened
  useEffect(() => {
    if (isOpen) {
      fetchChatHistory();
      fetchCurrentProvider();
    }
  }, [isOpen]);

  const fetchChatHistory = async () => {
    try {
      const response = await axios.get('/api/chat/history');
      setMessages(response.data.messages);
    } catch (error) {
      console.error('Error fetching chat history:', error);
      // Add error message
      setMessages([
        ...messages,
        {
          role: 'assistant',
          content: 'Error loading chat history. Please try again.',
          timestamp: Date.now() / 1000
        }
      ]);
    }
  };

  const fetchCurrentProvider = async () => {
    try {
      const response = await axios.get('/api/chat/provider');
      setProvider(response.data.provider);
    } catch (error) {
      console.error('Error fetching current provider:', error);
    }
  };

  const handleSendMessage = async () => {
    if (!inputValue.trim()) return;
    
    // Add user message to UI immediately
    const userMessage = {
      role: 'user',
      content: inputValue,
      timestamp: Date.now() / 1000
    };
    
    setMessages([...messages, userMessage]);
    setInputValue('');
    setIsLoading(true);
    
    try {
      // Send message to API
      const response = await axios.post('/api/chat/message', {
        content: userMessage.content
      });
      
      // Add assistant response
      setMessages(prevMessages => [
        ...prevMessages,
        {
          role: response.data.role,
          content: response.data.content,
          timestamp: response.data.timestamp
        }
      ]);
    } catch (error) {
      console.error('Error sending message:', error);
      // Add error message
      setMessages(prevMessages => [
        ...prevMessages,
        {
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: Date.now() / 1000
        }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSendMessage();
    }
  };

  const handleProviderChange = async (e) => {
    const newProvider = e.target.value;
    setProvider(newProvider);
    
    try {
      await axios.post(`/api/chat/provider/${newProvider}`);
      
      // Add system message about provider change
      setMessages([
        ...messages,
        {
          role: 'system',
          content: `Switched to ${newProvider} AI provider.`,
          timestamp: Date.now() / 1000
        }
      ]);
    } catch (error) {
      console.error('Error changing provider:', error);
      // Add error message
      setMessages([
        ...messages,
        {
          role: 'system',
          content: `Failed to switch to ${newProvider}. Please try again.`,
          timestamp: Date.now() / 1000
        }
      ]);
    }
  };

  const clearChat = async () => {
    try {
      await axios.post('/api/chat/clear');
      setMessages([
        {
          role: 'assistant',
          content: 'Chat history cleared. How can I help you today?',
          timestamp: Date.now() / 1000
        }
      ]);
    } catch (error) {
      console.error('Error clearing chat:', error);
    }
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <ChatBubbleContainer>
      {isOpen && (
        <ChatWindow>
          <ChatHeader>
            <span>CT-5 ASSISTANT</span>
            <div>
              <ProviderSelector value={provider} onChange={handleProviderChange}>
                <option value="openai">OpenAI</option>
                <option value="claude">Claude</option>
                <option value="gemini">Gemini</option>
                <option value="openrouter">OpenRouter</option>
                <option value="deepseek">DeepSeek</option>
              </ProviderSelector>
              <button onClick={clearChat} style={{ marginLeft: '5px', background: 'none', border: 'none', color: 'white', cursor: 'pointer' }}>
                🗑️
              </button>
            </div>
          </ChatHeader>
          
          <ChatMessages>
            {messages.length === 0 && (
              <MessageBubble>
                Hello! I'm CT-5, your crypto trading assistant. How can I help you today?
              </MessageBubble>
            )}
            
            {messages.map((message, index) => (
              <MessageBubble key={index} isUser={message.role === 'user'}>
                {message.content}
                <div style={{ fontSize: '10px', marginTop: '4px', opacity: 0.7, textAlign: 'right' }}>
                  {formatTimestamp(message.timestamp)}
                </div>
              </MessageBubble>
            ))}
            
            {isLoading && (
              <MessageBubble>
                <div style={{ display: 'flex', gap: '4px', justifyContent: 'center' }}>
                  <div className="dot" style={{ animation: 'pulse 1s infinite' }}>.</div>
                  <div className="dot" style={{ animation: 'pulse 1s infinite 0.2s' }}>.</div>
                  <div className="dot" style={{ animation: 'pulse 1s infinite 0.4s' }}>.</div>
                </div>
              </MessageBubble>
            )}
            
            <div ref={messagesEndRef} />
          </ChatMessages>
          
          <ChatInputContainer>
            <ChatInput
              type="text"
              placeholder="Type your message..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <SendButton onClick={handleSendMessage} disabled={isLoading}>
              SEND
            </SendButton>
          </ChatInputContainer>
        </ChatWindow>
      )}
      
      <ChatBubbleButton onClick={() => setIsOpen(!isOpen)}>
        {isOpen ? '×' : '?'}
      </ChatBubbleButton>
    </ChatBubbleContainer>
  );
};

export default ChatBubble;
