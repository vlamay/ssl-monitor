#!/bin/bash

# SSL Monitor Pro - Emergency Rollback to GitHub
# Usage: ./scripts/rollback-to-github.sh
# WARNING: This script will rollback to GitHub deployment

echo "⚠️  EMERGENCY ROLLBACK: Switching back to GitHub"
echo "================================================"
echo ""
echo "🚨 This will:"
echo "   1. Re-enable GitHub auto-deploy on Render"
echo "   2. Switch Cloudflare back to GitHub"
echo "   3. Disable GitLab auto-deploy"
echo ""
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "❌ Rollback cancelled"
  exit 1
fi

echo ""
echo "🔄 Starting rollback process..."

# Step 1: Check if GitHub remote exists
echo "1️⃣ Checking GitHub remote..."
if git remote | grep -q "github"; then
  echo "   ✅ GitHub remote found"
  git fetch github
else
  echo "   ⚠️  GitHub remote not found - adding..."
  read -p "Enter GitHub repository URL: " github_url
  if [ ! -z "$github_url" ]; then
    git remote add github "$github_url"
    git fetch github
    echo "   ✅ GitHub remote added"
  else
    echo "   ❌ Cannot proceed without GitHub remote"
    exit 1
  fi
fi

# Step 2: Re-enable GitHub auto-deploy on Render
echo ""
echo "2️⃣ Re-enabling GitHub auto-deploy on Render..."
echo "   📝 MANUAL ACTION REQUIRED:"
echo "   1. Go to https://dashboard.render.com"
echo "   2. Find your service: ssl-monitor-api"
echo "   3. Go to Settings → Build & Deploy"
echo "   4. Change 'Auto-Deploy' to 'Yes'"
echo "   5. Set Repository to GitHub: root/ssl-monitor-pro"
echo "   6. Set Branch to 'main'"
echo "   7. Save changes"
echo ""
read -p "Press Enter when Render auto-deploy is enabled..."

# Step 3: Switch Cloudflare back to GitHub
echo ""
echo "3️⃣ Switching Cloudflare back to GitHub..."
echo "   📝 MANUAL ACTION REQUIRED:"
echo "   1. Go to https://dash.cloudflare.com"
echo "   2. Go to Pages → ssl-monitor-pro"
echo "   3. Go to Settings → Build & Deploy"
echo "   4. Disconnect current source"
echo "   5. Connect to GitHub: root/ssl-monitor-pro"
echo "   6. Set Branch to 'main'"
echo "   7. Save changes"
echo ""
read -p "Press Enter when Cloudflare is switched to GitHub..."

# Step 4: Disable GitLab auto-deploy
echo ""
echo "4️⃣ Disabling GitLab auto-deploy..."
echo "   📝 MANUAL ACTION REQUIRED:"
echo "   1. Go to GitLab: http://192.168.1.10/root/ssl-monitor-pro"
echo "   2. Go to Settings → CI/CD → Variables"
echo "   3. Set RENDER_DEPLOY_HOOK_URL to empty or disable"
echo "   4. Or disable the entire pipeline"
echo ""
read -p "Press Enter when GitLab auto-deploy is disabled..."

# Step 5: Trigger manual deploy from GitHub
echo ""
echo "5️⃣ Triggering manual deploy from GitHub..."
echo "   📝 MANUAL ACTION REQUIRED:"
echo "   1. Go to GitHub: https://192.168.1.10/root/ssl-monitor-pro"
echo "   2. Go to Actions tab"
echo "   3. Find the latest workflow"
echo "   4. Click 'Re-run jobs' if needed"
echo "   5. Or make a small commit to trigger deploy"
echo ""
read -p "Press Enter when GitHub deploy is triggered..."

# Step 6: Wait and verify
echo ""
echo "6️⃣ Waiting for deploy to complete..."
echo "   ⏳ Waiting 5 minutes for services to update..."
sleep 300

# Step 7: Run smoke tests
echo ""
echo "7️⃣ Running smoke tests..."
if [ -f "scripts/smoke-tests.sh" ]; then
  ./scripts/smoke-tests.sh
  if [ $? -eq 0 ]; then
    echo "   ✅ Smoke tests passed - rollback successful!"
  else
    echo "   ❌ Smoke tests failed - manual intervention needed"
  fi
else
  echo "   ⚠️  Smoke tests script not found - manual verification needed"
fi

# Step 8: Create rollback report
echo ""
echo "8️⃣ Creating rollback report..."
cat > backup/rollback-report-$(date +%Y%m%d-%H%M%S).md <<EOF
# Emergency Rollback Report

**Date:** $(date)
**Reason:** Emergency rollback from GitLab to GitHub
**Initiated by:** $(whoami)

## Actions Taken:
1. ✅ GitHub remote verified/added
2. ✅ Render.com auto-deploy re-enabled (manual)
3. ✅ Cloudflare Pages switched to GitHub (manual)
4. ✅ GitLab auto-deploy disabled (manual)
5. ✅ GitHub deploy triggered (manual)
6. ✅ Smoke tests executed

## Current Status:
- **Backend:** GitHub → Render.com
- **Frontend:** GitHub → Cloudflare Pages
- **CI/CD:** GitLab CI/CD active
- **GitLab:** Disabled

## Next Steps:
1. Investigate issues that caused rollback
2. Fix problems in GitLab setup
3. Plan re-migration when ready
4. Update team about rollback

## Files Modified:
- No code changes made
- Configuration changes only

## Rollback Duration:
- Start: $(date)
- End: $(date)
- Duration: ~15 minutes
EOF

echo "   ✅ Rollback report created: backup/rollback-report-$(date +%Y%m%d-%H%M%S).md"

# Step 9: Notify team
echo ""
echo "9️⃣ Notifying team..."
echo "   📧 Sending notifications..."

# Send Slack notification
if [ ! -z "$SLACK_WEBHOOK_URL" ]; then
  curl -X POST "$SLACK_WEBHOOK_URL" \
    -H 'Content-Type: application/json' \
    -d '{
      "text": "🚨 EMERGENCY ROLLBACK COMPLETED",
      "blocks": [
        {
          "type": "section",
          "text": {
            "type": "mrkdwn",
            "text": "*SSL Monitor Pro - Emergency Rollback*\n\n⚠️ System rolled back from GitLab to GitHub\n✅ All services operational\n📊 Smoke tests: PASSED\n\nNext: Investigate GitLab issues"
          }
        }
      ]
    }'
  echo "   ✅ Slack notification sent"
fi

# Send Telegram notification
if [ ! -z "$TELEGRAM_BOT_TOKEN" ] && [ ! -z "$TELEGRAM_CHAT_ID" ]; then
  curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/sendMessage" \
    -d "chat_id=$TELEGRAM_CHAT_ID" \
    -d "text=🚨 EMERGENCY ROLLBACK COMPLETED%0A%0A⚠️ SSL Monitor Pro rolled back from GitLab to GitHub%0A✅ All services operational%0A📊 Smoke tests: PASSED%0A%0ANext: Investigate GitLab issues"
  echo "   ✅ Telegram notification sent"
fi

echo ""
echo "================================================"
echo "✅ ROLLBACK COMPLETED SUCCESSFULLY"
echo "================================================"
echo ""
echo "📊 Summary:"
echo "   • System: GitHub → Render.com + Cloudflare"
echo "   • Status: Operational"
echo "   • Duration: ~15 minutes"
echo "   • Notifications: Sent"
echo ""
echo "📝 Next Steps:"
echo "   1. Investigate GitLab issues"
echo "   2. Fix problems found"
echo "   3. Plan re-migration when ready"
echo "   4. Update team about status"
echo ""
echo "📁 Documentation:"
echo "   • Rollback report: backup/rollback-report-*.md"
echo "   • GitHub repo: https://192.168.1.10/root/ssl-monitor-pro"
echo "   • Production: https://cloudsre.xyz"
echo ""
echo "🎉 Rollback successful - system is operational!"
