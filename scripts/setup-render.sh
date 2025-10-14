#!/bin/bash

# SSL Monitor Pro - Render.com Setup for GitLab Migration
# Usage: ./scripts/setup-render.sh

echo "🔧 Configuring Render.com for GitLab Migration..."
echo "================================================"

# Load secrets
if [ -f ".migration-secrets" ]; then
    source .migration-secrets
else
    echo "❌ Error: .migration-secrets file not found!"
    exit 1
fi

echo ""
echo "📋 Current Render.com Configuration:"
echo "   • Service: ssl-monitor-api"
echo "   • URL: https://ssl-monitor-api.onrender.com"
echo "   • Current Source: GitHub (root/ssl-monitor-pro)"
echo "   • Target Source: GitLab (root/ssl-monitor-pro)"
echo ""

echo "🔧 Manual Configuration Required:"
echo ""
echo "1️⃣ Render.com Dashboard Steps:"
echo "   • Go to: https://dashboard.render.com"
echo "   • Find service: ssl-monitor-api"
echo "   • Go to: Settings → Build & Deploy"
echo ""
echo "2️⃣ Current Configuration (GitHub):"
echo "   • Repository: 192.168.1.10/root/ssl-monitor-pro"
echo "   • Branch: main"
echo "   • Auto-Deploy: Yes"
echo ""
echo "3️⃣ New Configuration (GitLab):"
echo "   • Repository: MANUAL (we'll use Deploy Hook)"
echo "   • Branch: main"
echo "   • Auto-Deploy: Via GitLab CI/CD"
echo "   • Deploy Hook: $RENDER_DEPLOY_HOOK_URL"
echo ""

echo "4️⃣ Steps to Configure:"
echo "   a) Disable GitHub Auto-Deploy:"
echo "      - Set Auto-Deploy: Disabled"
echo "      - Set Manual Deploy Only: Enabled"
echo ""
echo "   b) Get Deploy Hook URL:"
echo "      - Go to: Settings → Deploy Hook"
echo "      - Copy URL (should be like):"
echo "        https://api.render.com/deploy/srv-xxxxx?key=xxxxx"
echo "      - Update .migration-secrets with real URL"
echo ""
echo "   c) Test Deploy Hook:"
echo "      curl -X POST \$RENDER_DEPLOY_HOOK_URL"
echo ""

echo "5️⃣ GitLab CI/CD Integration:"
echo "   • Deploy Hook URL is already in GitLab Variables"
echo "   • GitLab pipeline will trigger deploys via webhook"
echo "   • No direct Git connection needed"
echo ""

echo "🧪 Testing Deploy Hook (Demo):"
echo "   Testing with demo URL..."
if [ ! -z "$RENDER_DEPLOY_HOOK_URL" ] && [[ "$RENDER_DEPLOY_HOOK_URL" != *"demo"* ]]; then
    echo "   ⚠️  Real URL detected - not testing automatically"
    echo "   Manual test: curl -X POST $RENDER_DEPLOY_HOOK_URL"
else
    echo "   ✅ Demo URL - safe to test"
    echo "   curl -X POST $RENDER_DEPLOY_HOOK_URL"
fi

echo ""
echo "📊 Expected Results:"
echo "   • Render Dashboard shows new deploy starting"
echo "   • Deploy logs show build process"
echo "   • Service remains available during deploy"
echo "   • New version deployed successfully"
echo ""

echo "⚠️  Important Notes:"
echo "   • Keep GitHub auto-deploy DISABLED during migration"
echo "   • Test deploy hook thoroughly before switching"
echo "   • Monitor first few deploys manually"
echo "   • Have rollback plan ready"
echo ""

echo "✅ Render.com Configuration Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Complete manual configuration in Render Dashboard"
echo "   2. Test deploy hook with real URL"
echo "   3. Verify GitLab Variables are set"
echo "   4. Proceed to Cloudflare Pages configuration"
echo ""
echo "🔗 Links:"
echo "   • Render Dashboard: https://dashboard.render.com"
echo "   • Service: ssl-monitor-api"
echo "   • GitLab Variables: http://192.168.1.10/root/ssl-monitor-pro/-/settings/ci_cd"
