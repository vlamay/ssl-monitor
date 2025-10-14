#!/bin/bash

# SSL Monitor Pro - Webhook Verification for Migration
# Usage: ./scripts/verify-webhooks.sh

echo "🔗 Verifying Webhooks for GitLab Migration..."
echo "==========================================="

# Load secrets
if [ -f ".migration-secrets" ]; then
    source .migration-secrets
else
    echo "❌ Error: .migration-secrets file not found!"
    exit 1
fi

API_URL="https://ssl-monitor-api.onrender.com"

echo ""
echo "📋 Webhook Verification Checklist:"
echo ""

echo "1️⃣ Stripe Webhooks:"
echo "   • URL: $API_URL/api/v1/stripe/webhook"
echo "   • Status: Checking..."
stripe_status=$(curl -s -o /dev/null -w '%{http_code}' "$API_URL/api/v1/stripe/webhook")
if [ "$stripe_status" = "404" ]; then
    echo "   ⚠️  Status: 404 (endpoint not found - may be normal)"
elif [ "$stripe_status" = "405" ]; then
    echo "   ✅ Status: 405 (Method Not Allowed - correct for GET)"
else
    echo "   ❓ Status: $stripe_status (unexpected)"
fi
echo "   • Expected: 405 Method Not Allowed (for GET requests)"
echo "   • POST requests should work for actual webhooks"
echo ""

echo "2️⃣ Telegram Webhooks:"
echo "   • URL: $API_URL/api/v1/telegram/webhook"
echo "   • Status: Checking..."
telegram_status=$(curl -s -o /dev/null -w '%{http_code}' "$API_URL/api/v1/telegram/webhook")
if [ "$telegram_status" = "404" ]; then
    echo "   ⚠️  Status: 404 (endpoint not found - may be normal)"
elif [ "$telegram_status" = "405" ]; then
    echo "   ✅ Status: 405 (Method Not Allowed - correct for GET)"
else
    echo "   ❓ Status: $telegram_status (unexpected)"
fi
echo "   • Expected: 405 Method Not Allowed (for GET requests)"
echo "   • POST requests should work for actual webhooks"
echo ""

echo "3️⃣ Slack Webhooks:"
echo "   • URL: $API_URL/api/v1/slack/webhook"
echo "   • Status: Checking..."
slack_status=$(curl -s -o /dev/null -w '%{http_code}' "$API_URL/api/v1/slack/webhook")
if [ "$slack_status" = "404" ]; then
    echo "   ⚠️  Status: 404 (endpoint not found - may be normal)"
elif [ "$slack_status" = "405" ]; then
    echo "   ✅ Status: 405 (Method Not Allowed - correct for GET)"
else
    echo "   ❓ Status: $slack_status (unexpected)"
fi
echo "   • Expected: 405 Method Not Allowed (for GET requests)"
echo "   • POST requests should work for actual webhooks"
echo ""

echo "4️⃣ Telegram Bot Configuration:"
echo "   • Bot Token: ${TELEGRAM_BOT_TOKEN:0:20}..."
echo "   • Chat ID: $TELEGRAM_CHAT_ID"
echo "   • Checking webhook info..."
if [ ! -z "$TELEGRAM_BOT_TOKEN" ] && [[ "$TELEGRAM_BOT_TOKEN" != *"demo"* ]]; then
    echo "   ⚠️  Real token detected - checking webhook..."
    webhook_info=$(curl -s "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo")
    if [ $? -eq 0 ]; then
        echo "   ✅ Webhook info retrieved successfully"
        echo "   • Response: $webhook_info"
    else
        echo "   ❌ Failed to get webhook info"
    fi
else
    echo "   ℹ️  Demo token - skipping webhook check"
fi
echo ""

echo "5️⃣ Slack Configuration:"
echo "   • Webhook URL: ${SLACK_WEBHOOK_URL:0:30}..."
echo "   • Bot Token: ${SLACK_BOT_TOKEN:0:20}..."
echo "   • Testing webhook..."
if [ ! -z "$SLACK_WEBHOOK_URL" ] && [[ "$SLACK_WEBHOOK_URL" != *"demo"* ]]; then
    echo "   ⚠️  Real webhook detected - testing..."
    test_message='{
        "text": "🧪 Test: GitLab Migration Webhook Verification",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*SSL Monitor Pro* - Webhook Test\n✅ GitLab migration webhook verification"
                }
            }
        ]
    }'
    
    slack_response=$(curl -s -X POST "$SLACK_WEBHOOK_URL" \
        -H 'Content-Type: application/json' \
        -d "$test_message")
    
    if [ $? -eq 0 ]; then
        echo "   ✅ Test message sent successfully"
    else
        echo "   ❌ Failed to send test message"
    fi
else
    echo "   ℹ️  Demo webhook - skipping test"
fi
echo ""

echo "6️⃣ Stripe Configuration:"
echo "   • Secret Key: ${STRIPE_SECRET_KEY:0:20}..."
echo "   • Webhook Secret: ${STRIPE_WEBHOOK_SECRET:0:20}..."
echo "   • Expected Events: checkout.session.completed, customer.subscription.updated"
echo "   • Manual verification required in Stripe Dashboard"
echo ""

echo "📊 Webhook Verification Summary:"
echo "   • Stripe: $stripe_status"
echo "   • Telegram: $telegram_status"
echo "   • Slack: $slack_status"
echo ""

echo "🔧 Manual Verification Steps:"
echo ""
echo "1️⃣ Stripe Dashboard:"
echo "   • Go to: https://dashboard.stripe.com"
echo "   • Navigate to: Developers → Webhooks"
echo "   • Find SSL Monitor Pro webhook"
echo "   • Verify endpoint URL: $API_URL/api/v1/stripe/webhook"
echo "   • Check signing secret matches GitLab Variables"
echo ""
echo "2️⃣ Telegram Bot:"
echo "   • Send message to bot: /start"
echo "   • Send message to bot: /status"
echo "   • Verify bot responds correctly"
echo "   • Check webhook URL in BotFather"
echo ""
echo "3️⃣ Slack App:"
echo "   • Go to: https://api.slack.com/apps"
echo "   • Find SSL Monitor Pro app"
echo "   • Check Event Subscriptions URL"
echo "   • Verify webhook URL matches"
echo ""

echo "⚠️  Important Notes:"
echo "   • Webhook URLs don't change during migration"
echo "   • Only the source (GitHub → GitLab) changes"
echo "   • Test all webhooks after migration"
echo "   • Monitor webhook delivery logs"
echo ""

echo "✅ Webhook Verification Complete!"
echo ""
echo "📋 Next Steps:"
echo "   1. Complete manual verification in each service"
echo "   2. Test webhook delivery after migration"
echo "   3. Monitor webhook logs"
echo "   4. Proceed to Phase 4 - Testing"
echo ""
echo "🔗 Links:"
echo "   • Stripe Dashboard: https://dashboard.stripe.com"
echo "   • Telegram BotFather: https://t.me/botfather"
echo "   • Slack API: https://api.slack.com/apps"
echo "   • Production API: $API_URL"
