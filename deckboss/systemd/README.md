# DeckBoss systemd Service

## Installation
```bash
sudo cp deckboss.service /etc/systemd/user/
sudo cp deckboss-healthcheck.sh /opt/deckboss/bin/
sudo chmod +x /opt/deckboss/bin/deckboss-healthcheck.sh
systemctl --user daemon-reload
systemctl --user enable --now deckboss
```

## Health Check
```bash
# Manual check
./deckboss-healthcheck.sh

# Auto-check every 60s via systemd watchdog
# (Requires WatchdogSec in service file)
journalctl --user -u deckboss -f
```

## GPU Memory Watchdog
- **Warning**: 4GB GPU memory used → logged
- **Critical**: 6GB GPU memory used → service restart triggered
- Jetson Orin has 7.6GB unified RAM shared with CPU
- DeckBoss limits itself to 4GB GPU allocation by default

## Log Rotation
Logs go to journald. Rotate with:
```bash
# Keep 7 days of logs
journalctl --user --vacuum-time=7d -u deckboss
```

## Orin-Specific Notes
- No sudo required — runs as user service (`--user`)
- `CPUQuota=200%` — allows burst on 8-core ARM
- `MemoryMax=4G` — prevents runaway memory from starving CUDA
- `ReadWritePaths` — only deckboss dirs, everything else read-only
