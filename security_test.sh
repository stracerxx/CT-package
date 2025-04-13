#!/bin/bash

# CT-5 Crypto Trading Bot Security Test Script
echo "====================================="
echo "  CT-5 Security Test"
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

echo "Testing authentication security..."

# Test 1: Accessing protected endpoint without token
echo "Test 1: Accessing protected endpoint without token"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/keys)
if [ "$RESPONSE" -eq 401 ]; then
    echo "✅ Protected endpoint correctly returns 401 when accessed without token"
else
    echo "❌ Protected endpoint does not return 401 when accessed without token (got $RESPONSE)"
fi

# Test 2: Login with invalid credentials
echo "Test 2: Login with invalid credentials"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"invalid","password":"invalid"}' -o /dev/null -w "%{http_code}")
if [ "$RESPONSE" -eq 401 ]; then
    echo "✅ Login correctly returns 401 with invalid credentials"
else
    echo "❌ Login does not return 401 with invalid credentials (got $RESPONSE)"
fi

# Test 3: Get valid token
echo "Test 3: Get valid token"
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "✅ Successfully obtained valid token"
else
    echo "❌ Failed to obtain valid token"
    exit 1
fi

# Test 4: Access protected endpoint with valid token
echo "Test 4: Access protected endpoint with valid token"
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/keys)
if [ "$RESPONSE" -eq 200 ]; then
    echo "✅ Protected endpoint correctly returns 200 with valid token"
else
    echo "❌ Protected endpoint does not return 200 with valid token (got $RESPONSE)"
fi

# Test 5: Test for SQL injection in login
echo "Test 5: Test for SQL injection in login"
RESPONSE=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin\' OR 1=1--","password":"anything"}' -o /dev/null -w "%{http_code}")
if [ "$RESPONSE" -eq 401 ] || [ "$RESPONSE" -eq 422 ]; then
    echo "✅ Login is protected against basic SQL injection"
else
    echo "❌ Login might be vulnerable to SQL injection (got $RESPONSE)"
fi

echo "Testing trading functionality..."

# Test 6: Get market condition
echo "Test 6: Get market condition"
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/trading/market-condition)
if echo "$RESPONSE" | grep -q "score"; then
    echo "✅ Market condition endpoint returns score"
else
    echo "❌ Market condition endpoint does not return expected data"
fi

# Test 7: Get strategies
echo "Test 7: Get strategies"
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/trading/strategies)
if echo "$RESPONSE" | grep -q "strategies"; then
    echo "✅ Strategies endpoint returns data"
else
    echo "❌ Strategies endpoint does not return expected data"
fi

# Test 8: Toggle strategy
echo "Test 8: Toggle strategy"
RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/trading/strategies/grid/toggle -o /dev/null -w "%{http_code}")
if [ "$RESPONSE" -eq 200 ]; then
    echo "✅ Strategy toggle endpoint works"
else
    echo "❌ Strategy toggle endpoint does not work (got $RESPONSE)"
fi

echo "Testing chat functionality..."

# Test 9: Send chat message
echo "Test 9: Send chat message"
RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d '{"content":"Hello CT-5"}' \
    http://localhost:8000/api/chat/message -o /dev/null -w "%{http_code}")
if [ "$RESPONSE" -eq 200 ]; then
    echo "✅ Chat message endpoint works"
else
    echo "❌ Chat message endpoint does not work (got $RESPONSE)"
fi

# Test 10: Get chat history
echo "Test 10: Get chat history"
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/chat/history)
if echo "$RESPONSE" | grep -q "messages"; then
    echo "✅ Chat history endpoint returns messages"
else
    echo "❌ Chat history endpoint does not return expected data"
fi

# Test 11: Set AI provider
echo "Test 11: Set AI provider"
RESPONSE=$(curl -s -X POST -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/chat/provider/openai -o /dev/null -w "%{http_code}")
if [ "$RESPONSE" -eq 200 ]; then
    echo "✅ Set AI provider endpoint works"
else
    echo "❌ Set AI provider endpoint does not work (got $RESPONSE)"
fi

echo "Testing RSS feed functionality..."

# Test 12: Get RSS feeds
echo "Test 12: Get RSS feeds"
RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/rss)
if echo "$RESPONSE" | grep -q "CoinDesk"; then
    echo "✅ RSS feeds endpoint returns data"
else
    echo "❌ RSS feeds endpoint does not return expected data"
fi

# Test 13: Get RSS feed items
echo "Test 13: Get RSS feed items"
FEED_ID=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/rss | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)
if [ -n "$FEED_ID" ]; then
    RESPONSE=$(curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/rss/$FEED_ID/items -o /dev/null -w "%{http_code}")
    if [ "$RESPONSE" -eq 200 ]; then
        echo "✅ RSS feed items endpoint works"
    else
        echo "❌ RSS feed items endpoint does not work (got $RESPONSE)"
    fi
else
    echo "❌ Could not get RSS feed ID"
fi

echo "====================================="
echo "  Security Test Complete"
echo "====================================="
