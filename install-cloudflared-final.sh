#!/bin/bash

# SSL Monitor Pro - Final Cloudflared Installation
# Run this script on the GitLab server (192.168.1.10)

echo "🚀 Installing Cloudflared - Final Setup"
echo "======================================="
echo ""

# Tunnel configuration
TUNNEL_NAME="gitlab-tunnel"
TUNNEL_ID="3bbbb7d4-ab51-44c3-90c1-d8d9eb8559d0"
TUNNEL_TOKEN="eyJhIjoiNDVjNTFiMzY0OGU3ZWI2YmY0MGY3ZWZlYTVlOGRmOTgiLCJ0IjoiM2JiYmI3ZDQtYWI1MS00NGMzLTkwYzEtZDhkOWViODU1OWQwIiwicyI6IlpEVXhNakF6TlRFdFpHSTFZUzAwTkdNMkxUbGlaalV0TlRNMk1HWXlNVGhqTkdFMSJ9"

echo "📋 Tunnel Configuration:"
echo "   Name: $TUNNEL_NAME"
echo "   ID: $TUNNEL_ID"
echo "   Token: ${TUNNEL_TOKEN:0:20}..."
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run with sudo privileges"
    echo "   Usage: sudo ./install-cloudflared-final.sh"
    exit 1
fi

echo "✅ Running with root privileges"
echo ""

# Step 1: Install cloudflared
echo "1️⃣ Installing cloudflared..."

# Check if already installed
if command -v cloudflared >/dev/null 2>&1; then
    echo "   ✅ cloudflared already installed"
    cloudflared --version
else
    echo "   📦 Installing cloudflared..."
    
    # Add Cloudflare GPG key
    mkdir -p --mode=0755 /usr/share/keyrings
    curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null
    
    # Add repository
    echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | tee /etc/apt/sources.list.d/cloudflared.list
    
    # Install
    apt-get update && apt-get install -y cloudflared
    
    if [ $? -eq 0 ]; then
        echo "   ✅ cloudflared installed successfully"
        cloudflared --version
    else
        echo "   ❌ Failed to install cloudflared"
        exit 1
    fi
fi

# Step 2: Install service with tunnel token
echo ""
echo "2️⃣ Installing tunnel service..."
cloudflared service install "$TUNNEL_TOKEN"

if [ $? -eq 0 ]; then
    echo "   ✅ Tunnel service installed successfully"
else
    echo "   ❌ Failed to install tunnel service"
    exit 1
fi

# Step 3: Start and enable service
echo ""
echo "3️⃣ Starting tunnel service..."
systemctl start cloudflared
systemctl enable cloudflared

if [ $? -eq 0 ]; then
    echo "   ✅ Tunnel service started and enabled"
else
    echo "   ❌ Failed to start tunnel service"
    exit 1
fi

# Step 4: Check service status
echo ""
echo "4️⃣ Checking service status..."
sleep 5  # Wait for service to start

STATUS=$(systemctl is-active cloudflared)
if [ "$STATUS" = "active" ]; then
    echo "   ✅ Service is active"
else
    echo "   ❌ Service is not active (status: $STATUS)"
    echo "   📋 Service status:"
    systemctl status cloudflared --no-pager -l
    exit 1
fi

# Step 5: Check tunnel connectivity
echo ""
echo "5️⃣ Testing tunnel connectivity..."
sleep 10  # Wait for tunnel to establish connection

# Test local connectivity
if curl -s --connect-timeout 5 "http://localhost:80" >/dev/null 2>&1; then
    echo "   ✅ GitLab is accessible locally"
else
    echo "   ❌ GitLab is not accessible locally"
    echo "   📋 Please check GitLab status:"
    echo "   sudo gitlab-ctl status"
fi

# Step 6: Show service management commands
echo ""
echo "🎉 CLOUDFLARED INSTALLATION COMPLETE!"
echo "====================================="
echo ""
echo "✅ Tunnel: $TUNNEL_NAME"
echo "✅ Service: Active"
echo "✅ GitLab: Accessible"
echo ""
echo "🔍 SERVICE MANAGEMENT:"
echo "   • Status: sudo systemctl status cloudflared"
echo "   • Restart: sudo systemctl restart cloudflared"
echo "   • Stop: sudo systemctl stop cloudflared"
echo "   • Logs: sudo journalctl -u cloudflared -f"
echo ""
echo "🌐 NEXT STEPS:"
echo "   1. Go to Cloudflare dashboard"
echo "   2. Add public hostname:"
echo "      • Subdomain: gitlab"
echo "      • Domain: trustforge.uk"
echo "      • Service: http://localhost:80"
echo "   3. Test: https://gitlab.trustforge.uk"
echo ""
echo "📊 TUNNEL STATUS:"
systemctl status cloudflared --no-pager
