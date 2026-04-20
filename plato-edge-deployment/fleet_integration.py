            "fleet_recommendation": "JC1 available for edge tasks within hardware constraints",
            "timestamp": hardware_state["timestamp"]
        }
    })

def run_fleet_integration_server(port=4444):
    """Run the fleet integration server."""
    print(f"""
🚀 FLEET INTEGRATION SERVER
===========================
🎯 Hardware-Aware Fleet Coordination
📡 http://0.0.0.0:{port}
🔗 Target Fleet: {FLEET_CONFIG['cocapn_endpoint']}
📊 Features:
  • Hardware-aware bottle protocol
  • Edge hardware dashboard
  • Fleet status synchronization
  • Incident reporting to fleet

📦 Bottle Directory: {FLEET_CONFIG['bottle_directory']}
🔄 Sync Interval: {FLEET_CONFIG['sync_interval_seconds']} seconds

🧪 Test Commands:
  curl http://localhost:{port}/fleet/status
  curl http://localhost:{port}/fleet/dashboard
  curl http://localhost:{port}/fleet/bottles
  curl -X POST http://localhost:{port}/fleet/incident -H "Content-Type: application/json" -d '{"type":"thermal","severity":"warning","description":"Temperature approaching limit"}'

Starting fleet integration server...
    """)
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

if __name__ == '__main__':
    run_fleet_integration_server(4444)