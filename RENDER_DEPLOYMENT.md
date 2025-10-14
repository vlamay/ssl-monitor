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
