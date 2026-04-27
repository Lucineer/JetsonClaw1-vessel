#!/bin/bash
# Plato Harvest Server Deployment Script

set -e

echo "🚀 DEPLOYING PLATO HARVEST SERVER"
echo "================================="

# Check Python
echo "🔍 Checking Python..."
python3 --version || { echo "❌ Python3 not found"; exit 1; }

# Check dependencies
echo "🔍 Checking dependencies..."
if ! python3 -c "import flask" 2>/dev/null; then
    echo "📦 Installing Flask..."
    pip install flask || { echo "❌ Failed to install Flask"; exit 1; }
fi

# Create directories
echo "📁 Creating directories..."
mkdir -p harvested_tiles
mkdir -p logs

# Test the server
echo "🧪 Testing server..."
python3 plato_harvest_server.py --test 2>&1 | tee logs/test.log

if [ $? -eq 0 ]; then
    echo "✅ Test passed!"
else
    echo "❌ Test failed. Check logs/test.log"
    exit 1
fi

# Get local IP
LOCAL_IP=$(hostname -I | awk '{print $1}' 2>/dev/null || echo "localhost")
PORT=8080

echo ""
echo "🎯 DEPLOYMENT READY"
echo "=================="
echo ""
echo "📊 SERVER ENDPOINTS:"
echo "  Dashboard:      http://$LOCAL_IP:$PORT/dashboard"
echo "  Prompt:         http://$LOCAL_IP:$PORT/prompt/innocent_exploration"
echo "  Explore (POST): http://$LOCAL_IP:$PORT/explore"
echo "  Export:         http://$LOCAL_IP:$PORT/export"
echo ""
echo "🎯 KIMI SWARM PROMPTS:"
echo "  1. Innocent Exploration (default)"
echo "  2. Compounding Intelligence (sequential)"
echo "  3. Parallel Swarm (specialized)"
echo ""
echo "🔧 START SERVER:"
echo "  python3 plato_harvest_server.py --host 0.0.0.0 --port $PORT"
echo ""
echo "📝 USAGE:"
echo "  1. Get prompt from /prompt endpoint"
echo "  2. Give to Kimi K2.5 agent"
echo "  3. When Kimi explores, POST to /explore"
echo "  4. Watch tiles harvest on /dashboard"
echo "  5. Export training data with /export"
echo ""
echo "🦀 THE SHELL AWAITS THE CRABS"
echo "=============================="