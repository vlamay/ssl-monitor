#!/bin/bash

# SSL Monitor Pro - DDNS Setup Script
# This script helps configure DDNS for GitLab public access

echo "🌐 SSL Monitor Pro - DDNS Setup"
echo "==============================="
echo ""

# Configuration variables (to be filled by user)
DDNS_DOMAIN=""
DDNS_TOKEN=""
GITLAB_IP="192.168.1.10"

# Function to get DDNS credentials
get_ddns_credentials() {
    echo "📋 DDNS Configuration"
    echo "====================="
    echo ""
    
    if [ -z "$DDNS_DOMAIN" ]; then
        echo "🌐 Enter your DDNS domain (e.g., gitlab.duckdns.org):"
        read -p "Domain: " DDNS_DOMAIN
    fi
    
    if [ -z "$DDNS_TOKEN" ]; then
        echo ""
        echo "🔑 Enter your DDNS token:"
        read -p "Token: " DDNS_TOKEN
    fi
    
    echo ""
    echo "📝 Configuration:"
    echo "   Domain: $DDNS_DOMAIN"
    echo "   Token: $DDNS_TOKEN"
    echo "   GitLab IP: $GITLAB_IP"
    echo ""
}

# Function to test DDNS domain
test_ddns_domain() {
    echo "🔍 Testing DDNS domain..."
    
    if curl -s --connect-timeout 10 "http://$DDNS_DOMAIN" >/dev/null 2>&1; then
        echo "✅ DDNS domain is accessible: http://$DDNS_DOMAIN"
        return 0
    else
        echo "❌ DDNS domain not accessible: http://$DDNS_DOMAIN"
        echo "   This is normal if DDNS is not yet configured"
        return 1
    fi
}

# Function to test GitLab repository access
test_gitlab_repo() {
    echo "🔍 Testing GitLab repository access..."
    
    if curl -s --connect-timeout 10 "http://$DDNS_DOMAIN/root/ssl-monitor-pro.git" >/dev/null 2>&1; then
        echo "✅ GitLab repository accessible: http://$DDNS_DOMAIN/root/ssl-monitor-pro.git"
        return 0
    else
        echo "❌ GitLab repository not accessible"
        return 1
    fi
}

# Function to update Render with DDNS
update_render_ddns() {
    echo "🔧 Updating Render with DDNS domain..."
    
    echo "📋 Manual steps for Render:"
    echo "   1. Go to: https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg"
    echo "   2. Settings → Build & Deploy → Update Repository"
    echo "   3. URL: http://$DDNS_DOMAIN/root/ssl-monitor-pro.git"
    echo "   4. Save Changes"
    echo "   5. Manual Deploy → Deploy latest commit"
    echo ""
}

# Function to create router configuration guide
create_router_guide() {
    echo "📋 Router Configuration Guide"
    echo "============================="
    echo ""
    echo "🔧 DDNS Settings:"
    echo "   • Service: DuckDNS"
    echo "   • Domain: $DDNS_DOMAIN"
    echo "   • Token: $DDNS_TOKEN"
    echo ""
    echo "🔧 Port Forwarding:"
    echo "   • External Port: 80"
    echo "   • Internal IP: $GITLAB_IP"
    echo "   • Internal Port: 80"
    echo "   • Protocol: TCP"
    echo ""
    echo "🔧 Port Forwarding (HTTPS):"
    echo "   • External Port: 443"
    echo "   • Internal IP: $GITLAB_IP"
    echo "   • Internal Port: 443"
    echo "   • Protocol: TCP"
    echo ""
}

# Function to create test script
create_test_script() {
    echo "📝 Creating test script..."
    
    cat > test-ddns.sh << EOF
#!/bin/bash
# DDNS Test Script

echo "🔍 Testing DDNS Configuration..."
echo "Domain: $DDNS_DOMAIN"
echo "GitLab IP: $GITLAB_IP"
echo ""

echo "1️⃣ Testing domain resolution:"
nslookup $DDNS_DOMAIN

echo ""
echo "2️⃣ Testing HTTP access:"
curl -I http://$DDNS_DOMAIN 2>/dev/null | head -1 || echo "   ❌ HTTP not accessible"

echo ""
echo "3️⃣ Testing GitLab repository:"
curl -I http://$DDNS_DOMAIN/root/ssl-monitor-pro.git 2>/dev/null | head -1 || echo "   ❌ Repository not accessible"

echo ""
echo "4️⃣ Testing GitLab main page:"
curl -s http://$DDNS_DOMAIN | head -5 || echo "   ❌ GitLab not accessible"

echo ""
echo "✅ Test complete!"
EOF

    chmod +x test-ddns.sh
    echo "   ✅ Created test-ddns.sh"
}

# Main execution
echo "1️⃣ Getting DDNS credentials..."
get_ddns_credentials

echo ""
echo "2️⃣ Testing DDNS domain..."
test_ddns_domain

echo ""
echo "3️⃣ Testing GitLab repository..."
test_gitlab_repo

echo ""
echo "4️⃣ Creating router configuration guide..."
create_router_guide

echo ""
echo "5️⃣ Creating test script..."
create_test_script

echo ""
echo "6️⃣ Render update instructions..."
update_render_ddns

echo ""
echo "🎉 DDNS SETUP COMPLETE!"
echo "======================="
echo ""
echo "📋 NEXT STEPS:"
echo "   1. Configure router DDNS settings"
echo "   2. Configure port forwarding"
echo "   3. Wait 5-10 minutes for propagation"
echo "   4. Run: ./test-ddns.sh"
echo "   5. Update Render with DDNS URL"
echo ""
echo "🔍 MONITORING:"
echo "   • Test script: ./test-ddns.sh"
echo "   • DDNS status: https://www.duckdns.org/"
echo "   • Render logs: https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg"
echo ""
echo "📞 SUPPORT:"
echo "   • DDNS issues: Check router configuration"
echo "   • GitLab issues: Check port forwarding"
echo "   • Render issues: Check repository URL"
