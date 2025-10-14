# 🚀 Render Environment Variables Setup

## Go to Render Dashboard

URL: https://dashboard.render.com → Select `ssl-monitor-api` → Environment

---

## Required Environment Variables

### 🔒 Security Keys
```bash
SECRET_KEY=eaefa6224b2d9e5671c352c2f3f3988c85abad57011c310535e4f3591ccbd2b6
JWT_SECRET_KEY=5c623dd403a425fd371eeb92c85b0ebe2888a10f5f454e7f76848e6b827d5acf
```

### 💳 Stripe (Test Keys)
```bash
STRIPE_PUBLISHABLE_KEY=pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY

STRIPE_SECRET_KEY=sk_test_51SGoJM20i6fmlbYddqN7SFX5II50PU8FNXk3TddOnH6QipGMvXwsmUxvoOKFITR42B924oxrc12Mx5t9pAQMX6Q700Zv95jBJt

STRIPE_WEBHOOK_SECRET=whsec_xxxxxx (get from Stripe Dashboard after webhook setup)
```

### 📱 Telegram Bot
```bash
TELEGRAM_BOT_TOKEN=7409378539:AAHGan44vnafc8FOWgyF0FnE3mmHaYhdhrs
TELEGRAM_CHAT_ID=8159854958
```

### 🌐 URLs
```bash
FRONTEND_URL=https://cloudsre.xyz
BACKEND_URL=https://status.cloudsre.xyz
```

### 📧 Admin & Support
```bash
ADMIN_EMAIL=vla.maidaniuk@gmail.com
ALERT_EMAIL=vla.maidaniuk@gmail.com
SUPPORT_EMAIL=vla.maidaniuk@gmail.com
```

### 🔐 CORS
```bash
CORS_ORIGINS=https://cloudsre.xyz,https://www.cloudsre.xyz
```

---

## Auto-Configured Variables

These are automatically set by Render (don't add manually):
- `DATABASE_URL` - PostgreSQL connection string
- `REDIS_URL` - Redis connection string  
- `PORT` - Server port

---

## How to Add Variables

### Method 1: Web Dashboard (Recommended)
1. Go to: https://dashboard.render.com
2. Select service: `ssl-monitor-api`
3. Go to: **Environment** tab
4. Click: **Add Environment Variable**
5. Add each variable from above
6. Click: **Save Changes**
7. Service will auto-redeploy

### Method 2: render.yaml (Already configured)
Variables are defined in `render.yaml` with `sync: false`  
This means you need to add them manually in dashboard

---

## Verification

After adding variables, check logs:

```bash
# In Render Dashboard → Logs
# Look for:
✅ Telegram bot configured
✅ Stripe API key loaded
✅ Database connected
✅ Redis connected
```

---

## Test After Deployment

```bash
# Health check
curl https://status.cloudsre.xyz/health

# Should return:
{
  "status": "healthy",
  "database": "connected"
}
```

---

## Switch to Live Mode (After Testing)

When ready for production:

1. **Stripe:** Switch keys from `test` to `live`
2. **Telegram:** Already live
3. **Security:** Regenerate SECRET_KEY for production

---

## Support

If variables don't load:
- Check for typos
- Verify no quotes around values
- Check Render logs for errors
- Restart service manually if needed

**Email:** vla.maidaniuk@gmail.com

