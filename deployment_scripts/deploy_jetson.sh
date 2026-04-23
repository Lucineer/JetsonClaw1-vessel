#!/bin/bash
# deploy_jetson.sh - Deploy warp-as-room to Jetson

set -e

echo "=== Jetson Deployment Script ==="
echo "Time: $(date)"
echo ""

# Configuration
INSTALL_DIR="/opt/warp-as-room"
CONFIG_DIR="/etc/warp-as-room"
LOG_DIR="/var/log/warp-as-room"
USER="warpuser"

echo "1. Checking system..."
# Check if running on Jetson
if [ ! -f /etc/nv_tegra_release ]; then
    echo "WARNING: This doesn't appear to be a Jetson system"
    echo "Continuing anyway for testing..."
fi

# Check CUDA
if ! command -v nvcc &> /dev/null; then
    echo "ERROR: nvcc not found. CUDA required."
    echo "Install CUDA toolkit first."
    exit 1
fi

echo "2. Creating directories..."
sudo mkdir -p $INSTALL_DIR $CONFIG_DIR $LOG_DIR
sudo chmod 755 $INSTALL_DIR $CONFIG_DIR $LOG_DIR

echo "3. Creating warp user..."
if ! id "$USER" &>/dev/null; then
    sudo useradd -r -s /bin/false $USER
fi
sudo chown -R $USER:$USER $INSTALL_DIR $LOG_DIR

echo "4. Copying files..."
# This would copy actual files
# For now, create placeholder structure
sudo mkdir -p $INSTALL_DIR/{bin,lib,include,examples,config}

echo "5. Creating systemd service..."
cat > /tmp/warp-as-room.service << SERVICE
[Unit]
Description=Warp-as-Room Edge AI Service
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$INSTALL_DIR
ExecStart=$INSTALL_DIR/bin/warp_daemon --config $CONFIG_DIR/warp.conf
Restart=always
RestartSec=10
StandardOutput=syslog
StandardError=syslog
SyslogIdentifier=warp-as-room

# Security
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ReadWritePaths=$LOG_DIR

[Install]
WantedBy=multi-user.target
SERVICE

sudo cp /tmp/warp-as-room.service /etc/systemd/system/
sudo systemctl daemon-reload

echo "6. Creating configuration..."
cat > /tmp/warp.conf << CONFIG
# Warp-as-Room Configuration
# Generated: $(date)

[system]
install_dir = $INSTALL_DIR
config_dir = $CONFIG_DIR
log_dir = $LOG_DIR
user = $USER

[performance]
latency_target_ms = 0.031  # Standard warp
throughput_target_qps = 32258
memory_limit_mb = 2048
power_limit_w = 10

[variants]
enabled = edge_ai,iot_sensors
edge_ai_priority = 1
iot_sensors_priority = 2

[logging]
level = info
file = $LOG_DIR/warp.log
max_size_mb = 100
backup_count = 5

[monitoring]
enable = true
metrics_port = 9090
health_check_interval = 30
CONFIG

sudo cp /tmp/warp.conf $CONFIG_DIR/
sudo chown $USER:$USER $CONFIG_DIR/warp.conf
sudo chmod 600 $CONFIG_DIR/warp.conf

echo "7. Creating health check..."
cat > /tmp/health_check.sh << HEALTH
#!/bin/bash
# warp-as-room health check

STATUS_FILE="$LOG_DIR/status.json"

# Check if daemon is running
if ! systemctl is-active --quiet warp-as-room.service; then
    echo '{"status": "error", "message": "Service not running", "timestamp": "'$(date -Iseconds)'"}' > $STATUS_FILE
    exit 1
fi

# Check disk space
DISK_USAGE=$(df $INSTALL_DIR --output=pcent | tail -1 | tr -d '% ')
if [ $DISK_USAGE -gt 90 ]; then
    echo '{"status": "warning", "message": "High disk usage: '$DISK_USAGE'%", "timestamp": "'$(date -Iseconds)'"}' > $STATUS_FILE
    exit 0
fi

# All good
echo '{"status": "healthy", "message": "Service running normally", "timestamp": "'$(date -Iseconds)'"}' > $STATUS_FILE
exit 0
HEALTH

sudo cp /tmp/health_check.sh $INSTALL_DIR/bin/
sudo chmod +x $INSTALL_DIR/bin/health_check.sh

echo "8. Creating log rotation..."
cat > /tmp/warp-logrotate << LOGROTATE
$LOG_DIR/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 640 $USER $USER
    sharedscripts
    postrotate
        systemctl reload warp-as-room.service > /dev/null 2>&1 || true
    endscript
}
LOGROTATE

sudo cp /tmp/warp-logrotate /etc/logrotate.d/warp-as-room

echo "9. Setting up cron for health checks..."
# Add to crontab
(sudo crontab -l 2>/dev/null; echo "*/5 * * * * $INSTALL_DIR/bin/health_check.sh") | sudo crontab -

echo "10. Summary:"
echo "   Install directory: $INSTALL_DIR"
echo "   Config directory:  $CONFIG_DIR"
echo "   Log directory:     $LOG_DIR"
echo "   Service user:      $USER"
echo "   Systemd service:   warp-as-room.service"
echo "   Health checks:     Every 5 minutes"
echo "   Log rotation:      Daily, keep 7 days"

echo ""
echo "=== Deployment Complete ==="
echo ""
echo "To start the service:"
echo "  sudo systemctl start warp-as-room.service"
echo "  sudo systemctl enable warp-as-room.service"
echo ""
echo "To check status:"
echo "  sudo systemctl status warp-as-room.service"
echo "  cat $LOG_DIR/status.json"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u warp-as-room.service -f"
echo ""
echo "Deployment ready for actual warp-as-room binaries."
