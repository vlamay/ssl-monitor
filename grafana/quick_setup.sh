#!/bin/bash

# SSL Monitor Pro - Grafana Quick Setup
# For client dashboards and monitoring

echo "🚀 Setting up Grafana + Prometheus for SSL Monitor Pro..."

# Update system
sudo apt-get update

# Install Grafana
echo "📊 Installing Grafana..."
sudo apt-get install -y software-properties-common
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo apt-get update
sudo apt-get install -y grafana

# Start and enable Grafana
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

echo "✅ Grafana installed and started"
echo "🌐 Access Grafana at: http://localhost:3000"
echo "👤 Default login: admin / admin"

# Install Prometheus
echo "📈 Installing Prometheus..."
cd /tmp
wget https://github.com/prometheus/prometheus/releases/download/v2.45.0/prometheus-2.45.0.linux-amd64.tar.gz
tar xvfz prometheus-*.tar.gz
sudo mv prometheus-2.45.0.linux-amd64 /opt/prometheus

# Create Prometheus config
sudo tee /opt/prometheus/prometheus.yml > /dev/null <<EOF
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'ssl-monitor-api'
    static_configs:
      - targets: ['ssl-monitor-api.onrender.com']
    metrics_path: '/metrics'
    scrape_interval: 30s
  - job_name: 'ssl-monitor-frontend'
    static_configs:
      - targets: ['ssl-monitor-pro.onrender.com']
    metrics_path: '/metrics'
    scrape_interval: 30s
EOF

# Create Prometheus service
sudo tee /etc/systemd/system/prometheus.service > /dev/null <<EOF
[Unit]
Description=Prometheus
Wants=network-online.target
After=network-online.target

[Service]
User=prometheus
Group=prometheus
Type=simple
ExecStart=/opt/prometheus/prometheus \\
  --config.file /opt/prometheus/prometheus.yml \\
  --storage.tsdb.path /opt/prometheus/data \\
  --web.console.templates=/opt/prometheus/consoles \\
  --web.console.libraries=/opt/prometheus/console_libraries \\
  --web.listen-address=0.0.0.0:9090

[Install]
WantedBy=multi-user.target
EOF

# Create prometheus user
sudo useradd --no-create-home --shell /bin/false prometheus
sudo mkdir /opt/prometheus/data
sudo chown prometheus:prometheus /opt/prometheus/data

# Start Prometheus
sudo systemctl daemon-reload
sudo systemctl start prometheus
sudo systemctl enable prometheus

echo "✅ Prometheus installed and started"
echo "🌐 Access Prometheus at: http://localhost:9090"

# Create Grafana dashboard config
sudo tee /opt/grafana/ssl-monitor-dashboard.json > /dev/null <<EOF
{
  "dashboard": {
    "id": null,
    "title": "SSL Monitor Pro - Client Dashboard",
    "tags": ["ssl", "monitoring"],
    "timezone": "Europe/Prague",
    "panels": [
      {
        "id": 1,
        "title": "SSL Certificates Status",
        "type": "stat",
        "targets": [
          {
            "expr": "ssl_cert_days_until_expiry",
            "legendFormat": "Days until expiry"
          }
        ],
        "fieldConfig": {
          "defaults": {
            "color": {
              "mode": "thresholds"
            },
            "thresholds": {
              "steps": [
                {"color": "green", "value": null},
                {"color": "yellow", "value": 30},
                {"color": "red", "value": 7}
              ]
            }
          }
        },
        "gridPos": {"h": 8, "w": 12, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Monitoring Uptime",
        "type": "graph",
        "targets": [
          {
            "expr": "ssl_check_success_rate",
            "legendFormat": "Success Rate"
          }
        ],
        "gridPos": {"h": 8, "w": 12, "x": 12, "y": 0}
      },
      {
        "id": 3,
        "title": "Alert History",
        "type": "table",
        "targets": [
          {
            "expr": "ssl_alerts_total",
            "legendFormat": "Total Alerts"
          }
        ],
        "gridPos": {"h": 8, "w": 24, "x": 0, "y": 8}
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

echo "✅ SSL Monitor Pro Grafana setup complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Open Grafana: http://localhost:3000"
echo "2. Login with: admin / admin"
echo "3. Add Prometheus data source: http://localhost:9090"
echo "4. Import dashboard: /opt/grafana/ssl-monitor-dashboard.json"
echo ""
echo "🎯 For client presentations:"
echo "- Show real-time SSL monitoring"
echo "- Demonstrate alert system"
echo "- Display uptime statistics"
echo ""
echo "💰 Premium Feature:"
echo "Add +2,000 CZK/month for 'Premium Grafana Dashboard Access'"
