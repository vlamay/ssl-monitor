#!/bin/bash

# SSL Monitor Pro - Update Render to use trustforge.uk domain
# This script updates Render to use the new trustforge.uk domain

echo "🇬🇧 SSL Monitor Pro - Update Render to trustforge.uk"
echo "===================================================="
echo ""

GITLAB_DOMAIN="gitlab.trustforge.uk"
GITLAB_IP="192.168.1.10"
RENDER_SERVICE_ID="srv-d3lbqje3jp1c73ej7csg"
RENDER_API_KEY="rnd_hRA8U5HRd4on737k4G51vv6x9ebX"
RENDER_DEPLOY_HOOK="https://api.render.com/deploy/srv-d3lbqje3jp1c73ej7csg?key=xxQEZgXYlEc"

# Function to check DNS propagation
check_dns_propagation() {
    echo "🔍 Checking DNS propagation for $GITLAB_DOMAIN..."
    
    # Try different DNS servers
    for dns in "8.8.8.8" "1.1.1.1" "208.67.222.222"; do
        echo "   Checking via DNS $dns..."
        RESULT=$(nslookup $GITLAB_DOMAIN $dns 2>/dev/null | grep -A1 "Name:" | tail -1 | awk '{print $2}')
        
        if [ "$RESULT" = "$GITLAB_IP" ]; then
            echo "   ✅ DNS propagated via $dns: $RESULT"
            return 0
        elif [ -n "$RESULT" ]; then
            echo "   ⚠️  DNS resolved but wrong IP: $RESULT (expected: $GITLAB_IP)"
        else
            echo "   ❌ No answer from $dns"
        fi
    done
    
    return 1
}

# Function to check HTTP accessibility
check_http_accessibility() {
    echo "🌐 Checking HTTP accessibility..."
    
    if curl -s --connect-timeout 10 http://$GITLAB_DOMAIN >/dev/null 2>&1; then
        echo "✅ GitLab is accessible via HTTP: http://$GITLAB_DOMAIN"
        return 0
    else
        echo "❌ GitLab not accessible via HTTP: http://$GITLAB_DOMAIN"
        return 1
    fi
}

# Function to check GitLab IP as fallback
check_gitlab_ip() {
    echo "🔍 Checking GitLab IP fallback..."
    
    if curl -s --connect-timeout 10 http://$GITLAB_IP >/dev/null 2>&1; then
        echo "✅ GitLab is accessible via IP: http://$GITLAB_IP"
        return 0
    else
        echo "❌ GitLab not accessible via IP: http://$GITLAB_IP"
        return 1
    fi
}

# Function to update Render repository
update_render_repo() {
    local repo_url=$1
    echo "🔧 Updating Render repository..."
    echo "   New URL: $repo_url"
    
    RESPONSE=$(curl -X PATCH \
        "https://api.render.com/v1/services/$RENDER_SERVICE_ID" \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"repo\": \"$repo_url\"
        }" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "✅ Render repository updated successfully"
        return 0
    else
        echo "❌ Failed to update Render repository"
        echo "   Response: $RESPONSE"
        return 1
    fi
}

# Function to trigger Render deployment
trigger_render_deploy() {
    echo "🚀 Triggering Render deployment..."
    
    RESPONSE=$(curl -X POST "$RENDER_DEPLOY_HOOK" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "✅ Render deployment triggered successfully"
        echo "   Deploy Hook: $RENDER_DEPLOY_HOOK"
        return 0
    else
        echo "❌ Failed to trigger Render deployment"
        echo "   Response: $RESPONSE"
        return 1
    fi
}

# Function to check Render deployment status
check_render_status() {
    echo "📊 Checking Render deployment status..."
    
    STATUS=$(curl -s \
        "https://api.render.com/v1/services/$RENDER_SERVICE_ID" \
        -H "Authorization: Bearer $RENDER_API_KEY" | \
        jq -r '.service.state' 2>/dev/null)
    
    if [ "$STATUS" != "null" ] && [ "$STATUS" != "" ]; then
        echo "   Render Service Status: $STATUS"
        
        if [ "$STATUS" = "live" ]; then
            echo "✅ Render service is live"
            return 0
        else
            echo "⏳ Render service status: $STATUS"
            return 1
        fi
    else
        echo "❌ Could not get Render status"
        return 1
    fi
}

# Function to check production health
check_production_health() {
    echo "🏥 Checking production health..."
    
    HEALTH_RESPONSE=$(curl -s https://ssl-monitor-api.onrender.com/health 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        STATUS=$(echo "$HEALTH_RESPONSE" | jq -r '.status' 2>/dev/null)
        if [ "$STATUS" = "healthy" ]; then
            echo "✅ Production system is healthy"
            echo "   Response: $HEALTH_RESPONSE"
            return 0
        else
            echo "⚠️  Production system status: $STATUS"
            return 1
        fi
    else
        echo "❌ Could not check production health"
        return 1
    fi
}

# Main execution
echo "1️⃣ Checking DNS propagation..."
if check_dns_propagation; then
    echo ""
    echo "2️⃣ Checking HTTP accessibility..."
    if check_http_accessibility; then
        echo ""
        echo "3️⃣ Updating Render repository with domain..."
        if update_render_repo "http://$GITLAB_DOMAIN/root/ssl-monitor-pro.git"; then
            echo ""
            echo "4️⃣ Triggering deployment..."
            if trigger_render_deploy; then
                echo ""
                echo "5️⃣ Waiting for deployment to start..."
                sleep 15
                
                echo ""
                echo "6️⃣ Checking deployment status..."
                check_render_status
                
                echo ""
                echo "7️⃣ Checking production health..."
                sleep 30
                check_production_health
                
                echo ""
                echo "🎉 TRUSTFORGE.UK UPDATE COMPLETE!"
                echo "=================================="
                echo "✅ GitLab accessible: http://$GITLAB_DOMAIN"
                echo "✅ Render updated with trustforge.uk domain"
                echo "✅ Deployment triggered"
                echo ""
                echo "🔍 Monitor deployment at:"
                echo "   https://dashboard.render.com/web/$RENDER_SERVICE_ID"
                echo ""
                echo "🔍 Check production health:"
                echo "   https://ssl-monitor-api.onrender.com/health"
            fi
        fi
    else
        echo ""
        echo "⚠️  HTTP not accessible, trying IP fallback..."
        if check_gitlab_ip; then
            echo ""
            echo "3️⃣ Updating Render repository with IP..."
            if update_render_repo "http://$GITLAB_IP/root/ssl-monitor-pro.git"; then
                echo ""
                echo "4️⃣ Triggering deployment..."
                trigger_render_deploy
            fi
        fi
    fi
else
    echo ""
    echo "⏳ DNS not ready yet. Please wait and run this script again."
    echo ""
    echo "💡 To check manually:"
    echo "   nslookup $GITLAB_DOMAIN 8.8.8.8"
    echo "   curl -I http://$GITLAB_DOMAIN"
    echo ""
    echo "🔄 Or run: ./scripts/update-render-ip.sh (for IP fallback)"
    exit 1
fi
