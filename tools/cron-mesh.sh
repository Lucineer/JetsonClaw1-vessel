#!/bin/bash
# Hourly mesh sync — runs from cron
cd /home/lucineer/.openclaw/workspace
python3 tools/mesh-bridge.py tick 2>&1 >> /tmp/mesh-cron.log
echo "--- $(date) ---" >> /tmp/mesh-cron.log