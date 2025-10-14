#!/bin/bash

# SSL Monitor Pro - GitLab CI/CD Variables Setup
# Usage: ./scripts/setup-gitlab-vars.sh

GITLAB_URL="http://192.168.1.10"
GITLAB_TOKEN="glpat-6xB--zr0yzQzyeuFcxaMYG86MQp1OjEH.01.0w0bnoard"
PROJECT_ID="root/ssl-monitor-pro"

echo "🔐 Setting up GitLab CI/CD Variables..."

# Function to add variable
add_variable() {
  local key=$1
  local value=$2
  local protected=${3:-false}
  local masked=${4:-true}
  
  echo "Adding variable: $key"
  
  response=$(curl -s --request POST \
    --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
    --form "key=$key" \
    --form "value=$value" \
    --form "protected=$protected" \
    --form "masked=$masked" \
    "$GITLAB_URL/api/v4/projects/$(echo $PROJECT_ID | sed 's/\//%2F/g')/variables")
  
  # Check if variable already exists
  if echo "$response" | grep -q "already exists"; then
    echo "  ⚠️  Variable $key already exists - updating..."
    curl -s --request PUT \
      --header "PRIVATE-TOKEN: $GITLAB_TOKEN" \
      --form "value=$value" \
      --form "protected=$protected" \
      --form "masked=$masked" \
      "$GITLAB_URL/api/v4/projects/$(echo $PROJECT_ID | sed 's/\//%2F/g')/variables/$key"
  else
    echo "  ✅ Variable $key added successfully"
  fi
}

# Check if .migration-secrets exists
if [ ! -f ".migration-secrets" ]; then
  echo "❌ Error: .migration-secrets file not found!"
  echo "Please create it first with all your credentials."
  echo "See the migration guide for details."
  exit 1
fi

# Source secrets file
echo "📖 Loading secrets from .migration-secrets..."
source .migration-secrets

# === RENDER.COM ===
echo ""
echo "📦 Adding Render.com variables..."
add_variable "RENDER_API_KEY" "$RENDER_API_KEY" false true
add_variable "RENDER_DEPLOY_HOOK_URL" "$RENDER_DEPLOY_HOOK_URL" false true

# === CLOUDFLARE ===
echo ""
echo "☁️ Adding Cloudflare variables..."
add_variable "CLOUDFLARE_API_TOKEN" "$CLOUDFLARE_API_TOKEN" false true
add_variable "CLOUDFLARE_ACCOUNT_ID" "$CLOUDFLARE_ACCOUNT_ID" false false
add_variable "CLOUDFLARE_ZONE_ID" "$CLOUDFLARE_ZONE_ID" false false

# === STRIPE ===
echo ""
echo "💳 Adding Stripe variables..."
add_variable "STRIPE_SECRET_KEY" "$STRIPE_SECRET_KEY" false true
add_variable "STRIPE_PUBLISHABLE_KEY" "$STRIPE_PUBLISHABLE_KEY" false false
add_variable "STRIPE_WEBHOOK_SECRET" "$STRIPE_WEBHOOK_SECRET" false true

# === DATABASE ===
echo ""
echo "🗄️ Adding Database variables..."
add_variable "DATABASE_URL" "$DATABASE_URL" false true
add_variable "POSTGRES_HOST" "$POSTGRES_HOST" false false
add_variable "POSTGRES_USER" "$POSTGRES_USER" false false
add_variable "POSTGRES_PASSWORD" "$POSTGRES_PASSWORD" false true
add_variable "POSTGRES_DB" "$POSTGRES_DB" false false

# === REDIS ===
echo ""
echo "🔴 Adding Redis variables..."
add_variable "REDIS_URL" "$REDIS_URL" false true
add_variable "UPSTASH_REDIS_URL" "$UPSTASH_REDIS_URL" false true

# === EMAIL ===
echo ""
echo "📧 Adding Email variables..."
add_variable "BREVO_API_KEY" "$BREVO_API_KEY" false true
add_variable "BREVO_FROM_EMAIL" "$BREVO_FROM_EMAIL" false false
add_variable "BREVO_FROM_NAME" "$BREVO_FROM_NAME" false false

# === TELEGRAM ===
echo ""
echo "📱 Adding Telegram variables..."
add_variable "TELEGRAM_BOT_TOKEN" "$TELEGRAM_BOT_TOKEN" false true
add_variable "TELEGRAM_CHAT_ID" "$TELEGRAM_CHAT_ID" false false

# === SLACK ===
echo ""
echo "💬 Adding Slack variables..."
add_variable "SLACK_WEBHOOK_URL" "$SLACK_WEBHOOK_URL" false true
add_variable "SLACK_BOT_TOKEN" "$SLACK_BOT_TOKEN" false true

# === MONITORING ===
echo ""
echo "📊 Adding Monitoring variables..."
add_variable "SENTRY_DSN" "$SENTRY_DSN" false false

# === APPLICATION ===
echo ""
echo "⚙️ Adding Application variables..."
add_variable "SECRET_KEY" "$SECRET_KEY" false true
add_variable "JWT_SECRET_KEY" "$JWT_SECRET_KEY" false true
add_variable "ENVIRONMENT" "production" false false

echo ""
echo "✅ All variables added to GitLab!"
echo ""
echo "🔍 Verify in GitLab UI:"
echo "   $GITLAB_URL/root/ssl-monitor-pro/-/settings/ci_cd"
echo "   → Variables section"
