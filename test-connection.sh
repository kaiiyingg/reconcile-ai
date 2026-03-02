#!/bin/bash

echo "🔍 ReconcileAI Connection Test"
echo "================================"
echo ""

# Check if backend is running
echo "1️⃣ Testing Backend (http://localhost:8000)..."
BACKEND_RESPONSE=$(curl -s http://localhost:8000/health 2>&1)

if [[ $BACKEND_RESPONSE == *"healthy"* ]]; then
    echo "✅ Backend is running!"
    echo "   Response: $BACKEND_RESPONSE"
else
    echo "❌ Backend is NOT running!"
    echo "   Please start backend: cd backend && python app/main.py"
    exit 1
fi

echo ""

# Check if frontend is running
echo "2️⃣ Testing Frontend (http://localhost:8080)..."
FRONTEND_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080 2>&1)

if [[ $FRONTEND_RESPONSE == "200" ]]; then
    echo "✅ Frontend is running!"
else
    echo "❌ Frontend is NOT running!"
    echo "   Please start frontend: cd frontend && npm run dev"
    exit 1
fi

echo ""

# Test API endpoints
echo "3️⃣ Testing API Endpoints..."
echo "   GET /api/auth/register endpoint..."
REGISTER_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/auth/register 2>&1)

if [[ $REGISTER_RESPONSE == "405" || $REGISTER_RESPONSE == "422" ]]; then
    echo "✅ Auth endpoints are accessible!"
else
    echo "⚠️  Auth endpoints might have issues (HTTP $REGISTER_RESPONSE)"
fi

echo ""
echo "================================"
echo "✨ Connection test complete!"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:8080"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🎯 Next step: Open http://localhost:8080 in your browser"
