#!/bin/bash

# CT-5 Crypto Trading Bot Functional Test Script
echo "====================================="
echo "  CT-5 Functional Test"
echo "====================================="

# Check if Docker and Docker Compose are installed
if ! command -v docker &> /dev/null || ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker and Docker Compose are required but not installed."
    echo "Please install Docker and Docker Compose first."
    exit 1
fi

# Check if containers are running
if ! docker-compose ps | grep -q "backend.*Up"; then
    echo "Error: CT-5 containers are not running."
    echo "Please run './setup.sh' first to set up the environment."
    exit 1
fi

# Get auth token
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "Error: Failed to obtain authentication token."
    exit 1
fi

echo "Testing trading strategies..."

# Test Grid Trading Strategy
echo "Test 1: Grid Trading Strategy"
RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "symbol": "BTC/USDT",
        "strategy": "grid",
        "parameters": {
            "upper_price": 70000,
            "lower_price": 60000,
            "grid_levels": 10,
            "investment_amount": 1000
        }
    }' \
    http://localhost:8000/api/trading/strategies/test)

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ Grid Trading Strategy test successful"
else
    echo "❌ Grid Trading Strategy test failed"
    echo "$RESPONSE"
fi

# Test Scalping Strategy
echo "Test 2: Scalping Strategy"
RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "symbol": "ETH/USDT",
        "strategy": "scalping",
        "parameters": {
            "take_profit_pct": 0.5,
            "stop_loss_pct": 0.3,
            "max_trades": 5,
            "trade_amount": 100
        }
    }' \
    http://localhost:8000/api/trading/strategies/test)

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ Scalping Strategy test successful"
else
    echo "❌ Scalping Strategy test failed"
    echo "$RESPONSE"
fi

# Test Swing Trading Strategy
echo "Test 3: Swing Trading Strategy"
RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "symbol": "SOL/USDT",
        "strategy": "swing",
        "parameters": {
            "entry_condition": "macd_crossover",
            "exit_condition": "take_profit",
            "take_profit_pct": 5,
            "stop_loss_pct": 3,
            "trade_amount": 200
        }
    }' \
    http://localhost:8000/api/trading/strategies/test)

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ Swing Trading Strategy test successful"
else
    echo "❌ Swing Trading Strategy test failed"
    echo "$RESPONSE"
fi

# Test DCA Strategy
echo "Test 4: DCA Strategy"
RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "symbol": "BTC/USDT",
        "strategy": "dca",
        "parameters": {
            "interval_days": 7,
            "investment_amount": 100,
            "total_periods": 10
        }
    }' \
    http://localhost:8000/api/trading/strategies/test)

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ DCA Strategy test successful"
else
    echo "❌ DCA Strategy test failed"
    echo "$RESPONSE"
fi

# Test Momentum Strategy
echo "Test 5: Momentum Strategy"
RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{
        "symbol": "ETH/USDT",
        "strategy": "momentum",
        "parameters": {
            "lookback_period": 14,
            "threshold": 0.5,
            "take_profit_pct": 4,
            "stop_loss_pct": 2,
            "trade_amount": 150
        }
    }' \
    http://localhost:8000/api/trading/strategies/test)

if echo "$RESPONSE" | grep -q "success"; then
    echo "✅ Momentum Strategy test successful"
else
    echo "❌ Momentum Strategy test failed"
    echo "$RESPONSE"
fi

echo "Testing chat functionality with different providers..."

# Test OpenAI provider
echo "Test 6: OpenAI Chat Provider"
curl -s -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/chat/provider/openai > /dev/null

RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"content":"What is Bitcoin?"}' \
    http://localhost:8000/api/chat/message)

if echo "$RESPONSE" | grep -q "content"; then
    echo "✅ OpenAI Chat Provider test successful"
else
    echo "❌ OpenAI Chat Provider test failed"
    echo "$RESPONSE"
fi

# Test Claude provider
echo "Test 7: Claude Chat Provider"
curl -s -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/chat/provider/claude > /dev/null

RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"content":"Explain Ethereum."}' \
    http://localhost:8000/api/chat/message)

if echo "$RESPONSE" | grep -q "content"; then
    echo "✅ Claude Chat Provider test successful"
else
    echo "❌ Claude Chat Provider test failed"
    echo "$RESPONSE"
fi

# Test chat history
echo "Test 8: Chat History"
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/chat/history)

if echo "$RESPONSE" | grep -q "messages"; then
    echo "✅ Chat History test successful"
else
    echo "❌ Chat History test failed"
    echo "$RESPONSE"
fi

# Test clear chat history
echo "Test 9: Clear Chat History"
RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/chat/clear -o /dev/null -w "%{http_code}")

if [ "$RESPONSE" -eq 204 ]; then
    echo "✅ Clear Chat History test successful"
else
    echo "❌ Clear Chat History test failed (got $RESPONSE)"
fi

echo "Testing Perpetual Earning Mode..."

# Test toggle Perpetual Mode
echo "Test 10: Toggle Perpetual Mode"
RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/trading/perpetual-mode/toggle -o /dev/null -w "%{http_code}")

if [ "$RESPONSE" -eq 200 ]; then
    echo "✅ Toggle Perpetual Mode test successful"
else
    echo "❌ Toggle Perpetual Mode test failed (got $RESPONSE)"
fi

# Test market condition analysis
echo "Test 11: Market Condition Analysis"
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/trading/market-condition)

if echo "$RESPONSE" | grep -q "score"; then
    echo "✅ Market Condition Analysis test successful"
    echo "   Market Condition Score: $(echo "$RESPONSE" | grep -o '"score":[0-9]*' | cut -d':' -f2)"
else
    echo "❌ Market Condition Analysis test failed"
    echo "$RESPONSE"
fi

echo "====================================="
echo "  Functional Test Complete"
echo "====================================="
