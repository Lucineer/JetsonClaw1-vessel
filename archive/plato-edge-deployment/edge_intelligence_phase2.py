            "adjustments": adjustments,
            "expected_improvement": f"Reduce memory usage by {int((1 - adjustments['batch_size']/current_state.get('batch_size', 8))*100)}%"
        }
    
    def _optimize_for_power(self, algorithm_type, current_state, hardware_telemetry):
        """Optimize for power constraints."""
        power = hardware_telemetry.get("power", {})
        power_w = power.get("total_w", power.get("estimated_w", 0))
        power_usage = power_w / self.constraints["power_w"]
        
        adjustments = {}
        
        if power_usage > 0.8:
            # Critical power situation
            adjustments = {
                "cpu_frequency": "low",
                "gpu_usage": "minimal",
                "batch_interval": current_state.get("batch_interval", 1) * 2,
                "power_saving_mode": True
            }
            strategy = "aggressive_power_saving"
        elif power_usage > 0.6:
            # High power usage
            adjustments = {
                "cpu_frequency": "medium",
                "gpu_usage": "reduced",
                "batch_interval": current_state.get("batch_interval", 1) * 1.5,
                "power_saving_mode": True
            }
            strategy = "moderate_power_saving"
        else:
            # Normal optimization
            adjustments = {
                "cpu_frequency": "adaptive",
                "gpu_usage": "normal",
                "batch_interval": current_state.get("batch_interval", 1),
                "power_saving_mode": False
            }
            strategy = "power_efficient"
        
        return {
            "optimized": True,
            "constraint": "power",
            "strategy": strategy,
            "power_usage": power_usage,
            "adjustments": adjustments,
            "expected_improvement": f"Reduce power consumption by ~{int((1 - 0.9**adjustments.get('batch_interval', 1))*100)}%"
        }
    
    def _optimize_for_thermal(self, algorithm_type, current_state, hardware_telemetry):
        """Optimize for thermal constraints."""
        temp_data = hardware_telemetry.get("temperature", {})
        temps = [v for v in temp_data.values() if isinstance(v, (int, float))]
        max_temp = max(temps) if temps else 0
        temp_usage = max_temp / self.constraints["temperature_c"]
        
        adjustments = {}
        
        if temp_usage > 0.8:
            # Critical thermal situation
            adjustments = {
                "throttle_level": "aggressive",
                "cooling_breaks": True,
                "break_duration": 30,
                "max_sustained_load": 0.3
            }
            strategy = "thermal_protection"
        elif temp_usage > 0.7:
            # High temperature
            adjustments = {
                "throttle_level": "moderate",
                "cooling_breaks": True,
                "break_duration": 15,
                "max_sustained_load": 0.5
            }
            strategy = "thermal_management"
        else:
            # Normal optimization
            adjustments = {
                "throttle_level": "none",
                "cooling_breaks": False,
                "break_duration": 0,
                "max_sustained_load": 0.8
            }
            strategy = "thermal_efficient"
        
        return {
            "optimized": True,
            "constraint": "thermal",
            "strategy": strategy,
            "temperature_c": max_temp,
            "adjustments": adjustments,
            "expected_improvement": f"Reduce temperature by ~{int((max_temp * 0.1))}°C"
        }
    
    def _optimize_for_cpu(self, algorithm_type, current_state, hardware_telemetry):
        """Optimize for CPU constraints."""
        cpu = hardware_telemetry.get("cpu", {})
        cpu_usage = cpu.get("usage_percent", 0) / 100
        
        adjustments = {}
        
        if cpu_usage > 0.8:
            # Critical CPU situation
            adjustments = {
                "parallel_workers": max(1, int(current_state.get("parallel_workers", 4) * 0.5)),
                "thread_priority": "low",
                "cpu_affinity": "efficiency_cores",
                "load_balancing": "conservative"
            }
            strategy = "cpu_conservation"
        elif cpu_usage > 0.6:
            # High CPU usage
            adjustments = {
                "parallel_workers": max(1, int(current_state.get("parallel_workers", 4) * 0.7)),
                "thread_priority": "normal",
                "cpu_affinity": "balanced",
                "load_balancing": "balanced"
            }
            strategy = "cpu_optimization"
        else:
            # Normal optimization
            adjustments = {
                "parallel_workers": current_state.get("parallel_workers", 4),
                "thread_priority": "normal",
                "cpu_affinity": "performance_cores",
                "load_balancing": "performance"
            }
            strategy = "cpu_efficient"
        
        return {
            "optimized": True,
            "constraint": "cpu",
            "strategy": strategy,
            "cpu_usage": cpu_usage,
            "adjustments": adjustments,
            "expected_improvement": f"Reduce CPU load by ~{int((1 - adjustments['parallel_workers']/current_state.get('parallel_workers', 4))*100)}%"
        }

class EdgeIntelligencePhase2:
    """Main class for Phase 2 Edge Intelligence."""
    
    def __init__(self):
        self.pattern_recognizer = SparsePatternRecognizer()
        self.intelligence_compounder = LocalIntelligenceCompounder()
        self.constraint_optimizer = ConstraintBasedOptimizer()
        self.hardware_monitor = None
        
        if REAL_HARDWARE:
            try:
                self.hardware_monitor = RealHardwareMonitor()
                print("✅ Real hardware monitor available for edge intelligence")
            except:
                print("⚠️  Real hardware monitor initialization failed")
        
        self._start_intelligence_processing()
        
        print("🚀 Edge Intelligence Phase 2 Initialized")
        print("   Features: Sparse pattern recognition, Local intelligence compounding, Constraint-based optimization")
    
    def _start_intelligence_processing(self):
        """Start background intelligence processing."""
        def process_intelligence():
            while True:
                if self.hardware_monitor:
                    # Process hardware telemetry for patterns
                    telemetry = self.hardware_monitor.get_all_telemetry()
                    
                    # Add temperature pattern
                    temp_data = telemetry.get("temperature", {})
                    if isinstance(temp_data, dict):
                        temps = [v for v in temp_data.values() if isinstance(v, (int, float))]
                        if temps:
                            max_temp = max(temps)
                            self.pattern_recognizer.add_sparse_observation(
                                "temperature_pattern",
                                {"max_temp": max_temp, "timestamp": time.time()}
                            )
                    
                    # Add memory pattern
                    memory = telemetry.get("memory", {})
                    if "used_mb" in memory:
                        self.pattern_recognizer.add_sparse_observation(
                            "memory_pattern",
                            {"used_mb": memory["used_mb"], "timestamp": time.time()}
                        )
                    
                    # Compound hardware intelligence
                    if temps and "used_mb" in memory:
                        hardware_score = (max_temp / 85) * 0.4 + (memory["used_mb"] / 8192) * 0.6
                        self.intelligence_compounder.compound_observation(
                            "hardware_health",
                            {"temperature": max_temp, "memory": memory["used_mb"]},
                            hardware_score,
                            confidence=0.7
                        )
                
                time.sleep(10)  # Process every 10 seconds
        
        thread = threading.Thread(target=process_intelligence, daemon=True)
        thread.start()
    
    def get_edge_intelligence(self):
        """Get complete edge intelligence."""
        return {
            "edge_intelligence_phase2": {
                "sparse_patterns": self.pattern_recognizer.get_pattern_summary(),
                "compounded_intelligence": self.intelligence_compounder.get_compounded_intelligence(),
                "constraint_optimization": {
                    "available": True,
                    "strategies": list(self.constraint_optimizer.optimization_strategies.keys())
                },
                "hardware_integration": REAL_HARDWARE and self.hardware_monitor is not None,
                "timestamp": datetime.now().isoformat()
            }
        }

# Initialize edge intelligence
edge_intelligence = EdgeIntelligencePhase2()

@app.route('/')
def index():
    return jsonify({
        "server": "Edge Intelligence Phase 2",
        "version": "phase2-1.0",
        "phase": "Edge Intelligence Development",
        "features": [
            "Sparse data pattern recognition",
            "Local intelligence compounding",
            "Constraint-based optimization",
            "Hardware-aware algorithms"
        ],
        "endpoints": {
            "/phase2/intelligence": "Complete edge intelligence",
            "/phase2/patterns": "Sparse pattern recognition",
            "/phase2/compound": "Compounded intelligence",
            "/phase2/optimize": "Constraint-based optimization (POST)",
            "/phase2/recognize": "Pattern recognition (POST)"
        }
    })

@app.route('/phase2/intelligence')
def phase2_intelligence():
    return jsonify(edge_intelligence.get_edge_intelligence())

@app.route('/phase2/patterns')
def phase2_patterns():
    return jsonify({
        "sparse_patterns": edge_intelligence.pattern_recognizer.get_pattern_summary(),
        "pattern_confidence_threshold": edge_intelligence.pattern_recognizer.confidence_threshold,
        "min_samples": edge_intelligence.pattern_recognizer.min_samples
    })

@app.route('/phase2/compound')
def phase2_compound():
    return jsonify({
        "compounded_intelligence": edge_intelligence.intelligence_compounder.get_compounded_intelligence(),
        "compounding_factor": edge_intelligence.intelligence_compounder.compounding_factor,
        "learning_rate": edge_intelligence.intelligence_compounder.learning_rate
    })

@app.route('/phase2/optimize', methods=['POST'])
def phase2_optimize():
    data = request.json
    if not data or 'algorithm_type' not in data:
        return jsonify({"error": "algorithm_type required"}), 400
    
    algorithm_type = data['algorithm_type']
    current_state = data.get('current_state', {})
    
    # Get hardware telemetry if available
    hardware_telemetry = None
    if edge_intelligence.hardware_monitor:
        hardware_telemetry = edge_intelligence.hardware_monitor.get_all_telemetry()
    
    optimization = edge_intelligence.constraint_optimizer.optimize_algorithm(
        algorithm_type, current_state, hardware_telemetry
    )
    
    return jsonify(optimization)

@app.route('/phase2/recognize', methods=['POST'])
def phase2_recognize():
    data = request.json
    if not data or 'pattern_type' not in data or 'observation' not in data:
        return jsonify({"error": "pattern_type and observation required"}), 400
    
    pattern_type = data['pattern_type']
    observation = data['observation']
    similarity_threshold = data.get('similarity_threshold', 0.6)
    
    recognition = edge_intelligence.pattern_recognizer.recognize_pattern(
        pattern_type, observation, similarity_threshold
    )
    
    return jsonify(recognition)

def run_edge_intelligence_server(port=4545):
    """Run the edge intelligence server."""
    print(f"""
🚀 EDGE INTELLIGENCE PHASE 2 SERVER
===================================
🎯 Sparse Pattern Recognition & Constraint Optimization
📡 http://0.0.0.0:{port}
🧠 Features:
  • Sparse data pattern recognition
  • Local intelligence compounding
  • Constraint-based optimization
  • Hardware-aware algorithms

📊 Intelligence Processing:
  • Pattern confidence threshold: {edge_intelligence.pattern_recognizer.confidence_threshold}
  • Compounding learning rate: {edge_intelligence.intelligence_compounder.learning_rate}
  • Hardware integration: {'✅ REAL' if REAL_HARDWARE else '⚠️ SIMULATED'}

🧪 Test Commands:
  curl http://localhost:{port}/phase2/intelligence
  curl http://localhost:{port}/phase2/patterns
  curl http://localhost:{port}/phase2/compound
  curl -X POST http://localhost:{port}/phase2/optimize -H "Content-Type: application/json" -d '{"algorithm_type":"inference","current_state":{"batch_size":8,"learning_rate":0.001}}'
  curl -X POST http://localhost:{port}/phase2/recognize -H "Content-Type: application/json" -d '{"pattern_type":"temperature_pattern","observation":{"max_temp":65}}'

Starting edge intelligence server...
    """)
    
    app.run(host='0.0.0.0', port=port, debug=False, threaded=True)

if __name__ == '__main__':
    run_edge_intelligence_server(4545)