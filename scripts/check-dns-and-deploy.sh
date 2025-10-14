#!/bin/bash

# SSL Monitor Pro - DNS Check and Deploy Script
# This script checks DNS propagation and triggers Render deployment

echo "🔍 SSL Monitor Pro - DNS Check & Deploy"
echo "======================================"
echo ""

GITLAB_DOMAIN="gitlab.cloudsre.xyz"
GITLAB_IP="192.168.1.10"
RENDER_SERVICE_ID="srv-d3lbqje3jp1c73ej7csg"
RENDER_API_KEY="rnd_hRA8U5HRd4on737k4G51vv6x9ebX"
RENDER_DEPLOY_HOOK="https://api.render.com/deploy/srv-d3lbqje3jp1c73ej7csg?key=xxQEZgXYlEc"

# Function to check DNS
check_dns() {
    echo "🔍 Checking DNS propagation for $GITLAB_DOMAIN..."
    
    # Check if domain resolves
    if nslookup $GITLAB_DOMAIN >/dev/null 2>&1; then
        RESOLVED_IP=$(nslookup $GITLAB_DOMAIN | grep -A1 "Name:" | tail -1 | awk '{print $2}')
        
        if [ "$RESOLVED_IP" = "$GITLAB_IP" ]; then
            echo "✅ DNS propagated successfully!"
            echo "   $GITLAB_DOMAIN → $RESOLVED_IP"
            return 0
        else
            echo "⚠️  DNS propagated but wrong IP: $RESOLVED_IP (expected: $GITLAB_IP)"
            return 1
        fi
    else
        echo "❌ DNS not yet propagated"
        return 1
    fi
}

# Function to check HTTP accessibility
check_http() {
    echo "🌐 Checking HTTP accessibility..."
    
    if curl -s --connect-timeout 10 http://$GITLAB_DOMAIN >/dev/null 2>&1; then
        echo "✅ GitLab is accessible via HTTP"
        return 0
    else
        echo "❌ GitLab not accessible via HTTP"
        return 1
    fi
}

# Function to update Render repository
update_render_repo() {
    echo "🔧 Updating Render repository settings..."
    
    # Update repository URL
    curl -X PATCH \
        "https://api.render.com/v1/services/$RENDER_SERVICE_ID" \
        -H "Authorization: Bearer $RENDER_API_KEY" \
        -H "Content-Type: application/json" \
        -d "{
            \"repo\": \"http://$GITLAB_DOMAIN/root/ssl-monitor-pro.git\"
        }" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Render repository updated successfully"
        echo "   New URL: http://$GITLAB_DOMAIN/root/ssl-monitor-pro.git"
        return 0
    else
        echo "❌ Failed to update Render repository"
        return 1
    fi
}

# Function to trigger Render deployment
trigger_render_deploy() {
    echo "🚀 Triggering Render deployment..."
    
    # Use deploy hook
    curl -X POST "$RENDER_DEPLOY_HOOK" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        echo "✅ Render deployment triggered successfully"
        echo "   Deploy Hook: $RENDER_DEPLOY_HOOK"
        return 0
    else
        echo "❌ Failed to trigger Render deployment"
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

# Main execution
echo "1️⃣ Checking DNS propagation..."
if check_dns; then
    echo ""
    echo "2️⃣ Checking HTTP accessibility..."
    if check_http; then
        echo ""
        echo "3️⃣ Updating Render repository..."
        if update_render_repo; then
            echo ""
            echo "4️⃣ Triggering deployment..."
            if trigger_render_deploy; then
                echo ""
                echo "5️⃣ Checking deployment status..."
                sleep 10  # Wait a bit for deployment to start
                check_render_status
                
                echo ""
                echo "🎉 DNS CHECK & DEPLOY COMPLETE!"
                echo "================================="
                echo "✅ GitLab accessible: http://$GITLAB_DOMAIN"
                echo "✅ Render updated with GitLab repository"
                echo "✅ Deployment triggered"
                echo ""
                echo "🔍 Monitor deployment at:"
                echo "   https://dashboard.render.com/web/$RENDER_SERVICE_ID"
            fi
        fi
    fi
else
    echo ""
    echo "⏳ DNS not ready yet. Please wait and run this script again."
    echo ""
    echo "💡 To check manually:"
    echo "   nslookup $GITLAB_DOMAIN"
    echo "   curl -I http://$GITLAB_DOMAIN"
    exit 1
fi
