#!/bin/bash
# === SSL MONITOR PRO - PRODUCTION DEPLOYMENT ===
# Финальный production deployment скрипт
# Дата: 12 октября 2025
# Проект: /home/vmaidaniuk/Cursor/ssl-monitor-final/

set -e  # Exit on error

echo "🚀 SSL Monitor Pro - Production Deployment"
echo "============================================"
echo ""

PROJECT_DIR="/home/vmaidaniuk/Cursor/ssl-monitor-final"
cd "$PROJECT_DIR"

# ============================================================
# 📋 ЭТАП 1: ENVIRONMENT SETUP
# ============================================================

echo "📋 ЭТАП 1: Environment Setup"
echo "----------------------------"

# Создать production .env файл
cat > backend/.env.production <<'ENV'
# === PRODUCTION ENVIRONMENT ===
DEBUG=False
API_ENV=production
PYTHON_VERSION=3.11.10

# === DATABASE (Render PostgreSQL) ===
# Будет автоматически подставлено из Render
DATABASE_URL=${DATABASE_URL}

# === REDIS (Render Redis) ===
# Будет автоматически подставлено из Render
REDIS_URL=${REDIS_URL}

# === STRIPE (TEST KEYS - заменить на LIVE после тестирования) ===
STRIPE_PUBLISHABLE_KEY=pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
STRIPE_SECRET_KEY=sk_test_51SGoJM20i6fmlbYddqN7SFX5II50PU8FNXk3TddOnH6QipGMvXwsmUxvoOKFITR42B924oxrc12Mx5t9pAQMX6Q700Zv95jBJt
STRIPE_WEBHOOK_SECRET=whsec_XXXXXXXXXXXXXXXXXX

# === TELEGRAM BOT ===
TELEGRAM_BOT_TOKEN=8343479392:AAH-XrM21TvjTt7YxG0IEYntP2RzTsxNPko
TELEGRAM_CHAT_ID=YOUR_CHAT_ID_HERE

# === URLS ===
BACKEND_URL=https://status.cloudsre.xyz
FRONTEND_URL=https://cloudsre.xyz

# === SECURITY ===
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE
JWT_SECRET_KEY=YOUR_JWT_SECRET_HERE

# === CORS ===
CORS_ORIGINS=https://cloudsre.xyz,https://www.cloudsre.xyz
ENV

echo "✅ Created .env.production"

# ============================================================
# 📱 ЭТАП 2: TELEGRAM BOT SETUP
# ============================================================

echo ""
echo "📱 ЭТАП 2: Telegram Bot Setup"
echo "-----------------------------"

# Создать скрипт для получения CHAT_ID
cat > get_telegram_chat_id.py <<'PYTHON'
#!/usr/bin/env python3
import requests
import json

BOT_TOKEN = "8343479392:AAH-XrM21TvjTt7YxG0IEYntP2RzTsxNPko"

print("🤖 Telegram Bot Setup")
print("=" * 50)
print("")
print("Отправьте любое сообщение боту, затем запустите этот скрипт")
print("")

url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
response = requests.get(url)
data = response.json()

if data['ok'] and len(data['result']) > 0:
    for update in data['result']:
        if 'message' in update:
            chat_id = update['message']['chat']['id']
            username = update['message']['from'].get('username', 'N/A')
            first_name = update['message']['from'].get('first_name', 'N/A')
            
            print(f"✅ Found Chat:")
            print(f"   Chat ID: {chat_id}")
            print(f"   Username: @{username}")
            print(f"   Name: {first_name}")
            print("")
            print(f"📝 Добавьте в .env:")
            print(f"   TELEGRAM_CHAT_ID={chat_id}")
            print("")
else:
    print("❌ Нет сообщений. Отправьте сообщение боту сначала!")
    print(f"   Бот: @YourBotName")
PYTHON

chmod +x get_telegram_chat_id.py

# Создать скрипт для тестирования бота
cat > test_telegram.py <<'PYTHON'
#!/usr/bin/env python3
import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv('backend/.env.production')

BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

if not BOT_TOKEN or not CHAT_ID:
    print("❌ TELEGRAM_BOT_TOKEN или TELEGRAM_CHAT_ID не настроены")
    sys.exit(1)

def send_message(text):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=data)
    return response.json()

# Test message
message = """
✅ <b>SSL Monitor Pro - Production Test</b>

🚀 Backend: Online
🎨 Frontend: Online
💳 Stripe: Configured
📊 Monitoring: Active

🔗 <a href="https://cloudsre.xyz">cloudsre.xyz</a>
📧 devops@upcz.cz
"""

result = send_message(message)

if result.get('ok'):
    print("✅ Telegram test message sent successfully!")
else:
    print(f"❌ Failed to send message: {result}")
PYTHON

chmod +x test_telegram.py

echo "✅ Created Telegram scripts"
echo ""
echo "📝 Next steps для Telegram:"
echo "   1. Отправьте сообщение боту"
echo "   2. Запустите: python3 get_telegram_chat_id.py"
echo "   3. Скопируйте CHAT_ID в .env.production"
echo "   4. Запустите: python3 test_telegram.py"

# ============================================================
# 🎨 ЭТАП 3: FRONTEND BUILD
# ============================================================

echo ""
echo "🎨 ЭТАП 3: Frontend Build"
echo "-------------------------"

cd frontend-modern

# Создать .env для frontend
cat > .env.production <<'ENV'
VITE_API_URL=https://status.cloudsre.xyz
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
VITE_APP_NAME=SSL Monitor Pro
VITE_APP_URL=https://cloudsre.xyz
ENV

echo "✅ Frontend environment configured"

# Note: Cloudflare Pages деплоится из Git, не требует build локально

cd "$PROJECT_DIR"

# ============================================================
# 💳 ЭТАП 4: STRIPE SETUP GUIDE
# ============================================================

echo ""
echo "💳 ЭТАП 4: Stripe Setup"
echo "-----------------------"

cat > STRIPE_SETUP.md <<'MARKDOWN'
# 💳 Stripe Production Setup

## 1. Создать Products в Stripe Dashboard

Перейти: https://dashboard.stripe.com/products

### Product 1: Starter Plan
- Name: SSL Monitor - Starter
- Price: €19.00 EUR / month
- Trial: 14 days
- Features metadata:
  - max_domains: 10
  - email_alerts: true

### Product 2: Professional Plan
- Name: SSL Monitor - Professional
- Price: €49.00 EUR / month
- Trial: 14 days
- Features metadata:
  - max_domains: 50
  - multi_channel_alerts: true
  - priority_support: true

### Product 3: Enterprise Plan
- Name: SSL Monitor - Enterprise
- Price: €149.00 EUR / month
- Trial: 14 days
- Features metadata:
  - max_domains: -1 (unlimited)
  - custom_integration: true
  - sla: true

## 2. Настроить Webhook

### Webhook URL
```
https://status.cloudsre.xyz/billing/webhook
```

### Events to subscribe
- ✅ checkout.session.completed
- ✅ customer.subscription.created
- ✅ customer.subscription.updated
- ✅ customer.subscription.deleted
- ✅ invoice.payment_succeeded
- ✅ invoice.payment_failed

### После создания
1. Скопировать Webhook Signing Secret
2. Добавить в Render Environment:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```

## 3. Test Mode → Live Mode

После тестирования:
1. Переключить Stripe на Live mode
2. Создать те же products в Live mode
3. Обновить keys в Render:
   - STRIPE_PUBLISHABLE_KEY=pk_live_xxx
   - STRIPE_SECRET_KEY=sk_live_xxx
4. Обновить Webhook URL на Live endpoint

## 4. Тестирование

```bash
# Test checkout (используйте test card: 4242 4242 4242 4242)
curl -X POST https://status.cloudsre.xyz/billing/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "plan": "starter",
    "trial_days": 14
  }'
```
MARKDOWN

echo "✅ Created STRIPE_SETUP.md guide"

# ============================================================
# 🚀 ЭТАП 5: GIT & DEPLOYMENT
# ============================================================

echo ""
echo "🚀 ЭТАП 5: Git & Deployment"
echo "---------------------------"

# Создать .gitignore если нет
if [ ! -f .gitignore ]; then
cat > .gitignore <<'IGNORE'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
.venv

# Environment
.env
.env.local
.env.production
*.env

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Database
*.db
*.sqlite
*.sqlite3
celerybeat-schedule

# Node
node_modules/
npm-debug.log
yarn-error.log

# Build
dist/
build/
*.egg-info/
IGNORE
fi

echo "✅ .gitignore updated"

# ============================================================
# 📊 ЭТАП 6: RENDER DEPLOYMENT CHECKLIST
# ============================================================

echo ""
echo "📊 ЭТАП 6: Render Deployment Checklist"
echo "--------------------------------------"

cat > RENDER_DEPLOYMENT.md <<'MARKDOWN'
# 🚀 Render.com Production Deployment

## Текущий статус
- ✅ Backend deployed на Render
- ✅ PostgreSQL running
- ✅ Redis running
- ⏳ Environment variables нужно обновить

## Environment Variables на Render

Перейти: https://dashboard.render.com → ssl-monitor-api → Environment

### Добавить/Обновить:

```bash
# Stripe
STRIPE_PUBLISHABLE_KEY=pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
STRIPE_SECRET_KEY=sk_test_51SGoJM20i6fmlbYddqN7SFX5II50PU8FNXk3TddOnH6QipGMvXwsmUxvoOKFITR42B924oxrc12Mx5t9pAQMX6Q700Zv95jBJt
STRIPE_WEBHOOK_SECRET=whsec_xxxxx (получить из Stripe после настройки webhook)

# Telegram
TELEGRAM_BOT_TOKEN=8343479392:AAH-XrM21TvjTt7YxG0IEYntP2RzTsxNPko
TELEGRAM_CHAT_ID=xxxxx (получить из get_telegram_chat_id.py)

# URLs
FRONTEND_URL=https://cloudsre.xyz
BACKEND_URL=https://status.cloudsre.xyz

# Security
SECRET_KEY=(generate: python -c "import secrets; print(secrets.token_hex(32))")

# CORS
CORS_ORIGINS=https://cloudsre.xyz,https://www.cloudsre.xyz
```

## Deployment Commands

```bash
# 1. Commit changes
git add .
git commit -m "production: add stripe + telegram + environment config"

# 2. Push to main (Render auto-deploys)
git push origin main

# 3. Check logs
# Render Dashboard → Logs → Watch deployment
```

## Verify Deployment

```bash
# Health check
curl https://status.cloudsre.xyz/health

# Statistics
curl https://status.cloudsre.xyz/statistics

# Billing plans
curl https://status.cloudsre.xyz/billing/plans
```
MARKDOWN

echo "✅ Created RENDER_DEPLOYMENT.md"

# ============================================================
# 🌐 ЭТАП 7: CLOUDFLARE PAGES DEPLOYMENT
# ============================================================

echo ""
echo "🌐 ЭТАП 7: Cloudflare Pages Deployment"
echo "--------------------------------------"

cat > CLOUDFLARE_PAGES_SETUP.md <<'MARKDOWN'
# ☁️ Cloudflare Pages Deployment

## 1. Создать проект в Cloudflare Pages

Перейти: https://dash.cloudflare.com → Pages → Create a project

### Connect to Git
1. Connect GitHub account
2. Select repository: `ssl-monitor-final`
3. Click "Begin setup"

### Build settings
```
Build command:        (leave empty - static HTML)
Build output directory: /frontend-modern
Root directory:       frontend-modern
```

### Environment variables
```
VITE_API_URL=https://status.cloudsre.xyz
```

### Deploy!
Click "Save and Deploy"

## 2. Configure Custom Domain

### Add domain
1. Pages → Project → Custom domains
2. Add domain: `cloudsre.xyz`
3. Add domain: `www.cloudsre.xyz`

### DNS Records (автоматически создадутся)
```
Type    Name    Target                              Proxy
CNAME   @       ssl-monitor-final.pages.dev         Yes
CNAME   www     ssl-monitor-final.pages.dev         Yes
```

### Add CNAME for backend (вручную)
```
Type    Name    Target                              Proxy
CNAME   status  ssl-monitor-api.onrender.com        Yes
```

## 3. Verify Deployment

```bash
# Frontend
curl -I https://cloudsre.xyz

# Backend
curl -I https://status.cloudsre.xyz

# API
curl https://status.cloudsre.xyz/health
```

## 4. SSL Certificate

Cloudflare автоматически создаст Universal SSL certificate
- Ожидание: 5-10 минут
- Проверка: https://cloudsre.xyz должен работать с HTTPS

## 5. Page Rules (опционально)

Для лучшей производительности:
1. Cloudflare Dashboard → Page Rules
2. Add rule: `cloudsre.xyz/*`
   - Cache Level: Standard
   - Browser Cache TTL: 4 hours
   - Edge Cache TTL: 2 hours
MARKDOWN

echo "✅ Created CLOUDFLARE_PAGES_SETUP.md"

# ============================================================
# ✅ ЭТАП 8: VERIFICATION SCRIPTS
# ============================================================

echo ""
echo "✅ ЭТАП 8: Verification Scripts"
echo "-------------------------------"

# Health check script
cat > verify_production.sh <<'BASH'
#!/bin/bash
echo "🔍 SSL Monitor Pro - Production Verification"
echo "============================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check frontend
echo -n "🎨 Frontend (cloudsre.xyz): "
if curl -s -o /dev/null -w "%{http_code}" https://cloudsre.xyz | grep -q "200"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Check backend health
echo -n "🔧 Backend health: "
HEALTH=$(curl -s https://status.cloudsre.xyz/health)
if echo "$HEALTH" | grep -q "healthy"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Check API docs
echo -n "📚 API docs: "
if curl -s -o /dev/null -w "%{http_code}" https://status.cloudsre.xyz/docs | grep -q "200"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Check statistics
echo -n "📊 Statistics endpoint: "
if curl -s https://status.cloudsre.xyz/statistics | grep -q "total_domains"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

# Check billing plans
echo -n "💳 Billing plans: "
if curl -s https://status.cloudsre.xyz/billing/plans | grep -q "plans"; then
    echo -e "${GREEN}✅ OK${NC}"
else
    echo -e "${RED}❌ FAILED${NC}"
fi

echo ""
echo "🎯 Verification Complete!"
BASH

chmod +x verify_production.sh

echo "✅ Created verify_production.sh"

# ============================================================
# 📋 ЭТАП 9: FINAL CHECKLIST
# ============================================================

echo ""
echo "📋 ЭТАП 9: Final Production Checklist"
echo "-------------------------------------"

cat > PRODUCTION_CHECKLIST.md <<'MARKDOWN'
# ✅ SSL Monitor Pro - Production Checklist

## 🔴 КРИТИЧНО (перед запуском)

### Backend (Render.com)
- [ ] Environment variables добавлены
  - [ ] STRIPE_SECRET_KEY
  - [ ] STRIPE_PUBLISHABLE_KEY
  - [ ] TELEGRAM_BOT_TOKEN
  - [ ] TELEGRAM_CHAT_ID
  - [ ] SECRET_KEY (generated)
- [ ] Latest code pushed to GitHub
- [ ] Deployment successful
- [ ] Health check returns OK
- [ ] Database migrations applied

### Frontend (Cloudflare Pages)
- [ ] Project created и connected to GitHub
- [ ] Build settings configured
- [ ] Environment variables set
- [ ] Deployment successful
- [ ] Custom domain connected (cloudsre.xyz)

### DNS (Cloudflare)
- [ ] CNAME @ → pages.dev (Proxied)
- [ ] CNAME www → pages.dev (Proxied)
- [ ] CNAME status → render.com (Proxied)
- [ ] SSL certificate active

### Stripe
- [ ] Products created (Starter, Pro, Enterprise)
- [ ] Prices configured
- [ ] Webhook endpoint created
- [ ] Webhook secret added to Render
- [ ] Test checkout works

### Telegram
- [ ] Bot token validated
- [ ] Chat ID obtained
- [ ] Test message sent successfully
- [ ] Notifications working

## 🟡 ВАЖНО (первая неделя)

### Testing
- [ ] Full user flow tested
- [ ] SSL check working
- [ ] Domain add/delete working
- [ ] Statistics accurate
- [ ] Stripe payment flow tested
- [ ] Telegram alerts tested

### Monitoring
- [ ] UptimeRobot configured
- [ ] Error tracking (Sentry) set up
- [ ] Health checks scheduled
- [ ] Alert email/Telegram configured

### Documentation
- [ ] API docs accessible
- [ ] User guides ready
- [ ] FAQ prepared
- [ ] Support email configured

## 🟢 ЖЕЛАТЕЛЬНО (этот месяц)

### Marketing
- [ ] SEO optimization
- [ ] Social media presence
- [ ] Product Hunt launch prepared
- [ ] Landing page optimized

### Features
- [ ] Email alerts configured
- [ ] Custom check intervals
- [ ] Export reports (CSV/PDF)
- [ ] API rate limiting

### Business
- [ ] Terms of Service
- [ ] Privacy Policy
- [ ] GDPR compliance
- [ ] Customer support system

## 🚀 LAUNCH SEQUENCE

### Day 0 (Сегодня)
1. ✅ Deploy backend
2. ✅ Deploy frontend
3. ✅ Configure DNS
4. ✅ Test everything
5. ✅ Switch Stripe to test mode
6. ✅ Soft launch

### Day 1-7 (Первая неделя)
1. Monitor errors
2. Fix issues
3. Collect feedback
4. Improve UX

### Day 8-30 (Первый месяц)
1. Switch Stripe to LIVE
2. Start marketing
3. First paying customer
4. Scale infrastructure

## 📊 SUCCESS METRICS

### Week 1
- [ ] 0 critical errors
- [ ] 10+ test users
- [ ] 100+ SSL checks performed

### Month 1
- [ ] First paying customer
- [ ] €100 MRR
- [ ] 50+ registered domains

### Month 3
- [ ] €1,000 MRR
- [ ] 10+ paying customers
- [ ] 500+ monitored domains

---

**Last updated:** $(date)
**Status:** Ready for Production 🚀
MARKDOWN

echo "✅ Created PRODUCTION_CHECKLIST.md"

# ============================================================
# 🎯 ЗАВЕРШЕНИЕ
# ============================================================

echo ""
echo "============================================"
echo "✅ Production Deployment Setup Complete!"
echo "============================================"
echo ""
echo "📁 Created Files:"
echo "   - backend/.env.production"
echo "   - get_telegram_chat_id.py"
echo "   - test_telegram.py"
echo "   - STRIPE_SETUP.md"
echo "   - RENDER_DEPLOYMENT.md"
echo "   - CLOUDFLARE_PAGES_SETUP.md"
echo "   - verify_production.sh"
echo "   - PRODUCTION_CHECKLIST.md"
echo ""
echo "🚀 Next Steps:"
echo ""
echo "1. 📱 Telegram Setup:"
echo "   python3 get_telegram_chat_id.py"
echo "   (Update TELEGRAM_CHAT_ID in .env.production)"
echo "   python3 test_telegram.py"
echo ""
echo "2. 💳 Stripe Setup:"
echo "   cat STRIPE_SETUP.md"
echo "   (Create products in Stripe Dashboard)"
echo ""
echo "3. 🚀 Deploy Backend:"
echo "   cat RENDER_DEPLOYMENT.md"
echo "   (Add env vars and push to GitHub)"
echo ""
echo "4. 🌐 Deploy Frontend:"
echo "   cat CLOUDFLARE_PAGES_SETUP.md"
echo "   (Create Pages project)"
echo ""
echo "5. ✅ Verify:"
echo "   ./verify_production.sh"
echo ""
echo "6. 📋 Checklist:"
echo "   cat PRODUCTION_CHECKLIST.md"
echo ""
echo "🎯 Ready to launch SSL Monitor Pro!"
echo ""

