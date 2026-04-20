                predictions["failure_predictions"].items() if v["probability"] > 0.4],
        "optimization_count": len(enhancer.predictor.optimization_suggestions),
        "forecast": intelligence["enhanced_hardware_intelligence"]["health_forecast"].get("overall_health", "unknown"),
        "timestamp": datetime.now().isoformat()
    })

def run_enhanced_intelligence_server(port=4343):
    """Run the enhanced hardware intelligence server."""
    print(f"""
🚀 ENHANCED HARDWARE INTELLIGENCE SERVER
========================================
🎯 Predictive Failure Detection & Optimization
📡 http://0.0.0.0:{port}
🔮 Features:
  • Predictive failure detection (thermal, memory, power)
  • Hardware optimization suggestions
  • Health forecasting
  • Real-time monitoring integration

📊 Endpoints:
  /enhanced/intelligence - Complete enhanced intelligence
  /enhanced/predictions  - Failure predictions
  /enhanced/optimizations - Optimization suggestions  
  /enhanced/forecast     - Health forecast
  /enhanced/health       - Enhanced health check

🧪 Test Commands:
  curl http://localhost:{port}/enhanced/intelligence
  curl http://localhost:{port}/enhanced/predictions
  curl http://localhost:{port}/enhanced/optimizations

Starting enhanced intelligence server...
    """)
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

if __name__ == '__main__':
    run_enhanced_intelligence_server(4343)