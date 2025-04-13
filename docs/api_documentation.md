# CT-5 Crypto Trading Bot - API Documentation

## Overview

This document provides detailed information about the API endpoints available in the CT-5 crypto trading bot application. The API is built with FastAPI and follows RESTful principles.

## Base URL

All API endpoints are prefixed with `/api`.

## Authentication

Most endpoints require authentication using JWT (JSON Web Token). To authenticate:

1. Obtain a token by sending a POST request to `/api/auth/login`
2. Include the token in the Authorization header of subsequent requests:
   `Authorization: Bearer {your_token}`

## Endpoints

### Authentication

#### Login

- **URL**: `/api/auth/login`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "username": "string",
    "password": "string"
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "access_token": "string",
      "token_type": "bearer"
    }
    ```
- **Error Response**:
  - **Code**: 401
  - **Content**:
    ```json
    {
      "detail": "Incorrect username or password"
    }
    ```

#### Register

- **URL**: `/api/auth/register`
- **Method**: `POST`
- **Auth Required**: No
- **Request Body**:
  ```json
  {
    "username": "string",
    "email": "string",
    "password": "string"
  }
  ```
- **Success Response**:
  - **Code**: 201
  - **Content**:
    ```json
    {
      "id": "integer",
      "username": "string",
      "email": "string",
      "is_active": true
    }
    ```
- **Error Response**:
  - **Code**: 400
  - **Content**:
    ```json
    {
      "detail": "Username already registered"
    }
    ```

#### Get Users (Admin only)

- **URL**: `/api/auth/users`
- **Method**: `GET`
- **Auth Required**: Yes (Admin)
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    [
      {
        "id": "integer",
        "username": "string",
        "email": "string",
        "is_active": true,
        "is_admin": false
      }
    ]
    ```

### API Keys

#### Get API Keys

- **URL**: `/api/keys`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    [
      {
        "id": "integer",
        "service": "string",
        "api_key": "string",
        "is_active": true
      }
    ]
    ```

#### Add API Key

- **URL**: `/api/keys`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "service": "string",
    "api_key": "string"
  }
  ```
- **Success Response**:
  - **Code**: 201
  - **Content**:
    ```json
    {
      "id": "integer",
      "service": "string",
      "api_key": "string",
      "is_active": true
    }
    ```

#### Delete API Key

- **URL**: `/api/keys/{service}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 204
  - **Content**: None

### System Prompts

#### Get System Prompts

- **URL**: `/api/system`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    [
      {
        "id": "integer",
        "name": "string",
        "content": "string",
        "is_active": true
      }
    ]
    ```

#### Add System Prompt

- **URL**: `/api/system`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "name": "string",
    "content": "string",
    "is_active": false
  }
  ```
- **Success Response**:
  - **Code**: 201
  - **Content**:
    ```json
    {
      "id": "integer",
      "name": "string",
      "content": "string",
      "is_active": true
    }
    ```

#### Update System Prompt

- **URL**: `/api/system/{id}`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "name": "string",
    "content": "string",
    "is_active": true
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "id": "integer",
      "name": "string",
      "content": "string",
      "is_active": true
    }
    ```

#### Delete System Prompt

- **URL**: `/api/system/{id}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 204
  - **Content**: None

### RSS Feeds

#### Get RSS Feeds

- **URL**: `/api/rss`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    [
      {
        "id": "integer",
        "name": "string",
        "url": "string",
        "category": "string",
        "is_active": true
      }
    ]
    ```

#### Add RSS Feed

- **URL**: `/api/rss`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "name": "string",
    "url": "string",
    "category": "string"
  }
  ```
- **Success Response**:
  - **Code**: 201
  - **Content**:
    ```json
    {
      "id": "integer",
      "name": "string",
      "url": "string",
      "category": "string",
      "is_active": true
    }
    ```

#### Get RSS Feed Items

- **URL**: `/api/rss/{id}/items`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    [
      {
        "id": "integer",
        "title": "string",
        "description": "string",
        "link": "string",
        "published_date": "string"
      }
    ]
    ```

#### Refresh RSS Feed

- **URL**: `/api/rss/{id}/refresh`
- **Method**: `POST`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "status": "success",
      "items_count": "integer"
    }
    ```

#### Update RSS Feed

- **URL**: `/api/rss/{id}`
- **Method**: `PUT`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "name": "string",
    "url": "string",
    "category": "string",
    "is_active": true
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "id": "integer",
      "name": "string",
      "url": "string",
      "category": "string",
      "is_active": true
    }
    ```

#### Delete RSS Feed

- **URL**: `/api/rss/{id}`
- **Method**: `DELETE`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 204
  - **Content**: None

### Trading

#### Get Market Condition

- **URL**: `/api/trading/market-condition`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "score": "integer",
      "is_trading_active": true,
      "indicators": {
        "trend": "string",
        "volatility": "string",
        "momentum": "string"
      }
    }
    ```

#### Get Active Trades

- **URL**: `/api/trading/active-trades`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "trades": [
        {
          "id": "string",
          "symbol": "string",
          "strategy": "string",
          "side": "string",
          "amount": "number",
          "entry_price": "number",
          "current_price": "number",
          "entry_time": "string"
        }
      ]
    }
    ```

#### Get Strategies

- **URL**: `/api/trading/strategies`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "strategies": {
        "grid": true,
        "scalping": false,
        "swing": true,
        "dca": true,
        "momentum": false
      }
    }
    ```

#### Toggle Strategy

- **URL**: `/api/trading/strategies/{strategy}/toggle`
- **Method**: `POST`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "strategy": "string",
      "active": true
    }
    ```

#### Toggle Perpetual Mode

- **URL**: `/api/trading/perpetual-mode/toggle`
- **Method**: `POST`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "perpetual_mode": true
    }
    ```

#### Test Strategy

- **URL**: `/api/trading/strategies/test`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "symbol": "string",
    "strategy": "string",
    "parameters": {
      "key1": "value1",
      "key2": "value2"
    }
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "success": true,
      "strategy": "string",
      "results": {
        "key1": "value1",
        "key2": "value2"
      }
    }
    ```

### Chat

#### Send Message

- **URL**: `/api/chat/message`
- **Method**: `POST`
- **Auth Required**: Yes
- **Request Body**:
  ```json
  {
    "content": "string"
  }
  ```
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "role": "assistant",
      "content": "string",
      "provider": "string",
      "timestamp": "number"
    }
    ```

#### Get Chat History

- **URL**: `/api/chat/history`
- **Method**: `GET`
- **Auth Required**: Yes
- **Query Parameters**:
  - `limit`: integer (optional, default=50)
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "messages": [
        {
          "role": "string",
          "content": "string",
          "timestamp": "number"
        }
      ],
      "count": "integer"
    }
    ```

#### Clear Chat History

- **URL**: `/api/chat/clear`
- **Method**: `POST`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 204
  - **Content**: None

#### Set AI Provider

- **URL**: `/api/chat/provider/{provider}`
- **Method**: `POST`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "provider": "string",
      "timestamp": "number"
    }
    ```

#### Get AI Provider

- **URL**: `/api/chat/provider`
- **Method**: `GET`
- **Auth Required**: Yes
- **Success Response**:
  - **Code**: 200
  - **Content**:
    ```json
    {
      "provider": "string",
      "timestamp": "number"
    }
    ```

## Status Codes

- 200: OK
- 201: Created
- 204: No Content
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Unprocessable Entity
- 500: Internal Server Error

## Error Handling

All errors return a JSON object with a `detail` field containing the error message:

```json
{
  "detail": "Error message"
}
```

## Rate Limiting

The API implements rate limiting to prevent abuse. Clients are limited to 100 requests per minute. When the rate limit is exceeded, the API returns a 429 Too Many Requests response.

## CORS

Cross-Origin Resource Sharing (CORS) is enabled for the frontend URL specified in the environment variables.
