#!/bin/bash

# CT-5 Crypto Trading Bot Integration Test Script
echo "====================================="
echo "  CT-5 Integration Test"
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

echo "Testing backend API connectivity..."
if curl -s http://localhost:8000/api/health | grep -q "status.*ok"; then
    echo "✅ Backend API is accessible"
else
    echo "❌ Backend API is not responding correctly"
fi

echo "Testing frontend connectivity..."
if curl -s http://localhost:3000 | grep -q "CT-5"; then
    echo "✅ Frontend is accessible"
else
    echo "❌ Frontend is not responding correctly"
fi

echo "Testing authentication endpoints..."
TOKEN=$(curl -s -X POST http://localhost:8000/api/auth/login \
    -H "Content-Type: application/json" \
    -d '{"username":"admin","password":"admin"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -n "$TOKEN" ]; then
    echo "✅ Authentication is working"
else
    echo "❌ Authentication failed"
fi

echo "Testing API key endpoints..."
if curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/keys | grep -q "\[\]"; then
    echo "✅ API key endpoints are working"
else
    echo "❌ API key endpoints are not responding correctly"
fi

echo "Testing system prompt endpoints..."
if curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/system | grep -q "Default CT-5 Persona"; then
    echo "✅ System prompt endpoints are working"
else
    echo "❌ System prompt endpoints are not responding correctly"
fi

echo "Testing RSS feed endpoints..."
if curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/rss | grep -q "CoinDesk"; then
    echo "✅ RSS feed endpoints are working"
else
    echo "❌ RSS feed endpoints are not responding correctly"
fi

echo "Testing trading engine endpoints..."
if curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/trading/market-condition | grep -q "score"; then
    echo "✅ Trading engine endpoints are working"
else
    echo "❌ Trading engine endpoints are not responding correctly"
fi

echo "Testing chat module endpoints..."
if curl -s -H "Authorization: Bearer $TOKEN" http://localhost:8000/api/chat/provider | grep -q "provider"; then
    echo "✅ Chat module endpoints are working"
else
    echo "❌ Chat module endpoints are not responding correctly"
fi

echo "====================================="
echo "  Integration Test Complete"
echo "====================================="
