#!/bin/bash

# SSL Monitor Pro - Sync GitLab to GitHub
# This script creates a temporary sync between GitLab and GitHub
# so Render can continue using GitHub while we work on GitLab integration

echo "🔄 SSL Monitor Pro - GitLab to GitHub Sync"
echo "=========================================="
echo ""

GITLAB_URL="http://192.168.1.10/root/ssl-monitor-pro.git"
GITHUB_URL="https://github.com/vlamay/ssl-monitor.git"
TEMP_DIR="temp-sync"

# Function to check if we're in the right directory
check_directory() {
    if [ ! -f "README.md" ] || [ ! -d "backend" ] || [ ! -d "frontend" ]; then
        echo "❌ Not in SSL Monitor Pro directory"
        echo "   Please run this script from the project root"
        exit 1
    fi
    echo "✅ In correct directory"
}

# Function to add GitHub remote
add_github_remote() {
    echo "🔗 Adding GitHub remote..."
    
    # Check if GitHub remote already exists
    if git remote get-url github >/dev/null 2>&1; then
        echo "   GitHub remote already exists"
    else
        git remote add github "$GITHUB_URL"
        echo "   ✅ GitHub remote added"
    fi
}

# Function to push to GitHub
push_to_github() {
    echo "📤 Pushing to GitHub..."
    
    # Get current branch
    CURRENT_BRANCH=$(git branch --show-current)
    echo "   Current branch: $CURRENT_BRANCH"
    
    # Push to GitHub
    if git push github "$CURRENT_BRANCH"; then
        echo "   ✅ Successfully pushed to GitHub"
        return 0
    else
        echo "   ❌ Failed to push to GitHub"
        return 1
    fi
}

# Function to create sync script
create_sync_script() {
    echo "📝 Creating automatic sync script..."
    
    cat > sync-to-github.sh << 'EOF'
#!/bin/bash
# Auto-sync GitLab to GitHub
# Run this after each commit to GitLab

echo "🔄 Syncing to GitHub..."

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)

# Push to GitHub
git push github "$CURRENT_BRANCH"

if [ $? -eq 0 ]; then
    echo "✅ Synced to GitHub successfully"
else
    echo "❌ Sync failed"
fi
EOF

    chmod +x sync-to-github.sh
    echo "   ✅ Created sync-to-github.sh"
}

# Function to setup GitLab webhook (placeholder)
setup_gitlab_webhook() {
    echo "🔗 GitLab Webhook Setup (Manual):"
    echo "   1. Go to GitLab: http://192.168.1.10/root/ssl-monitor-pro/-/hooks"
    echo "   2. Add webhook URL: https://api.github.com/repos/vlamay/ssl-monitor/hooks"
    echo "   3. Trigger: Push events"
    echo "   4. Add webhook"
    echo "   ⚠️  This requires GitHub API token"
}

# Main execution
echo "1️⃣ Checking directory..."
check_directory

echo ""
echo "2️⃣ Adding GitHub remote..."
add_github_remote

echo ""
echo "3️⃣ Pushing current code to GitHub..."
if push_to_github; then
    echo ""
    echo "4️⃣ Creating sync script..."
    create_sync_script
    
    echo ""
    echo "🎉 SYNC SETUP COMPLETE!"
    echo "======================"
    echo "✅ GitHub remote added"
    echo "✅ Current code pushed to GitHub"
    echo "✅ Sync script created: ./sync-to-github.sh"
    echo ""
    echo "📋 HOW TO USE:"
    echo "   1. Make changes in GitLab"
    echo "   2. Commit and push to GitLab"
    echo "   3. Run: ./sync-to-github.sh"
    echo "   4. Render will automatically deploy from GitHub"
    echo ""
    echo "🔗 MANUAL SYNC:"
    echo "   git push github main"
    echo ""
    echo "🎯 RESULT:"
    echo "   • GitLab remains primary repository"
    echo "   • GitHub stays in sync"
    echo "   • Render continues working"
    echo "   • No service interruption"
else
    echo ""
    echo "❌ SYNC SETUP FAILED"
    echo "===================="
    echo "Please check:"
    echo "   • GitHub repository exists"
    echo "   • GitHub credentials are correct"
    echo "   • Network connectivity"
fi
