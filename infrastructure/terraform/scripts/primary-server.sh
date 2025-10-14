#!/bin/bash
# SSL Monitor Pro - Primary Server Setup Script

set -e

# Environment variables
ENVIRONMENT=${environment}
DOMAIN=${domain}

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

# Install Nginx
apt-get install -y nginx certbot python3-certbot-nginx

# Install monitoring tools
apt-get install -y htop iotop nethogs

# Create application directory
mkdir -p /opt/ssl-monitor
cd /opt/ssl-monitor

# Create Docker Compose file for SSL Monitor
cat > docker-compose.yml << 'EOF'
version: '3.8'

services:
  ssl-monitor-api:
    image: ssl-monitor-api:latest
    container_name: ssl-monitor-api
    restart: unless-stopped
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
      - STRIPE_SECRET_KEY=${STRIPE_SECRET_KEY}
      - STRIPE_WEBHOOK_SECRET=${STRIPE_WEBHOOK_SECRET}
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    networks:
      - ssl-monitor-network

  ssl-monitor-worker:
    image: ssl-monitor-api:latest
    container_name: ssl-monitor-worker
    restart: unless-stopped
    command: ["python", "-m", "celery", "worker", "-A", "app.celery", "--loglevel=info"]
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
      - TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    networks:
      - ssl-monitor-network

  ssl-monitor-scheduler:
    image: ssl-monitor-api:latest
    container_name: ssl-monitor-scheduler
    restart: unless-stopped
    command: ["python", "-m", "celery", "beat", "-A", "app.celery", "--loglevel=info"]
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - REDIS_URL=${REDIS_URL}
      - SECRET_KEY=${SECRET_KEY}
      - ENVIRONMENT=production
    volumes:
      - ./logs:/app/logs
    networks:
      - ssl-monitor-network

networks:
  ssl-monitor-network:
    driver: bridge
EOF

# Create environment file
cat > .env << 'EOF'
# Database
DATABASE_URL=postgresql://user:password@database:5432/sslmonitor

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key-here

# Telegram
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id

# Stripe
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_WEBHOOK_SECRET=your-stripe-webhook-secret

# Environment
ENVIRONMENT=production
EOF

# Create Nginx configuration
cat > /etc/nginx/sites-available/ssl-monitor << 'EOF'
server {
    listen 80;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "no-referrer-when-downgrade" always;
    add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req zone=api burst=20 nodelay;
    
    # Health check endpoint
    location /health {
        proxy_pass http://localhost:8000/health;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # API endpoints
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
    
    # Webhook endpoints
    location /billing/webhook {
        proxy_pass http://localhost:8000/billing/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /telegram/webhook {
        proxy_pass http://localhost:8000/telegram/webhook;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    # Static files (if serving from this server)
    location /static/ {
        alias /opt/ssl-monitor/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Default location
    location / {
        return 301 https://$server_name$request_uri;
    }
}

# HTTPS configuration (will be added by Certbot)
server {
    listen 443 ssl http2;
    server_name ${DOMAIN} www.${DOMAIN};
    
    # SSL configuration will be added by Certbot
    
    # Same location blocks as HTTP
    # ... (will be generated by Certbot)
}
EOF

# Enable the site
ln -sf /etc/nginx/sites-available/ssl-monitor /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test Nginx configuration
nginx -t

# Start Nginx
systemctl enable nginx
systemctl start nginx

# Install monitoring agent (Prometheus Node Exporter)
wget https://github.com/prometheus/node_exporter/releases/latest/download/node_exporter-1.6.1.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.1.linux-amd64.tar.gz
mv node_exporter-1.6.1.linux-amd64/node_exporter /usr/local/bin/
rm -rf node_exporter-1.6.1.linux-amd64*

# Create systemd service for Node Exporter
cat > /etc/systemd/system/node_exporter.service << 'EOF'
[Unit]
Description=Node Exporter
After=network.target

[Service]
User=ubuntu
Group=ubuntu
Type=simple
ExecStart=/usr/local/bin/node_exporter
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Start Node Exporter
systemctl daemon-reload
systemctl enable node_exporter
systemctl start node_exporter

# Create log rotation configuration
cat > /etc/logrotate.d/ssl-monitor << 'EOF'
/opt/ssl-monitor/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 ubuntu ubuntu
    postrotate
        docker-compose -f /opt/ssl-monitor/docker-compose.yml restart ssl-monitor-api ssl-monitor-worker ssl-monitor-scheduler
    endscript
}
EOF

# Create backup script
cat > /opt/ssl-monitor/backup.sh << 'EOF'
#!/bin/bash
# SSL Monitor Pro - Backup Script

BACKUP_DIR="/opt/ssl-monitor/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="ssl_monitor_backup_${DATE}.tar.gz"

mkdir -p $BACKUP_DIR

# Backup application data
tar -czf "${BACKUP_DIR}/${BACKUP_FILE}" \
    --exclude="*.log" \
    --exclude="node_modules" \
    --exclude=".git" \
    /opt/ssl-monitor

# Keep only last 7 days of backups
find $BACKUP_DIR -name "ssl_monitor_backup_*.tar.gz" -mtime +7 -delete

echo "Backup completed: ${BACKUP_FILE}"
EOF

chmod +x /opt/ssl-monitor/backup.sh

# Add backup to crontab
echo "0 2 * * * /opt/ssl-monitor/backup.sh" | crontab -

# Create health check script
cat > /opt/ssl-monitor/health-check.sh << 'EOF'
#!/bin/bash
# SSL Monitor Pro - Health Check Script

API_URL="http://localhost:8000/health"
LOG_FILE="/opt/ssl-monitor/logs/health-check.log"

# Check API health
if curl -f -s "$API_URL" > /dev/null; then
    echo "$(date): API health check passed" >> $LOG_FILE
else
    echo "$(date): API health check failed" >> $LOG_FILE
    # Restart API container
    docker-compose -f /opt/ssl-monitor/docker-compose.yml restart ssl-monitor-api
fi

# Check disk space
DISK_USAGE=$(df / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "$(date): Disk usage high: ${DISK_USAGE}%" >> $LOG_FILE
fi

# Check memory usage
MEMORY_USAGE=$(free | awk 'NR==2{printf "%.0f", $3*100/$2}')
if [ $MEMORY_USAGE -gt 80 ]; then
    echo "$(date): Memory usage high: ${MEMORY_USAGE}%" >> $LOG_FILE
fi
EOF

chmod +x /opt/ssl-monitor/health-check.sh

# Add health check to crontab (every 5 minutes)
echo "*/5 * * * * /opt/ssl-monitor/health-check.sh" | crontab -

# Create directories
mkdir -p /opt/ssl-monitor/logs
mkdir -p /opt/ssl-monitor/backups
mkdir -p /opt/ssl-monitor/static

# Set proper permissions
chown -R ubuntu:ubuntu /opt/ssl-monitor

echo "✅ Primary server setup completed successfully!"
echo "🔧 Next steps:"
echo "1. Configure SSL certificates with Certbot"
echo "2. Deploy application with Docker Compose"
echo "3. Set up monitoring and alerting"
echo "4. Configure database connections"
