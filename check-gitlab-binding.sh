#!/bin/bash

# SSL Monitor Pro - Check GitLab Binding
# Check what IP addresses GitLab is listening on

echo "🔍 Checking GitLab Binding Configuration"
echo "========================================"
echo ""

GITLAB_IP="192.168.1.10"

echo "📋 Checking GitLab server ($GITLAB_IP) binding..."
echo ""

# Function to check local network connectivity
check_local_connectivity() {
    echo "1️⃣ Checking local network connectivity..."
    
    if ping -c 1 $GITLAB_IP >/dev/null 2>&1; then
        echo "   ✅ GitLab server is reachable: $GITLAB_IP"
        return 0
    else
        echo "   ❌ GitLab server is not reachable: $GITLAB_IP"
        return 1
    fi
}

# Function to check HTTP connectivity
check_http_connectivity() {
    echo "2️⃣ Checking HTTP connectivity..."
    
    # Test different URLs
    for URL in "http://$GITLAB_IP:80" "http://localhost:80" "http://127.0.0.1:80"; do
        echo "   Testing: $URL"
        if curl -s --connect-timeout 5 "$URL" >/dev/null 2>&1; then
            echo "   ✅ Accessible: $URL"
            return 0
        else
            echo "   ❌ Not accessible: $URL"
        fi
    done
    return 1
}

# Function to provide recommendations
provide_recommendations() {
    echo ""
    echo "💡 RECOMMENDATIONS FOR CLOUDFLARE TUNNEL:"
    echo "=========================================="
    echo ""
    echo "🔧 TRY THESE SERVICE URLS (in order):"
    echo ""
    echo "1️⃣ http://localhost:80"
    echo "   • Most common for local services"
    echo ""
    echo "2️⃣ http://127.0.0.1:80"
    echo "   • Alternative to localhost"
    echo ""
    echo "3️⃣ http://0.0.0.0:80"
    echo "   • If GitLab binds to all interfaces"
    echo ""
    echo "4️⃣ http://$GITLAB_IP:80"
    echo "   • If GitLab specifically binds to this IP"
    echo ""
    echo "🎯 CLOUDFLARE TUNNEL SETTINGS:"
    echo "   • Subdomain: gitlab"
    echo "   • Domain: trustforge.uk"
    echo "   • Path: / (empty)"
    echo "   • Service Type: HTTP"
    echo "   • Service URL: [try the URLs above]"
    echo ""
    echo "📋 IF ALL FAIL:"
    echo "   1. Check GitLab configuration"
    echo "   2. Ensure GitLab binds to 0.0.0.0:80 (not just localhost)"
    echo "   3. Check firewall settings"
    echo "   4. Verify GitLab is actually running on port 80"
}

# Function to check GitLab configuration
check_gitlab_config() {
    echo ""
    echo "🔧 GITLAB CONFIGURATION CHECK:"
    echo "=============================="
    echo ""
    echo "📋 Commands to run on GitLab server ($GITLAB_IP):"
    echo ""
    echo "1️⃣ Check what's listening on port 80:"
    echo "   sudo netstat -tlnp | grep :80"
    echo "   # or"
    echo "   sudo ss -tlnp | grep :80"
    echo ""
    echo "2️⃣ Check GitLab configuration:"
    echo "   sudo grep -r 'external_url' /etc/gitlab/"
    echo "   sudo grep -r 'listen.*80' /etc/gitlab/"
    echo ""
    echo "3️⃣ Check GitLab status:"
    echo "   sudo gitlab-ctl status"
    echo ""
    echo "4️⃣ Restart GitLab (if needed):"
    echo "   sudo gitlab-ctl restart"
    echo ""
    echo "5️⃣ Check GitLab logs:"
    echo "   sudo gitlab-ctl tail nginx"
}

# Main execution
echo "Checking GitLab binding for Cloudflare Tunnel setup..."
echo ""

if check_local_connectivity; then
    echo ""
    if check_http_connectivity; then
        echo ""
        echo "✅ GitLab is accessible!"
        provide_recommendations
    else
        echo ""
        echo "❌ GitLab HTTP service issues detected"
        check_gitlab_config
    fi
else
    echo ""
    echo "❌ GitLab server connectivity issues"
    check_gitlab_config
fi

echo ""
echo "🎯 NEXT STEPS:"
echo "=============="
echo "1. Try the recommended Service URLs in Cloudflare"
echo "2. If still failing, check GitLab configuration on server"
echo "3. Ensure GitLab is properly configured and running"
echo "4. Test the tunnel once Service URL is working"
