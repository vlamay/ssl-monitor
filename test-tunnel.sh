#!/bin/bash

# SSL Monitor Pro - Tunnel Testing Script
# Test Cloudflare Tunnel connectivity

echo "🔍 Testing Cloudflare Tunnel"
echo "============================"
echo ""

TUNNEL_URL="https://gitlab.trustforge.uk"
GITLAB_REPO_URL="$TUNNEL_URL/root/ssl-monitor-pro.git"

# Function to test basic connectivity
test_basic_connectivity() {
    echo "1️⃣ Testing basic connectivity..."
    
    if curl -s --connect-timeout 10 "$TUNNEL_URL" >/dev/null 2>&1; then
        echo "   ✅ Basic connectivity: OK"
        return 0
    else
        echo "   ❌ Basic connectivity: FAILED"
        return 1
    fi
}

# Function to test GitLab main page
test_gitlab_page() {
    echo "2️⃣ Testing GitLab main page..."
    
    RESPONSE=$(curl -s -I "$TUNNEL_URL" 2>/dev/null | head -1)
    
    if [[ "$RESPONSE" == *"200"* ]] || [[ "$RESPONSE" == *"302"* ]]; then
        echo "   ✅ GitLab page: OK ($RESPONSE)"
        return 0
    else
        echo "   ❌ GitLab page: FAILED ($RESPONSE)"
        return 1
    fi
}

# Function to test repository access
test_repository_access() {
    echo "3️⃣ Testing repository access..."
    
    RESPONSE=$(curl -s -I "$GITLAB_REPO_URL" 2>/dev/null | head -1)
    
    if [[ "$RESPONSE" == *"200"* ]] || [[ "$RESPONSE" == *"302"* ]]; then
        echo "   ✅ Repository access: OK ($RESPONSE)"
        return 0
    else
        echo "   ❌ Repository access: FAILED ($RESPONSE)"
        return 1
    fi
}

# Function to test SSL certificate
test_ssl_certificate() {
    echo "4️⃣ Testing SSL certificate..."
    
    if echo | openssl s_client -servername gitlab.trustforge.uk -connect gitlab.trustforge.uk:443 2>/dev/null | openssl x509 -noout -dates >/dev/null 2>&1; then
        echo "   ✅ SSL certificate: OK"
        return 0
    else
        echo "   ❌ SSL certificate: FAILED"
        return 1
    fi
}

# Function to test response time
test_response_time() {
    echo "5️⃣ Testing response time..."
    
    TIME=$(curl -s -o /dev/null -w '%{time_total}' "$TUNNEL_URL" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Response time: ${TIME}s"
        return 0
    else
        echo "   ❌ Response time: FAILED"
        return 1
    fi
}

# Function to provide next steps
provide_next_steps() {
    echo ""
    echo "🎯 NEXT STEPS:"
    echo "=============="
    echo ""
    echo "1️⃣ UPDATE RENDER:"
    echo "   • Go to: https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg"
    echo "   • Settings → Build & Deploy → Update Repository"
    echo "   • URL: $GITLAB_REPO_URL"
    echo "   • Save Changes"
    echo ""
    echo "2️⃣ TRIGGER DEPLOYMENT:"
    echo "   • Manual Deploy → Deploy latest commit"
    echo "   • Wait for deployment to complete"
    echo ""
    echo "3️⃣ VERIFY INTEGRATION:"
    echo "   • Check Render logs"
    echo "   • Test production health: https://ssl-monitor-api.onrender.com/health"
    echo ""
    echo "4️⃣ COMPLETE CI/CD:"
    echo "   • GitLab → Render integration complete"
    echo "   • Automatic deployments enabled"
    echo "   • MimeText issue resolved"
}

# Main execution
echo "Testing tunnel: $TUNNEL_URL"
echo "Repository URL: $GITLAB_REPO_URL"
echo ""

PASSED_TESTS=0
TOTAL_TESTS=5

if test_basic_connectivity; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

echo ""
if test_gitlab_page; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

echo ""
if test_repository_access; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

echo ""
if test_ssl_certificate; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

echo ""
if test_response_time; then
    PASSED_TESTS=$((PASSED_TESTS + 1))
fi

echo ""
echo "📊 TEST RESULTS:"
echo "================"
echo "✅ Tests Passed: $PASSED_TESTS/$TOTAL_TESTS"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo "🎉 ALL TESTS PASSED!"
    echo "✅ Tunnel is working perfectly"
    provide_next_steps
elif [ $PASSED_TESTS -ge 3 ]; then
    echo "⚠️  MOSTLY WORKING"
    echo "✅ Tunnel is functional"
    provide_next_steps
else
    echo "❌ TUNNEL ISSUES DETECTED"
    echo ""
    echo "🔧 TROUBLESHOOTING:"
    echo "   1. Check if cloudflared is running: sudo systemctl status cloudflared"
    echo "   2. Check cloudflared logs: sudo journalctl -u cloudflared -f"
    echo "   3. Verify GitLab is running: curl -I http://192.168.1.10:80"
    echo "   4. Check Cloudflare tunnel status in dashboard"
fi
