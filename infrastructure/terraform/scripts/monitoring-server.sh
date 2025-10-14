#!/bin/bash
# SSL Monitor Pro - Monitoring Server Setup Script

set -e

# Environment variables
ENVIRONMENT=${environment}

# Update system
apt-get update
apt-get upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
usermod -aG docker ubuntu

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Create monitoring directory
mkdir -p /opt/monitoring
cd /opt/monitoring

# Create Docker Compose file for Monitoring Stack
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: unless-stopped
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - ./rules:/etc/prometheus/rules
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=30d'
      - '--web.enable-lifecycle'
      - '--web.enable-admin-api'
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    ports:
      - "3000:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin123
      - GF_USERS_ALLOW_SIGN_UP=false
      - GF_INSTALL_PLUGINS=grafana-clock-panel,grafana-simple-json-datasource
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/provisioning:/etc/grafana/provisioning
      - ./grafana/dashboards:/var/lib/grafana/dashboards
    networks:
      - monitoring

  alertmanager:
    image: prom/alertmanager:latest
    container_name: alertmanager
    restart: unless-stopped
    ports:
      - "9093:9093"
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
      - alertmanager_data:/alertmanager
    command:
      - '--config.file=/etc/alertmanager/alertmanager.yml'
      - '--storage.path=/alertmanager'
      - '--web.external-url=http://localhost:9093'
    networks:
      - monitoring

  node-exporter:
    image: prom/node-exporter:latest
    container_name: node-exporter
    restart: unless-stopped
    ports:
      - "9100:9100"
    volumes:
      - /proc:/host/proc:ro
      - /sys:/host/sys:ro
      - /:/rootfs:ro
    command:
      - '--path.procfs=/host/proc'
      - '--path.rootfs=/rootfs'
      - '--path.sysfs=/host/sys'
      - '--collector.filesystem.mount-points-exclude=^/(sys|proc|dev|host|etc)($$|/)'
    networks:
      - monitoring

  cadvisor:
    image: gcr.io/cadvisor/cadvisor:latest
    container_name: cadvisor
    restart: unless-stopped
    ports:
      - "8080:8080"
    volumes:
      - /:/rootfs:ro
      - /var/run:/var/run:ro
      - /sys:/sys:ro
      - /var/lib/docker/:/var/lib/docker:ro
      - /dev/disk/:/dev/disk:ro
    privileged: true
    devices:
      - /dev/kmsg
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:
  alertmanager_data:

networks:
  monitoring:
    driver: bridge
EOF

# Create Prometheus configuration
cat > prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # Node Exporter
  - job_name: 'node-exporter'
    static_configs:
      - targets: ['node-exporter:9100']

  # cAdvisor
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['cadvisor:8080']

  # SSL Monitor API (Primary Server)
  - job_name: 'ssl-monitor-primary'
    static_configs:
      - targets: ['10.0.1.10:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # SSL Monitor API (Standby Server)
  - job_name: 'ssl-monitor-standby'
    static_configs:
      - targets: ['10.0.1.11:8000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # Database monitoring
  - job_name: 'postgres-exporter'
    static_configs:
      - targets: ['postgres-exporter:9187']
    scrape_interval: 30s

  # Redis monitoring
  - job_name: 'redis-exporter'
    static_configs:
      - targets: ['redis-exporter:9121']
    scrape_interval: 30s
EOF

# Create Alertmanager configuration
cat > alertmanager.yml << 'EOF'
global:
  smtp_smarthost: 'localhost:587'
  smtp_from: 'alerts@sslmonitor.pro'

route:
  group_by: ['alertname']
  group_wait: 10s
  group_interval: 10s
  repeat_interval: 1h
  receiver: 'web.hook'

receivers:
  - name: 'web.hook'
    webhook_configs:
      - url: 'http://10.0.1.10:8000/api/alerts/webhook'
        send_resolved: true

  - name: 'telegram'
    webhook_configs:
      - url: 'http://10.0.1.10:8000/api/alerts/telegram'
        send_resolved: true

  - name: 'email'
    email_configs:
      - to: 'admin@sslmonitor.pro'
        subject: '[SSL Monitor] {{ .GroupLabels.alertname }}'
        body: |
          {{ range .Alerts }}
          Alert: {{ .Annotations.summary }}
          Description: {{ .Annotations.description }}
          {{ end }}
EOF

# Create alert rules directory
mkdir -p rules

# Create SSL Monitor specific alert rules
cat > rules/ssl-monitor.yml << 'EOF'
groups:
  - name: ssl-monitor
    rules:
      # API Health Checks
      - alert: SSLMONITOR_API_DOWN
        expr: up{job="ssl-monitor-primary"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "SSL Monitor API is down"
          description: "Primary SSL Monitor API has been down for more than 1 minute"

      - alert: SSLMONITOR_API_HIGH_ERROR_RATE
        expr: rate(ssl_monitor_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: warning
        annotations:
          summary: "SSL Monitor API high error rate"
          description: "API error rate is {{ $value }} errors per second"

      # Certificate Monitoring
      - alert: SSL_CERTIFICATE_EXPIRING
        expr: ssl_cert_days_until_expiry < 30
        for: 0m
        labels:
          severity: warning
        annotations:
          summary: "SSL Certificate expiring soon"
          description: "Certificate for {{ $labels.domain }} expires in {{ $value }} days"

      - alert: SSL_CERTIFICATE_EXPIRED
        expr: ssl_cert_days_until_expiry < 0
        for: 0m
        labels:
          severity: critical
        annotations:
          summary: "SSL Certificate has expired"
          description: "Certificate for {{ $labels.domain }} has expired"

      # Infrastructure Alerts
      - alert: HIGH_CPU_USAGE
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High CPU usage"
          description: "CPU usage is above 80% for more than 5 minutes"

      - alert: HIGH_MEMORY_USAGE
        expr: (1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High memory usage"
          description: "Memory usage is above 80% for more than 5 minutes"

      - alert: DISK_SPACE_LOW
        expr: (1 - (node_filesystem_avail_bytes / node_filesystem_size_bytes)) * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Low disk space"
          description: "Disk space usage is above 80% for more than 5 minutes"

      # Database Alerts
      - alert: DATABASE_CONNECTION_HIGH
        expr: pg_stat_database_numbackends / pg_settings_max_connections * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High database connections"
          description: "Database connection usage is above 80%"

      # Redis Alerts
      - alert: REDIS_MEMORY_HIGH
        expr: redis_memory_used_bytes / redis_memory_max_bytes * 100 > 80
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High Redis memory usage"
          description: "Redis memory usage is above 80%"
EOF

# Create Grafana provisioning directory
mkdir -p grafana/provisioning/datasources
mkdir -p grafana/provisioning/dashboards

# Create Grafana datasource configuration
cat > grafana/provisioning/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
EOF

# Create Grafana dashboard provisioning
cat > grafana/provisioning/dashboards/dashboard.yml << 'EOF'
apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    updateIntervalSeconds: 10
    allowUiUpdates: true
    options:
      path: /var/lib/grafana/dashboards
EOF

# Create SSL Monitor dashboard
mkdir -p grafana/dashboards

cat > grafana/dashboards/ssl-monitor-overview.json << 'EOF'
{
  "dashboard": {
    "id": null,
    "title": "SSL Monitor Pro - Overview",
    "tags": ["ssl", "monitoring"],
    "timezone": "Europe/Prague",
    "panels": [
      {
        "id": 1,
        "title": "API Health Status",
        "type": "stat",
        "targets": [
          {
            "expr": "up{job=\"ssl-monitor-primary\"}",
            "legendFormat": "Primary API"
          },
          {
            "expr": "up{job=\"ssl-monitor-standby\"}",
            "legendFormat": "Standby API"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "red", "value": 0},
                {"color": "green", "value": 1}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Request Rate",
        "type": "graph",
        "targets": [
          {
            "expr": "rate(ssl_monitor_requests_total[5m])",
            "legendFormat": "Requests/sec"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "SSL Certificate Status",
        "type": "stat",
        "targets": [
          {
            "expr": "ssl_cert_days_until_expiry < 30",
            "legendFormat": "Expiring Soon"
          },
          {
            "expr": "ssl_cert_days_until_expiry < 7",
            "legendFormat": "Critical"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
      },
      {
        "id": 4,
        "title": "System Resources",
        "type": "graph",
        "targets": [
          {
            "expr": "100 - (avg by(instance) (rate(node_cpu_seconds_total{mode=\"idle\"}[5m])) * 100)",
            "legendFormat": "CPU Usage %"
          },
          {
            "expr": "(1 - (node_memory_MemAvailable_bytes / node_memory_MemTotal_bytes)) * 100",
            "legendFormat": "Memory Usage %"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 16}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
EOF

# Create backup script for monitoring data
cat > /opt/monitoring/backup.sh << 'EOF'
#!/bin/bash
# Monitoring data backup script

BACKUP_DIR="/opt/monitoring/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="monitoring_backup_${DATE}.tar.gz"

mkdir -p $BACKUP_DIR

# Backup Prometheus data
docker exec prometheus promtool tsdb create-blocks-from openmetrics /prometheus /tmp/backup
docker cp prometheus:/tmp/backup "${BACKUP_DIR}/prometheus_${DATE}"

# Backup Grafana data
docker cp grafana:/var/lib/grafana "${BACKUP_DIR}/grafana_${DATE}"

# Create archive
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" -C "${BACKUP_DIR}" "prometheus_${DATE}" "grafana_${DATE}"

# Cleanup
rm -rf "${BACKUP_DIR}/prometheus_${DATE}" "${BACKUP_DIR}/grafana_${DATE}"

# Keep only last 7 days of backups
find $BACKUP_DIR -name "monitoring_backup_*.tar.gz" -mtime +7 -delete

echo "Monitoring backup completed: ${BACKUP_FILE}"
EOF

chmod +x /opt/monitoring/backup.sh

# Add backup to crontab (daily at 3 AM)
echo "0 3 * * * /opt/monitoring/backup.sh" | crontab -

# Create health check script
cat > /opt/monitoring/health-check.sh << 'EOF'
#!/bin/bash
# Monitoring stack health check

LOG_FILE="/opt/monitoring/logs/health-check.log"
mkdir -p /opt/monitoring/logs

# Check Prometheus
if curl -f -s "http://localhost:9090/-/healthy" > /dev/null; then
    echo "$(date): Prometheus health check passed" >> $LOG_FILE
else
    echo "$(date): Prometheus health check failed" >> $LOG_FILE
    docker-compose -f /opt/monitoring/docker-compose.yml restart prometheus
fi

# Check Grafana
if curl -f -s "http://localhost:3000/api/health" > /dev/null; then
    echo "$(date): Grafana health check passed" >> $LOG_FILE
else
    echo "$(date): Grafana health check failed" >> $LOG_FILE
    docker-compose -f /opt/monitoring/docker-compose.yml restart grafana
fi

# Check Alertmanager
if curl -f -s "http://localhost:9093/-/healthy" > /dev/null; then
    echo "$(date): Alertmanager health check passed" >> $LOG_FILE
else
    echo "$(date): Alertmanager health check failed" >> $LOG_FILE
    docker-compose -f /opt/monitoring/docker-compose.yml restart alertmanager
fi
EOF

chmod +x /opt/monitoring/health-check.sh

# Add health check to crontab (every 5 minutes)
echo "*/5 * * * * /opt/monitoring/health-check.sh" | crontab -

# Create directories
mkdir -p /opt/monitoring/logs
mkdir -p /opt/monitoring/backups

# Set proper permissions
chown -R ubuntu:ubuntu /opt/monitoring

# Start monitoring stack
cd /opt/monitoring
docker-compose up -d

echo "✅ Monitoring server setup completed successfully!"
echo "🔧 Services available:"
echo "- Prometheus: http://10.0.1.20:9090"
echo "- Grafana: http://10.0.1.20:3000 (admin/admin123)"
echo "- Alertmanager: http://10.0.1.20:9093"
echo "- Node Exporter: http://10.0.1.20:9100"
echo "- cAdvisor: http://10.0.1.20:8080"
