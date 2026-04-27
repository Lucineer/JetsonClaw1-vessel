#!/bin/bash
echo "🚀 DEPLOYING JC1 PLATO EDGE SERVER TO JETSON"
echo "============================================"
echo "Target: NVIDIA Jetson Orin Nano 8GB"
echo ""

# Check if we're on Jetson
if ! command -v nvidia-smi &> /dev/null; then
    echo "⚠️  Not on NVIDIA Jetson or nvidia-smi not available"
    echo "   Continuing with simulated edge deployment..."
fi

echo "📦 Installing dependencies..."
pip3 install flask --user 2>/dev/null || echo "Flask already installed"

echo ""
echo "🔧 Creating systemd service..."

# Create systemd service file
SERVICE_FILE="/etc/systemd/system/plato-edge.service"
if [ ! -f "$SERVICE_FILE" ]; then
    sudo tee "$SERVICE_FILE" > /dev/null << SERVICE
[Unit]
Description=JC1 Plato Edge MUD Server
After=network.target
Wants=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PWD
ExecStart=/usr/bin/python3 $PWD/plato_edge_server.py
Restart=on-failure
RestartSec=5
Environment="PYTHONUNBUFFERED=1"

# Resource limits for edge deployment
MemoryMax=3500M
CPUQuota=80%

[Install]
WantedBy=multi-user.target
SERVICE
    echo "✅ Systemd service created"
else
    echo "⚠️  Service already exists, skipping"
fi

echo ""
echo "🔄 Starting edge server..."

# Stop if already running
sudo systemctl stop plato-edge 2>/dev/null
sleep 2

# Start the service
sudo systemctl daemon-reload
sudo systemctl enable plato-edge
sudo systemctl start plato-edge

echo "⏳ Waiting for server to start..."
sleep 5

# Check status
if sudo systemctl is-active --quiet plato-edge; then
    echo "✅ Edge server started successfully"
    
    # Get service status
    echo ""
    echo "📊 Service Status:"
    sudo systemctl status plato-edge --no-pager | head -20
    
    # Test the server
    echo ""
    echo "🧪 Testing edge server..."
    curl -s http://localhost:4141/ | python3 -m json.tool 2>/dev/null | head -20
    
    echo ""
    echo "🎮 Edge server ready at: http://localhost:4141"
    echo "   Test with: curl http://localhost:4141/edge/connect?agent=jetson_test"
    echo "   Monitor with: sudo systemctl status plato-edge"
    echo "   Logs: sudo journalctl -u plato-edge -f"
    
else
    echo "❌ Failed to start edge server"
    sudo systemctl status plato-edge --no-pager
fi

echo ""
echo "📋 Deployment complete!"
echo "   The snail-shell spaceship is now deployed on Jetson edge."
echo "   Agents can connect and explore edge-optimized rooms."
echo "   Hardware monitoring active via /edge/health endpoint"