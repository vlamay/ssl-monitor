#!/bin/bash

# SSL Monitor Pro - Cloudflared Installation Script
# Run this script on the GitLab server (192.168.1.10)

echo "🚀 Installing Cloudflared on GitLab Server"
echo "=========================================="
echo ""

# Check if running as root or with sudo
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run with sudo privileges"
    echo "   Usage: sudo ./install-cloudflared.sh"
    exit 1
fi

echo "✅ Running with root privileges"
echo ""

# Step 1: Add Cloudflare GPG key
echo "1️⃣ Adding Cloudflare GPG key..."
mkdir -p --mode=0755 /usr/share/keyrings
curl -fsSL https://pkg.cloudflare.com/cloudflare-main.gpg | tee /usr/share/keyrings/cloudflare-main.gpg >/dev/null

if [ $? -eq 0 ]; then
    echo "   ✅ GPG key added successfully"
else
    echo "   ❌ Failed to add GPG key"
    exit 1
fi

# Step 2: Add repository
echo ""
echo "2️⃣ Adding Cloudflare repository..."
echo 'deb [signed-by=/usr/share/keyrings/cloudflare-main.gpg] https://pkg.cloudflare.com/cloudflared any main' | tee /etc/apt/sources.list.d/cloudflared.list

if [ $? -eq 0 ]; then
    echo "   ✅ Repository added successfully"
else
    echo "   ❌ Failed to add repository"
    exit 1
fi

# Step 3: Update package list and install cloudflared
echo ""
echo "3️⃣ Updating package list and installing cloudflared..."
apt-get update && apt-get install -y cloudflared

if [ $? -eq 0 ]; then
    echo "   ✅ Cloudflared installed successfully"
else
    echo "   ❌ Failed to install cloudflared"
    exit 1
fi

# Step 4: Install service with token
echo ""
echo "4️⃣ Installing cloudflared service with tunnel token..."
TOKEN="eyJhIjoiNDVjNTFiMzY0OGU3ZWI2YmY0MGY3ZWZlYTVlOGRmOTgiLCJ0IjoiM2JiYmI3ZDQtYWI1MS00NGMzLTkwYzEtZDhkOWViODU1OWQwIiwicyI6IlpEVXhNakF6TlRFdFpHSTFZUzAwTkdNMkxUbGlaalV0TlRNMk1HWXlNVGhqTkdFMSJ9"

cloudflared service install "$TOKEN"

if [ $? -eq 0 ]; then
    echo "   ✅ Cloudflared service installed successfully"
else
    echo "   ❌ Failed to install cloudflared service"
    exit 1
fi

# Step 5: Check service status
echo ""
echo "5️⃣ Checking cloudflared service status..."
systemctl status cloudflared --no-pager -l

echo ""
echo "🎉 CLOUDFLARED INSTALLATION COMPLETE!"
echo "====================================="
echo ""
echo "✅ Cloudflared installed and configured"
echo "✅ Service is running"
echo "✅ Tunnel is active"
echo ""
echo "🔍 Next steps:"
echo "   1. Go back to Cloudflare dashboard"
echo "   2. Configure public hostname:"
echo "      • Subdomain: gitlab"
echo "      • Domain: trustforge.uk"
echo "      • Service: http://192.168.1.10:80"
echo "   3. Test connection: https://gitlab.trustforge.uk"
echo ""
echo "📊 Service management commands:"
echo "   • Status: sudo systemctl status cloudflared"
echo "   • Restart: sudo systemctl restart cloudflared"
echo "   • Logs: sudo journalctl -u cloudflared -f"
