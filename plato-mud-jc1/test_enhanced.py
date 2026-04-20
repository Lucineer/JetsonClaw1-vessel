#!/usr/bin/env python3
"""Test the enhanced Plato MUD server."""

import sys
import time
import threading

# Import our enhanced server
sys.path.append('.')
from enhanced_mud_server import run_enhanced_server, run_enhanced_experiment

print("🚀 Testing JC1 Enhanced Plato MUD Server...")

# Start server in background
server_thread = threading.Thread(target=run_enhanced_server, args=('0.0.0.0', 4044))
server_thread.daemon = True
server_thread.start()

print("⏳ Waiting for server to start...")
time.sleep(3)

print("\n🧪 Running enhanced experiment (3 players, 4 steps each)...")
run_enhanced_experiment(3, 4)

print("\n✅ Enhanced server running at http://0.0.0.0:4044")
print("   Features: 16 rooms, sentiment tracking, archetype behaviors")
print("   Shell-crab trap with compounding intelligence")
print("   Press Ctrl+C to stop.")

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 Server stopped.")