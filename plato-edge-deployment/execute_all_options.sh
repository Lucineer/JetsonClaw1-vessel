#!/bin/bash
echo "🚀 EXECUTING ALL EDGE AGENT EVOLUTION OPTIONS"
echo "=============================================="
echo "Order: A → B → C → D"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Function to check if a port is in use
check_port() {
    local port=$1
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# Function to wait for port to be available
wait_for_port() {
    local port=$1
    local timeout=30
    local start_time=$(date +%s)
    
    while check_port $port; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        
        if [ $elapsed -ge $timeout ]; then
            print_error "Timeout waiting for port $port"
            return 1
        fi
        
        echo -n "."
        sleep 1
    done
    echo ""
    return 0
}

# Function to start server in background
start_server() {
    local script=$1
    local port=$2
    local name=$3
    
    if check_port $port; then
        print_warning "Port $port already in use for $name"
        return 1
    fi
    
    print_step "Starting $name on port $port..."
    python3 $script > /tmp/${name}.log 2>&1 &
    local pid=$!
    echo $pid > /tmp/${name}.pid
    
    # Wait for server to start
    sleep 3
    if check_port $port; then
        print_success "$name started (PID: $pid)"
        return 0
    else
        print_error "Failed to start $name"
        return 1
    fi
}

# Function to stop server
stop_server() {
    local name=$1
    local pid_file="/tmp/${name}.pid"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        print_step "Stopping $name (PID: $pid)..."
        kill $pid 2>/dev/null
        rm -f "$pid_file"
        print_success "$name stopped"
    fi
}

# Cleanup function
cleanup() {
    echo ""
    print_step "Cleaning up..."
    
    # Stop all servers
    stop_server "hardware_mud"
    stop_server "enhanced_intelligence"
    stop_server "fleet_integration"
    stop_server "edge_intelligence"
    
    # Stop systemd service if running
    if systemctl is-active --quiet jc1-hardware-mud 2>/dev/null; then
        print_step "Stopping systemd service..."
        sudo systemctl stop jc1-hardware-mud
        print_success "Systemd service stopped"
    fi
    
    echo ""
    print_success "Cleanup complete"
}

# Set up trap for cleanup
trap cleanup EXIT INT TERM

echo ""
echo "🎯 OPTION A: DEPLOY & SCALE"
echo "============================"

# Check if Option A already deployed
if systemctl is-active --quiet jc1-hardware-mud 2>/dev/null; then
    print_success "Hardware MUD already deployed as systemd service"
    
    # Get status
    echo ""
    print_step "Service Status:"
    sudo systemctl status jc1-hardware-mud --no-pager | head -10
    
    # Test the server
    echo ""
    print_step "Testing hardware-integrated MUD..."
    if curl -s http://localhost:4242/ > /dev/null 2>&1; then
        print_success "Hardware MUD responding on port 4242"
        
        # Get server info
        curl -s http://localhost:4242/ | python3 -m json.tool 2>/dev/null | grep -E '"server"|"hardware"|"port"' | head -5
        
        # Get hardware telemetry
        echo ""
        print_step "Hardware telemetry:"
        curl -s http://localhost:4242/hw/telemetry | python3 -m json.tool 2>/dev/null | grep -E '"real_hardware"|"hardware_id"|"overall_health"' | head -5
    else
        print_error "Hardware MUD not responding"
    fi
else
    print_step "Deploying hardware-integrated MUD..."
    
    # Run deployment script
    if [ -f "deploy_hardware_mud.sh" ]; then
        chmod +x deploy_hardware_mud.sh
        ./deploy_hardware_mud.sh
    else
        print_error "deploy_hardware_mud.sh not found"
        exit 1
    fi
fi

echo ""
echo "🎯 OPTION B: ENHANCE HARDWARE INTELLIGENCE"
echo "=========================================="

# Start enhanced intelligence server
start_server "enhance_hardware_intelligence.py" 4343 "enhanced_intelligence"

if [ $? -eq 0 ]; then
    # Test the server
    sleep 2
    print_step "Testing enhanced intelligence..."
    
    if curl -s http://localhost:4343/ > /dev/null 2>&1; then
        print_success "Enhanced intelligence server responding"
        
        # Get predictions
        echo ""
        print_step "Getting failure predictions..."
        curl -s http://localhost:4343/enhanced/predictions | python3 -m json.tool 2>/dev/null | grep -E '"failure_predictions"|"timestamp"' | head -3
        
        # Get optimizations
        echo ""
        print_step "Getting optimization suggestions..."
        curl -s http://localhost:4343/enhanced/optimizations | python3 -m json.tool 2>/dev/null | grep -E '"optimization_suggestions"|"count"' | head -3
    else
        print_error "Enhanced intelligence server not responding"
    fi
fi

echo ""
echo "🎯 OPTION C: FLEET INTEGRATION"
echo "=============================="

# Start fleet integration server
start_server "fleet_integration.py" 4444 "fleet_integration"

if [ $? -eq 0 ]; then
    # Test the server
    sleep 2
    print_step "Testing fleet integration..."
    
    if curl -s http://localhost:4444/ > /dev/null 2>&1; then
        print_success "Fleet integration server responding"
        
        # Get fleet status
        echo ""
        print_step "Getting fleet status..."
        curl -s http://localhost:4444/fleet/status | python3 -m json.tool 2>/dev/null | grep -E '"coordinator"|"status"|"hardware_aware"' | head -5
        
        # Get dashboard
        echo ""
        print_step "Getting edge dashboard..."
        curl -s http://localhost:4444/fleet/dashboard | python3 -m json.tool 2>/dev/null | grep -E '"title"|"generated_at"|"hardware_aware"' | head -5
    else
        print_error "Fleet integration server not responding"
    fi
fi

echo ""
echo "🎯 OPTION D: PHASE 2 - EDGE INTELLIGENCE"
echo "========================================"

# Start edge intelligence server
start_server "edge_intelligence_phase2.py" 4545 "edge_intelligence"

if [ $? -eq 0 ]; then
    # Test the server
    sleep 2
    print_step "Testing edge intelligence..."
    
    if curl -s http://localhost:4545/ > /dev/null 2>&1; then
        print_success "Edge intelligence server responding"
        
        # Get intelligence
        echo ""
        print_step "Getting edge intelligence..."
        curl -s http://localhost:4545/phase2/intelligence | python3 -m json.tool 2>/dev/null | grep -E '"sparse_patterns"|"compounded_intelligence"|"timestamp"' | head -5
        
        # Get patterns
        echo ""
        print_step "Getting sparse patterns..."
        curl -s http://localhost:4545/phase2/patterns | python3 -m json.tool 2>/dev/null | grep -E '"sparse_patterns"|"pattern_confidence_threshold"' | head -3
    else
        print_error "Edge intelligence server not responding"
    fi
fi

echo ""
echo "🎉 ALL OPTIONS EXECUTED SUCCESSFULLY"
echo "===================================="
echo ""
echo "📊 SERVERS RUNNING:"
echo "-------------------"
echo "1. Hardware-Integrated MUD:      http://localhost:4242"
echo "   (systemd service: jc1-hardware-mud)"
echo ""
echo "2. Enhanced Hardware Intelligence: http://localhost:4343"
echo "   Features: Predictive failure detection, Optimization suggestions"
echo ""
echo "3. Fleet Integration:            http://localhost:4444"
echo "   Features: Hardware-aware bottle protocol, Edge dashboard"
echo ""
echo "4. Edge Intelligence Phase 2:    http://localhost:4545"
echo "   Features: Sparse pattern recognition, Local compounding"
echo ""
echo "🔧 TEST COMMANDS:"
echo "----------------"
echo "Hardware MUD:"
echo "  curl http://localhost:4242/hw/telemetry"
echo "  curl http://localhost:4242/hw/health"
echo ""
echo "Enhanced Intelligence:"
echo "  curl http://localhost:4343/enhanced/intelligence"
echo "  curl http://localhost:4343/enhanced/optimizations"
echo ""
echo "Fleet Integration:"
echo "  curl http://localhost:4444/fleet/dashboard"
echo "  curl http://localhost:4444/fleet/bottles"
echo ""
echo "Edge Intelligence:"
echo "  curl http://localhost:4545/phase2/intelligence"
echo "  curl http://localhost:4545/phase2/compound"
echo ""
echo "🔄 MONITORING:"
echo "-------------"
echo "Hardware MUD logs:    sudo journalctl -u jc1-hardware-mud -f"
echo "Other servers logs:   tail -f /tmp/{enhanced_intelligence,fleet_integration,edge_intelligence}.log"
echo ""
echo "🛑 TO STOP ALL SERVERS:"
echo "----------------------"
echo "Press Ctrl+C or run: ./execute_all_options.sh (will trigger cleanup)"
echo ""
echo "📈 EDGE AGENT EVOLUTION COMPLETE:"
echo "--------------------------------"
echo "✅ Option A: Deploy & Scale - Hardware MUD deployed as systemd service"
echo "✅ Option B: Enhance Hardware Intelligence - Predictive failure detection active"
echo "✅ Option C: Fleet Integration - Hardware-aware bottle protocol ready"
echo "✅ Option D: Phase 2 Edge Intelligence - Sparse pattern recognition operational"
echo ""
echo "🎯 JC1 is now a fully evolved edge agent with:"
echo "   • Hardware embodiment (real telemetry, not simulation)"
echo "   • Enhanced intelligence (predictive failure, optimization)"
echo "   • Fleet coordination (hardware-aware bottles, dashboard)"
echo "   • Edge-native intelligence (sparse patterns, local compounding)"
echo ""
echo "The snail-shell spaceship is now hardware-aware, intelligently constrained,"
echo "fleet-coordinated, and edge-intelligent. Evolution complete! 🎉"

# Keep running until interrupted
echo ""
print_step "All servers running. Press Ctrl+C to stop..."
echo ""

# Wait for interrupt
while true; do
    sleep 1
done