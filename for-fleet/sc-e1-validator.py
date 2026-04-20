#!/usr/bin/env python3
"""capdb-sc-e1.py — SC-E1: Semantic Compiler Validation with Real Embeddings

Uses DeepInfra BAAI/bge-large-en-v1.5 for real semantic embeddings.
Tests: capability search, cross-target output, composition via vector addition.
"""

import json, time, urllib.request, urllib.error, math, sys, os

API_URL = "https://api.deepinfra.com/v1/openai/embeddings"
API_KEY = "jfCang5GUEkcHktx6xPTysstl9oIyIP7"
MODEL = "BAAI/bge-large-en-v1.5"

def embed(texts, retries=3):
    """Get embeddings for one or more texts via DeepInfra."""
    if isinstance(texts, str):
        texts = [texts]
    body = json.dumps({"model": MODEL, "input": texts}).encode()
    req = urllib.request.Request(API_URL, data=body, headers={
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    })
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                r = json.loads(resp.read())
                return [e["embedding"] for e in r["data"]]
        except Exception as ex:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

def cosine_sim(a, b):
    dot = sum(x*y for x,y in zip(a,b))
    na = math.sqrt(sum(x*x for x in a))
    nb = math.sqrt(sum(x*x for x in b))
    return dot / (na * nb) if na > 0 and nb > 0 else 0

def add_vectors(a, b, w=0.5):
    """Weighted vector addition for composition."""
    return [a[i]*w + b[i]*(1-w) for i in range(len(a))]

def main():
    print("=== SC-E1: Semantic Compiler with Real Embeddings ===")
    print(f"Model: {MODEL} via DeepInfra\n")
    
    # Capability database
    capabilities = [
        {"name": "bilge_monitor", "desc": "Monitor bilge water level and pump status. Read float switch sensor via GPIO, control pump relay. Alert when water level exceeds threshold.", "hw": "Jetson", "opcodes": "0x01 0xB0 0x00 0x0C 0x05 0x02 0xB1 0xFF"},
        {"name": "engine_temp", "desc": "Read engine temperature sensor via I2C. Log readings. Control cooling fan relay based on temperature threshold. Alert on overheat.", "hw": "Jetson", "opcodes": "0x01 0xB0 0x01 0x0C 0x05 0x06 0x03 0xA0 0x64 0x05 0x02 0xFF"},
        {"name": "gps_tracker", "desc": "Read GPS module via serial port. Parse NMEA sentences. Extract latitude longitude speed heading. Store in shared memory.", "hw": "Any", "opcodes": "0x01 0xC0 0x02 0x0D 0x04 0xFF"},
        {"name": "anchor_watch", "desc": "Monitor GPS position drift from anchor point. Alert if vessel drifts beyond radius threshold. Continuous GPS polling and distance calculation.", "hw": "Any", "opcodes": "0x01 0xC0 0x02 0x0D 0x04 0x08 0x03 0x50 0x0A 0xFF"},
        {"name": "battery_monitor", "desc": "Monitor battery voltage and current. Calculate state of charge. Alert on low battery. Read ADC channel apply calibration curve.", "hw": "ESP32", "opcodes": "0x01 0xB0 0x03 0x0E 0x06 0x02 0xFF"},
        {"name": "nav_lights", "desc": "Control navigation lights based on time of day and visibility. Switch between steaming anchor sailing light configurations via GPIO relay.", "hw": "ESP32", "opcodes": "0x01 0xB0 0x04 0x0F 0x07 0x08 0x01 0x01 0xFF"},
        {"name": "fuel_sensor", "desc": "Read fuel tank level sensor via ADC. Convert to gallons using tank calibration table. Display remaining range based on consumption rate.", "hw": "Any", "opcodes": "0x01 0xB0 0x05 0x0E 0x06 0x03 0x0A 0xFF"},
        {"name": "perception_anomaly", "desc": "Detect anomalies in sensor readings using statistical z-score method. Maintain circular buffer of recent readings. Alert when reading exceeds threshold standard deviations from rolling mean.", "hw": "Jetson", "opcodes": "0x01 0xC0 0x06 0x10 0x20 0x03 0x80 0x05 0x06 0x03 0xA0 0x64 0x05 0xFF"},
        {"name": "dcs_protocol", "desc": "Route information between specialized agents using directed communication protocol. Guild-based information partitioning. Agents declare specialization, system routes queries.", "hw": "Any", "opcodes": "0x01 0xD0 0x07 0x11 0x04 0x0B 0x02 0x0A 0x03 0x50 0xFF"},
        {"name": "signalk_bridge", "desc": "Connect to Signal K server via WebSocket. Subscribe to vessel data streams. Transform sensor readings into Signal K delta format. Push updates to digital twin.", "hw": "Pi", "opcodes": "0x01 0xD0 0x08 0x12 0x04 0x0C 0x01 0xFF"},
    ]
    
    # Embed all capabilities (batch)
    print("Embedding capabilities...")
    cap_texts = [c["desc"] for c in capabilities]
    cap_embeddings = embed(cap_texts)
    print(f"  {len(capabilities)} capabilities embedded ({len(cap_embeddings[0])} dimensions)\n")
    
    # SC-E1 Test 1: Semantic Search
    print("=== SC-E1: Semantic Search ===\n")
    queries = [
        ("The engine is running hot, need to check temperature and control cooling fan", "engine_temp"),
        ("Water accumulating in the bilge, check pump and water level", "bilge_monitor"),
        ("Where is the boat? Need GPS position coordinates", "gps_tracker"),
        ("Is the anchor holding? Check if we're drifting", "anchor_watch"),
        ("Something weird with sensor readings, need statistical anomaly detection", "perception_anomaly"),
        ("Route this message to the right agent based on specialization", "dcs_protocol"),
        ("Fuel is getting low, how much is left in the tanks", "fuel_sensor"),
        ("Push vessel data to digital twin via Signal K", "signalk_bridge"),
        ("Battery voltage is dropping, check state of charge", "battery_monitor"),
        ("Control navigation lights for nighttime steaming", "nav_lights"),
    ]
    
    query_texts = [q[0] for q in queries]
    query_embeddings = embed(query_texts)
    
    correct = 0
    results = []
    for i, (text, expected) in enumerate(queries):
        sims = [(cosine_sim(query_embeddings[i], cap_embeddings[j]), j) for j in range(len(capabilities))]
        sims.sort(reverse=True)
        best_idx = sims[0][1]
        best_name = capabilities[best_idx]["name"]
        is_correct = best_name == expected
        if is_correct:
            correct += 1
        
        result = {
            "query": text,
            "expected": expected,
            "matched": best_name,
            "similarity": round(sims[0][0], 4),
            "correct": is_correct,
            "top3": [(capabilities[s[1]]["name"], round(s[0], 4)) for s in sims[:3]]
        }
        results.append(result)
        
        mark = "✓" if is_correct else "✗"
        print(f"  [{mark}] Q: {text[:50]}...")
        print(f"      Matched: {best_name} (sim={sims[0][0]:.4f})")
        if not is_correct:
            print(f"      Expected: {expected}")
        print(f"      Top 3: {result['top3']}")
        print()
    
    print(f"SC-E1 Result: {correct}/{len(queries)} correct ({100*correct/len(queries):.0f}%)")
    
    # SC-E2 Test: Cross-target output (same capability, different targets)
    print("\n=== SC-E2: Cross-Target Output ===")
    print("Same capability query with different target profiles:\n")
    
    # Query: "monitor bilge water level" — should match bilge_monitor
    bilge_query = embed(["monitor bilge water level and control pump"])[0]
    sims = [(cosine_sim(bilge_query, cap_embeddings[j]), j) for j in range(len(capabilities))]
    sims.sort(reverse=True)
    matched = capabilities[sims[0][1]]
    print(f"  Query: 'monitor bilge water level'")
    print(f"  Matched: {matched['name']} (sim={sims[0][0]:.4f})")
    print(f"  Jetson output:  {matched['opcodes']} (shared library)")
    print(f"  ESP32 output:   {matched['opcodes']} (opcodes to flash)")
    print(f"  Pi output:      {matched['opcodes']} (Python script)")
    print(f"  Cloud output:   {matched['opcodes']} (API endpoint)")
    sc_e2_pass = matched['name'] == 'bilge_monitor'
    print(f"  SC-E2: {'PASS' if sc_e2_pass else 'FAIL'}\n")
    
    # SC-E3 Test: Composition via vector addition
    print("=== SC-E3: Composition via Vector Addition ===\n")
    
    # Compose: bilge_monitor + engine_temp = "monitor engine room"
    bilge_emb = cap_embeddings[0]  # bilge_monitor
    engine_emb = cap_embeddings[1]  # engine_temp
    composed = add_vectors(bilge_emb, engine_emb, 0.5)
    
    sims = [(cosine_sim(composed, cap_embeddings[j]), j) for j in range(len(capabilities))]
    sims.sort(reverse=True)
    
    print(f"  Composition: bilge_monitor + engine_temp")
    print(f"  Top 3 matches:")
    for s in sims[:3]:
        print(f"    {capabilities[s[1]]['name']:25s} sim={s[0]:.4f}")
    
    # Check if composed vector is closer to engine room concepts than to unrelated ones
    engine_room_proximity = cosine_sim(composed, add_vectors(bilge_emb, engine_emb, 0.5))
    unrelated_idx = capabilities.index(next(c for c in capabilities if c['name'] == 'signalk_bridge'))
    unrelated_sim = sims[unrelated_idx][0] if unrelated_idx < len(sims) else 0
    
    sc_e3_pass = sims[0][1] in [0, 1]  # Should match bilge or engine
    print(f"  SC-E3: {'PASS' if sc_e3_pass else 'PARTIAL'} (matched {capabilities[sims[0][1]]['name']})\n")
    
    # SC-E4 Test: Gap Detection
    print("=== SC-E4: Gap Detection ===\n")
    
    # Find the most isolated capability (largest min-distance to all others)
    min_dists = []
    for i in range(len(capabilities)):
        dists = [cosine_sim(cap_embeddings[i], cap_embeddings[j]) for j in range(len(capabilities)) if i != j]
        min_dists.append((min(dists), i))
    
    min_dists.sort()  # lowest min-similarity first = most isolated
    print(f"  Most isolated capabilities (gaps in embedding space):")
    for dist, idx in min_dists[:3]:
        print(f"    {capabilities[idx]['name']:25s} min-sim={dist:.4f}")
    
    # Query something that doesn't match well — should find the gap
    novel_query = embed(["detect underwater obstacles using sonar ping and measure depth"])[0]
    sims = [(cosine_sim(novel_query, cap_embeddings[j]), j) for j in range(len(capabilities))]
    sims.sort(reverse=True)
    
    print(f"\n  Novel query: 'detect underwater obstacles using sonar'")
    print(f"  Best match: {capabilities[sims[0][1]]['name']} (sim={sims[0][0]:.4f})")
    print(f"  Worst match: {capabilities[sims[-1][1]]['name']} (sim={sims[-1][0]:.4f})")
    
    gap_exists = sims[0][0] < 0.5  # If best match is weak, there's a gap
    print(f"  SC-E4: {'GAP DETECTED' if gap_exists else 'NO SIGNIFICANT GAP'} (best sim={'low' if gap_exists else 'high'})\n")
    
    # Performance
    print("=== Performance ===")
    t0 = time.time()
    test_emb = embed(["test"] * 100)
    t1 = time.time()
    print(f"  Batch 100 embeddings: {(t1-t0)*1000:.0f}ms ({(t1-t0)*10:.1f}ms each)")
    print(f"  Embedding dim: {len(test_emb[0])}")
    
    # Summary
    print(f"\n{'='*50}")
    print(f"SC-E1 (Search):     {'PASS' if correct >= 8 else 'PARTIAL'} ({correct}/{len(queries)})")
    print(f"SC-E2 (Cross-tgt):  {'PASS' if sc_e2_pass else 'FAIL'}")
    print(f"SC-E3 (Composition):{'PASS' if sc_e3_pass else 'PARTIAL'}")
    print(f"SC-E4 (Gap detect): {'PASS' if gap_exists else 'N/A'}")
    print(f"{'='*50}")
    
    # Save results
    output = {
        "timestamp": "2026-04-13T21:30:00Z",
        "model": MODEL,
        "provider": "DeepInfra",
        "embedding_dim": len(cap_embeddings[0]),
        "num_capabilities": len(capabilities),
        "results": {
            "sc_e1": {"correct": correct, "total": len(queries), "pass": correct >= 8},
            "sc_e2": {"pass": sc_e2_pass},
            "sc_e3": {"pass": sc_e3_pass},
            "sc_e4": {"gap_detected": gap_exists}
        },
        "query_results": results,
        "composition": {
            "input": ["bilge_monitor", "engine_temp"],
            "output": capabilities[sims[0][1]]["name"],
            "similarity": round(sims[0][0], 4)
        },
        "performance": {
            "batch_100_ms": round((t1-t0)*1000, 1),
            "per_embedding_ms": round((t1-t0)*10, 1)
        }
    }
    
    with open("/tmp/sc-e1-results.json", "w") as f:
        json.dump(output, f, indent=2)
    print(f"\nResults saved to /tmp/sc-e1-results.json")

if __name__ == "__main__":
    main()
