#!/bin/bash
# deckboss-healthcheck.sh — Called by systemd ExecStartPost or cron
# Checks: GPU memory usage, process alive, inference latency
# Exits 0=healthy, 1=degraded, 2=critical (triggers restart)

GPU_MEM_WARN=4096   # 4GB
GPU_MEM_CRIT=6144   # 6GB of 7.6GB total
LATENCY_WARN=50     # ms
LATENCY_CRIT=200     # ms
HEALTH_PORT=9876

# Check if deckbossd is running
if ! pgrep -x deckbossd > /dev/null 2>&1; then
    echo "CRITICAL: deckbossd not running"
    exit 2
fi

# Check GPU memory (parse from sysfs or nvidia-smi)
GPU_MEM_MB=$(cat /sys/kernel/debug/nvmap/gpu/meminfo 2>/dev/null | grep -i "total" | awk '{print $NF/1024}' || echo "0")
if [ "$GPU_MEM_MB" -gt "$GPU_MEM_CRIT" ] 2>/dev/null; then
    echo "CRITICAL: GPU memory ${GPU_MEM_MB}MB exceeds ${GPU_MEM_CRIT}MB"
    exit 2
elif [ "$GPU_MEM_MB" -gt "$GPU_MEM_WARN" ] 2>/dev/null; then
    echo "WARN: GPU memory ${GPU_MEM_MB}MB exceeds ${GPU_MEM_WARN}MB"
    exit 1
fi

# Check health endpoint
RESP=$(curl -s --max-time 3 "http://localhost:${HEALTH_PORT}/health" 2>/dev/null)
if [ $? -ne 0 ]; then
    echo "WARN: Health endpoint unreachable"
    exit 1
fi

LATENCY=$(echo "$RESP" | grep -o '"latency_ms":[0-9.]*' | cut -d: -f2)
if [ -n "$LATENCY" ]; then
    if (( $(echo "$LATENCY > $LATENCY_CRIT" | bc -l 2>/dev/null) )); then
        echo "CRITICAL: Inference latency ${LATENCY}ms"
        exit 2
    elif (( $(echo "$LATENCY > $LATENCY_WARN" | bc -l 2>/dev/null) )); then
        echo "WARN: Inference latency ${LATENCY}ms"
        exit 1
    fi
fi

echo "OK: GPU=${GPU_MEM_MB}MB latency=${LATENCY:-N/A}ms"
exit 0
