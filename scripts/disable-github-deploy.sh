#!/bin/bash

# SSL Monitor Pro - Disable GitHub Auto-Deploy
# Usage: ./scripts/disable-github-deploy.sh

echo "🚫 Disabling GitHub Auto-Deploy for Migration..."
echo "=============================================="
echo ""

echo "⚠️  IMPORTANT: Manual steps required in external services!"
echo ""
echo "📋 Steps to disable GitHub auto-deploy:"
echo ""

echo "1️⃣ Render.com:"
echo "   • Go to: https://dashboard.render.com"
echo "   • Find service: ssl-monitor-api"
echo "   • Go to: Settings → Build & Deploy"
echo "   • Set Auto-Deploy: Disabled"
echo "   • Set Manual Deploy Only: Enabled"
echo "   • Save changes"
echo ""

echo "2️⃣ Cloudflare Pages:"
echo "   • Go to: https://dash.cloudflare.com"
echo "   • Navigate to: Pages → ssl-monitor-pro"
echo "   • Go to: Settings → Build & Deploy"
echo "   • Disconnect GitHub source"
echo "   • Confirm disconnection"
echo ""

echo "3️⃣ GitLab CI/CD (if any):"
echo "   • Go to: https://192.168.1.10/root/ssl-monitor-pro"
echo "   • Go to: Actions tab"
echo "   • Disable all workflows"
echo "   • Or delete .github/workflows directory"
echo ""

echo "4️⃣ GitHub Webhooks:"
echo "   • Go to: Repository Settings → Webhooks"
echo "   • Disable all webhooks"
echo "   • Or delete them completely"
echo ""

echo "🔍 Verification Steps:"
echo "   1. Check Render Dashboard - no auto-deploys"
echo "   2. Check Cloudflare - no GitHub builds"
echo "   3. Check GitLab CI/CD - no running workflows"
echo "   4. Verify GitLab pipeline is working"
echo ""

echo "✅ After manual steps:"
echo "   • GitHub auto-deploy will be disabled"
echo "   • All deploys will come from GitLab"
echo "   • System will be fully migrated"
echo ""

echo "⚠️  CRITICAL: Do not skip these manual steps!"
echo "   They are required for complete migration."
echo ""

echo "📞 Need help? Check MIGRATION_GUIDE.md Phase 5"
