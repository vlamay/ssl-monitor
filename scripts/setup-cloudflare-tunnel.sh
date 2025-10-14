#!/bin/bash

# SSL Monitor Pro - Cloudflare Tunnel Setup Script
# This script helps set up Cloudflare Tunnel for GitLab public access

echo "🌐 SSL Monitor Pro - Cloudflare Tunnel Setup"
echo "============================================"
echo ""

# Configuration
DOMAIN="trustforge.uk"
SUBDOMAIN="gitlab"
GITLAB_IP="192.168.1.10"
GITLAB_PORT="80"

echo "📋 Configuration:"
echo "   Domain: $DOMAIN"
echo "   Subdomain: $SUBDOMAIN"
echo "   Full URL: https://$SUBDOMAIN.$DOMAIN"
echo "   GitLab: $GITLAB_IP:$GITLAB_PORT"
echo ""

# Function to check if cloudflared is installed
check_cloudflared() {
    echo "🔍 Checking if cloudflared is installed..."
    
    if command -v cloudflared >/dev/null 2>&1; then
        echo "✅ cloudflared is already installed"
        cloudflared --version
        return 0
    else
        echo "❌ cloudflared is not installed"
        return 1
    fi
}

# Function to install cloudflared
install_cloudflared() {
    echo "📦 Installing cloudflared..."
    
    # Detect OS
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "   Detected Linux system"
        
        # Check if it's Ubuntu/Debian
        if command -v apt >/dev/null 2>&1; then
            echo "   Installing via apt..."
            curl -L --output cloudflared.deb https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb
            sudo dpkg -i cloudflared.deb
            rm cloudflared.deb
        # Check if it's CentOS/RHEL
        elif command -v yum >/dev/null 2>&1; then
            echo "   Installing via yum..."
            sudo yum install -y cloudflared
        # Check if snap is available
        elif command -v snap >/dev/null 2>&1; then
            echo "   Installing via snap..."
            sudo snap install cloudflared
        else
            echo "   Installing manually..."
            wget -O cloudflared https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
            chmod +x cloudflared
            sudo mv cloudflared /usr/local/bin/
        fi
    else
        echo "❌ Unsupported OS: $OSTYPE"
        echo "   Please install cloudflared manually"
        return 1
    fi
    
    if check_cloudflared; then
        echo "✅ cloudflared installed successfully"
        return 0
    else
        echo "❌ Failed to install cloudflared"
        return 1
    fi
}

# Function to check GitLab accessibility
check_gitlab_local() {
    echo "🔍 Checking GitLab local accessibility..."
    
    if curl -s --connect-timeout 5 "http://$GITLAB_IP:$GITLAB_PORT" >/dev/null 2>&1; then
        echo "✅ GitLab is accessible locally at http://$GITLAB_IP:$GITLAB_PORT"
        return 0
    else
        echo "❌ GitLab is not accessible locally"
        echo "   Please check if GitLab is running"
        return 1
    fi
}

# Function to create tunnel configuration
create_tunnel_config() {
    echo "📝 Creating tunnel configuration..."
    
    cat > tunnel-config.yml << EOF
tunnel: gitlab-tunnel
credentials-file: /root/.cloudflared/$(uuidgen).json

ingress:
  - hostname: $SUBDOMAIN.$DOMAIN
    service: http://$GITLAB_IP:$GITLAB_PORT
  - service: http_status:404
EOF

    echo "✅ Tunnel configuration created: tunnel-config.yml"
    echo ""
    echo "📋 Configuration content:"
    cat tunnel-config.yml
    echo ""
}

# Function to provide manual setup instructions
provide_manual_instructions() {
    echo "📋 Manual Cloudflare Tunnel Setup Instructions"
    echo "=============================================="
    echo ""
    echo "1️⃣ CLOUDFLARE DASHBOARD:"
    echo "   • Go to: https://dash.cloudflare.com/"
    echo "   • Select domain: $DOMAIN"
    echo "   • Go to: Zero Trust → Access → Tunnels"
    echo "   • Click: 'Create a tunnel'"
    echo "   • Name: gitlab-tunnel"
    echo ""
    echo "2️⃣ INSTALL CLOUDFLARED:"
    echo "   • Copy the installation command from Cloudflare"
    echo "   • Run it on this server ($GITLAB_IP)"
    echo ""
    echo "3️⃣ CONFIGURE TUNNEL:"
    echo "   • Copy the tunnel token from Cloudflare"
    echo "   • Run: cloudflared tunnel run --token [TOKEN]"
    echo ""
    echo "4️⃣ ADD PUBLIC HOSTNAME:"
    echo "   • In tunnel settings, add public hostname:"
    echo "   • Subdomain: $SUBDOMAIN"
    echo "   • Domain: $DOMAIN"
    echo "   • Service: http://$GITLAB_IP:$GITLAB_PORT"
    echo ""
    echo "5️⃣ TEST CONNECTION:"
    echo "   • curl -I https://$SUBDOMAIN.$DOMAIN"
    echo "   • Should return GitLab response"
    echo ""
    echo "6️⃣ UPDATE RENDER:"
    echo "   • Repository URL: https://$SUBDOMAIN.$DOMAIN/root/ssl-monitor-pro.git"
    echo ""
}

# Function to create test script
create_test_script() {
    echo "📝 Creating test script..."
    
    cat > test-tunnel.sh << EOF
#!/bin/bash
# Cloudflare Tunnel Test Script

echo "🔍 Testing Cloudflare Tunnel..."
echo "Domain: $SUBDOMAIN.$DOMAIN"
echo "GitLab: $GITLAB_IP:$GITLAB_PORT"
echo ""

echo "1️⃣ Testing domain resolution:"
nslookup $SUBDOMAIN.$DOMAIN

echo ""
echo "2️⃣ Testing HTTPS access:"
curl -I https://$SUBDOMAIN.$DOMAIN 2>/dev/null | head -1 || echo "   ❌ HTTPS not accessible"

echo ""
echo "3️⃣ Testing GitLab repository:"
curl -I https://$SUBDOMAIN.$DOMAIN/root/ssl-monitor-pro.git 2>/dev/null | head -1 || echo "   ❌ Repository not accessible"

echo ""
echo "4️⃣ Testing GitLab main page:"
curl -s https://$SUBDOMAIN.$DOMAIN | head -5 || echo "   ❌ GitLab not accessible"

echo ""
echo "✅ Test complete!"
EOF

    chmod +x test-tunnel.sh
    echo "   ✅ Created test-tunnel.sh"
}

# Main execution
echo "1️⃣ Checking cloudflared installation..."
if ! check_cloudflared; then
    echo ""
    echo "2️⃣ Installing cloudflared..."
    if ! install_cloudflared; then
        echo ""
        echo "❌ Installation failed. Please install manually."
        provide_manual_instructions
        exit 1
    fi
fi

echo ""
echo "3️⃣ Checking GitLab local accessibility..."
if ! check_gitlab_local; then
    echo ""
    echo "❌ GitLab is not accessible locally"
    echo "   Please start GitLab first"
    exit 1
fi

echo ""
echo "4️⃣ Creating tunnel configuration..."
create_tunnel_config

echo ""
echo "5️⃣ Creating test script..."
create_test_script

echo ""
echo "6️⃣ Providing manual setup instructions..."
provide_manual_instructions

echo ""
echo "🎉 CLOUDFLARE TUNNEL SETUP COMPLETE!"
echo "===================================="
echo ""
echo "📋 NEXT STEPS:"
echo "   1. Follow manual instructions above"
echo "   2. Create tunnel in Cloudflare dashboard"
echo "   3. Install and run cloudflared with token"
echo "   4. Add public hostname"
echo "   5. Test: ./test-tunnel.sh"
echo "   6. Update Render with tunnel URL"
echo ""
echo "🔍 FILES CREATED:"
echo "   • tunnel-config.yml (tunnel configuration)"
echo "   • test-tunnel.sh (test script)"
echo ""
echo "📞 SUPPORT:"
echo "   • Cloudflare docs: https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/"
echo "   • Tunnel troubleshooting: Check cloudflared logs"
