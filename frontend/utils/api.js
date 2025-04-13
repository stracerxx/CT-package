import React, { useState, useEffect } from 'react';
import axios from 'axios';

// API service for handling all backend requests
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Add auth token to all requests
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);

// Handle token expiration
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // Clear token and redirect to login
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const login = async (username, password) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
      username,
      password
    });
    
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
      return { success: true, data: response.data };
    }
    
    return { success: false, error: 'Invalid credentials' };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Login failed' 
    };
  }
};

export const register = async (username, email, password) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/auth/register`, {
      username,
      email,
      password
    });
    
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Registration failed' 
    };
  }
};

export const logout = () => {
  localStorage.removeItem('token');
  window.location.href = '/login';
};

// Trading API
export const getMarketCondition = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/trading/market-condition`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to get market condition' 
    };
  }
};

export const getActiveTrades = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/trading/active-trades`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to get active trades' 
    };
  }
};

export const getStrategies = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/trading/strategies`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to get strategies' 
    };
  }
};

export const toggleStrategy = async (strategy) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/trading/strategies/${strategy}/toggle`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || `Failed to toggle ${strategy} strategy` 
    };
  }
};

export const togglePerpetualMode = async () => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/trading/perpetual-mode/toggle`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to toggle perpetual mode' 
    };
  }
};

// Chat API
export const sendChatMessage = async (content) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/chat/message`, { content });
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to send message' 
    };
  }
};

export const getChatHistory = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/chat/history`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to get chat history' 
    };
  }
};

export const clearChatHistory = async () => {
  try {
    await axios.post(`${API_BASE_URL}/api/chat/clear`);
    return { success: true };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to clear chat history' 
    };
  }
};

export const setAiProvider = async (provider) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/chat/provider/${provider}`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || `Failed to set AI provider to ${provider}` 
    };
  }
};

export const getAiProvider = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/chat/provider`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to get AI provider' 
    };
  }
};

// RSS Feed API
export const getRssFeeds = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/rss`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to get RSS feeds' 
    };
  }
};

export const getRssFeedItems = async (feedId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/rss/${feedId}/items`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to get RSS feed items' 
    };
  }
};

export const refreshRssFeed = async (feedId) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/rss/${feedId}/refresh`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to refresh RSS feed' 
    };
  }
};

// Admin API
export const getUsers = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/auth/users`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to get users' 
    };
  }
};

export const getApiKeys = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/keys`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to get API keys' 
    };
  }
};

export const addApiKey = async (service, apiKey) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/keys`, {
      service,
      api_key: apiKey
    });
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to add API key' 
    };
  }
};

export const deleteApiKey = async (service) => {
  try {
    await axios.delete(`${API_BASE_URL}/api/keys/${service}`);
    return { success: true };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to delete API key' 
    };
  }
};

export const getSystemPrompts = async () => {
  try {
    const response = await axios.get(`${API_BASE_URL}/api/system`);
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to get system prompts' 
    };
  }
};

export const addSystemPrompt = async (name, content, isActive) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/system`, {
      name,
      content,
      is_active: isActive
    });
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to add system prompt' 
    };
  }
};

export const setActiveSystemPrompt = async (id) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/api/system/${id}`, {
      is_active: true
    });
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to set active system prompt' 
    };
  }
};

export const deleteSystemPrompt = async (id) => {
  try {
    await axios.delete(`${API_BASE_URL}/api/system/${id}`);
    return { success: true };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to delete system prompt' 
    };
  }
};

export const addRssFeed = async (name, url, category) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/api/rss`, {
      name,
      url,
      category
    });
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to add RSS feed' 
    };
  }
};

export const toggleRssFeedStatus = async (id, isActive) => {
  try {
    const response = await axios.put(`${API_BASE_URL}/api/rss/${id}`, {
      is_active: !isActive
    });
    return { success: true, data: response.data };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to toggle RSS feed status' 
    };
  }
};

export const deleteRssFeed = async (id) => {
  try {
    await axios.delete(`${API_BASE_URL}/api/rss/${id}`);
    return { success: true };
  } catch (error) {
    return { 
      success: false, 
      error: error.response?.data?.detail || 'Failed to delete RSS feed' 
    };
  }
};
