# 🚀 Render.com Deploy Instructions

## Step-by-Step Deployment Guide

### 1. Create Render Account
1. Go to https://render.com
2. Sign up with GitHub account
3. Verify your email address

### 2. Create PostgreSQL Database
1. In Render dashboard, click "New +" → "PostgreSQL"
2. Configure:
   - **Name**: `ssl-monitor-db`
   - **Database**: `sslmonitor`
   - **User**: `ssluser`
   - **Region**: Frankfurt (EU)
   - **Plan**: Free
3. Click "Create Database"
4. **Save the connection string** - you'll need it!

### 3. Create Redis Instance
1. Click "New +" → "Redis"
2. Configure:
   - **Name**: `ssl-monitor-redis`
   - **Region**: Frankfurt
   - **Plan**: Free
3. Click "Create Redis"
4. **Save the connection string** (redis://red-xxxxx:6379)

### 4. Create Web Service (Backend)
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure:

**Basic Settings:**
- **Name**: `ssl-monitor-backend`
- **Environment**: Python
- **Region**: Frankfurt (EU)
- **Branch**: main
- **Root Directory**: ./

**Build Settings:**
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

**Plan:**
- **Instance Type**: Free

4. Set Environment Variables:
```
DATABASE_URL = [paste from PostgreSQL dashboard]
REDIS_URL = [paste from Redis dashboard]
STRIPE_SECRET_KEY = YOUR_STRIPE_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY = pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
TELEGRAM_BOT_TOKEN = [optional - your bot token]
TELEGRAM_CHAT_ID = [optional - your chat ID]
```

5. Click "Create Web Service"

### 5. Create Worker (Celery)
1. Click "New +" → "Background Worker"
2. Select same repository
3. Configure:

**Basic Settings:**
- **Name**: `ssl-monitor-worker`
- **Environment**: Python
- **Region**: Frankfurt

**Build Settings:**
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && celery -A celery_worker worker --loglevel=info`

4. Set same environment variables as backend
5. Click "Create Background Worker"

### 6. Create Scheduler (Celery Beat)
1. Click "New +" → "Background Worker"
2. Select same repository
3. Configure:

**Basic Settings:**
- **Name**: `ssl-monitor-beat`
- **Build Command**: `pip install -r backend/requirements.txt`
- **Start Command**: `cd backend && celery -A celery_worker beat --loglevel=info`

4. Set environment variables (DATABASE_URL, REDIS_URL)
5. Click "Create Background Worker"

### 7. Deploy & Test

**Wait for deployment** (5-10 minutes):
- Backend will be available at: `https://ssl-monitor-backend.onrender.com`
- Watch logs in Render dashboard

**Test your deployment:**
```bash
# Health check
curl https://ssl-monitor-backend.onrender.com/health

# Get pricing plans
curl https://ssl-monitor-backend.onrender.com/billing/plans

# API docs
open https://ssl-monitor-backend.onrender.com/docs
```

### 8. Setup Custom Domain (Optional)

If you have a domain:
1. Go to your web service settings
2. Click "Custom Domains"
3. Add your domain: `api.sslmonitor.pro`
4. Update DNS records as instructed
5. Wait for SSL certificate (automatic)

### 9. Configure Stripe Webhooks

1. Go to Stripe Dashboard: https://dashboard.stripe.com/webhooks
2. Click "Add endpoint"
3. Enter URL: `https://ssl-monitor-backend.onrender.com/billing/webhook`
4. Select events:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`
5. Copy webhook signing secret
6. Add to Render environment variables:
   ```
   STRIPE_WEBHOOK_SECRET = whsec_xxxxx
   ```

### 10. Post-Deploy Checklist

- [ ] Backend health check passes
- [ ] Can see pricing plans via API
- [ ] Database tables created
- [ ] Can add test domain
- [ ] Stripe test payment works (card: 4242424242424242)
- [ ] Telegram notifications work (if configured)
- [ ] API documentation accessible

### 11. Go Live!

**Switch to Production Stripe Keys:**
1. Get LIVE keys from Stripe dashboard
2. Update in Render:
   ```
   STRIPE_SECRET_KEY = sk_live_xxxxx
   STRIPE_PUBLISHABLE_KEY = pk_live_xxxxx
   ```
3. Redeploy

**Start Marketing:**
- Share on LinkedIn
- Post on Reddit (r/SideProject, r/devops)
- Email your network
- Launch promo: LAUNCH50 (50% off)

## 🎯 Your URLs

- **API**: https://ssl-monitor-backend.onrender.com
- **Docs**: https://ssl-monitor-backend.onrender.com/docs
- **Health**: https://ssl-monitor-backend.onrender.com/health
- **Pricing**: https://ssl-monitor-backend.onrender.com/billing/plans

## 💰 Cost Breakdown

- PostgreSQL: **€0/month** (Free tier: 1GB storage, 97 hours/month)
- Redis: **€0/month** (Free tier: 25MB, 30 connections)
- Backend: **€0/month** (Free tier: 750 hours/month)
- Worker: **€0/month** (Free tier)
- Beat: **€0/month** (Free tier)

**Total: €0/month** 🎉

## ⏰ Timeline

- Database setup: 2 minutes
- Backend deploy: 5-8 minutes
- Workers deploy: 3-5 minutes each
- DNS propagation (if custom domain): up to 48 hours
- **Total: 15-20 minutes to live production!**

## 🆘 Troubleshooting

**Build fails:**
- Check that requirements.txt has all dependencies
- Verify Python version is 3.11
- Check build logs in Render dashboard

**Database connection errors:**
- Verify DATABASE_URL is set correctly
- Check that database is running
- Ensure database user has correct permissions

**Celery not processing tasks:**
- Check REDIS_URL is set
- Verify worker is running (check logs)
- Ensure beat scheduler is running

**Stripe webhooks failing:**
- Verify webhook URL is accessible
- Check STRIPE_WEBHOOK_SECRET is set
- Look for errors in Stripe dashboard

## 📞 Support

- Render Docs: https://render.com/docs
- Stripe Docs: https://stripe.com/docs
- Project Issues: GitHub Issues

---

**You're ready to launch! 🚀**

Next: Get your first paying customer within 7 days!

