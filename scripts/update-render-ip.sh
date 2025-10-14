#!/bin/bash

# SSL Monitor Pro - Update Render to use GitLab IP
# This script updates Render to use GitLab IP directly instead of domain

echo "🔧 SSL Monitor Pro - Update Render to GitLab IP"
echo "=============================================="
echo ""

GITLAB_IP="192.168.1.10"
RENDER_SERVICE_ID="srv-d3lbqje3jp1c73ej7csg"
RENDER_API_KEY="rnd_hRA8U5HRd4on737k4G51vv6x9ebX"
RENDER_DEPLOY_HOOK="https://api.render.com/deploy/srv-d3lbqje3jp1c73ej7csg?key=xxQEZgXYlEc"

# Function to check GitLab IP accessibility
check_gitlab_ip() {
    echo "🔍 Checking GitLab IP accessibility..."
    
    if curl -s --connect-timeout 10 http://$GITLAB_IP >/dev/null 2>&1; then
        echo "✅ GitLab is accessible via IP: $GITLAB_IP"
        return 0
    else
        echo "❌ GitLab not accessible via IP: $GITLAB_IP"
        return 1
    fi
}

# Function to update Render repository to use IP
update_render_repo_ip() {
    echo "🔧 Updating Render repository to use GitLab IP..."
    
    # Update repository URL to use IP
    RESPONSE=$(curl -X PATCH \
        "https://api.render.com/v1/services/$RENDER_SERVICE_ID" \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"repo\": \"http://$GITLAB_IP/root/ssl-monitor-pro.git\"
        }" 2>/dev/null)
    
    if [ $? -eq 0 ]; then
        echo "✅ Render repository updated successfully"
        echo "   New URL: http://$GITLAB_IP/root/ssl-monitor-pro.git"
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
    
    # Use deploy hook
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
    
    # Get service status
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
echo "1️⃣ Checking GitLab IP accessibility..."
if check_gitlab_ip; then
    echo ""
    echo "2️⃣ Updating Render repository to use IP..."
    if update_render_repo_ip; then
        echo ""
        echo "3️⃣ Triggering deployment..."
        if trigger_render_deploy; then
            echo ""
            echo "4️⃣ Waiting for deployment to start..."
            sleep 15  # Wait for deployment to start
            
            echo ""
            echo "5️⃣ Checking deployment status..."
            check_render_status
            
            echo ""
            echo "6️⃣ Checking production health..."
            sleep 30  # Wait for deployment to complete
            check_production_health
            
            echo ""
            echo "🎉 RENDER UPDATE COMPLETE!"
            echo "=========================="
            echo "✅ GitLab accessible: http://$GITLAB_IP"
            echo "✅ Render updated with GitLab IP"
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
    echo "❌ GitLab IP not accessible. Please check:"
    echo "   • GitLab server is running"
    echo "   • Network connectivity"
    echo "   • Firewall settings"
    exit 1
fi
