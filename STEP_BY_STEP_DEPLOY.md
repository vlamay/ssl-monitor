# 🚀 Step-by-Step Deployment Guide

**Platform**: SSL Monitor Pro  
**Target**: Render.com + Cloudflare DNS  
**Domain**: cloudsre.xyz  
**Time**: 45-60 minutes  
**Cost**: €0/month (free tier)  

---

## 📋 Prerequisites Checklist

- [x] Project ready: /home/vmaidaniuk/ssl-monitor
- [x] Git commits: 5 commits ready
- [x] SSH key created
- [ ] SSH key added to GitHub
- [ ] GitHub repository created
- [ ] Code pushed to GitHub
- [ ] Render.com account
- [ ] Cloudflare account with cloudsre.xyz

---

## STEP 0: SSH Key Setup ✅ COMPLETED

SSH key created and added to ssh-agent.

**Your PUBLIC KEY**:
```
ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIBp+HEDu5YulfCDmPabmXvAZ4ChJwW1lW8YitYyqeYvp vla.maidaniuk@gmail.com
```

**Add to GitHub**:
1. Go to: https://github.com/settings/ssh/new
2. Title: `Ubuntu - SSL Monitor`
3. Key type: `Authentication Key`
4. Paste the key above
5. Click "Add SSH key"

---

## STEP 1: Create GitHub Repository (2 min)

### Option A: If repository doesn't exist yet

1. **Open**: https://github.com/new

2. **Fill form**:
   - Repository name: `ssl-monitor`
   - Description: `Enterprise SSL Certificate Monitoring SaaS Platform - €1000 MRR`
   - Visibility: **Public** ✓ (required for Render free tier)
   - Initialize: 
     - [ ] Don't add README
     - [ ] Don't add .gitignore  
     - [ ] Don't add license
   
3. **Click** "Create repository"

### Option B: If repository exists

Skip to Step 2

---

## STEP 2: Push Code to GitHub (2 min)

### Execute these commands:

```bash
cd /home/vmaidaniuk/ssl-monitor

# Remove old remote if exists
git remote remove origin 2>/dev/null

# Add GitHub remote
git remote add origin git@github.com:maydanov-dev/ssl-monitor.git

# Ensure branch is named main
git branch -M main

# Push to GitHub
git push -u origin main
```

### Or use the script:

```bash
cd /home/vmaidaniuk/ssl-monitor
chmod +x GIT_COMMANDS.sh
./GIT_COMMANDS.sh
```

### Expected output:

```
Enumerating objects: 45, done.
Counting objects: 100% (45/45), done.
...
To github.com:maydanov-dev/ssl-monitor.git
 * [new branch]      main -> main
```

### Verify:

Open: **https://github.com/maydanov-dev/ssl-monitor**

You should see:
- ✅ ~38 files
- ✅ Folders: backend/, frontend/, database/
- ✅ Files: render.yaml, docker-compose.yml, README.md
- ✅ Latest commit: "🎯 Add START_DEPLOYMENT quick reference"

---

## STEP 3: Render.com Account Setup (3 min)

1. **Open**: https://render.com

2. **Sign up**:
   - Click "Get Started"
   - Choose "Sign up with GitHub"
   - Authorize Render to access GitHub

3. **Verify email** if prompted

4. **You're in!** You should see Render Dashboard

---

## STEP 4: Create PostgreSQL Database (2 min)

1. **In Render Dashboard**: Click "New +" → "PostgreSQL"

2. **Configure**:
   - **Name**: `ssl-monitor-db`
   - **Database**: `sslmonitor`
   - **User**: `ssluser`
   - **Region**: Frankfurt (Europe)
   - **PostgreSQL Version**: 15
   - **Plan**: Free

3. **Click** "Create Database"

4. **Wait** ~1-2 minutes for database to be ready

5. **IMPORTANT: Copy Internal Database URL**:
   - Go to database "Info" tab
   - Find "Internal Database URL"
   - Copy it (looks like: `postgresql://ssluser:password@dpg-xxxxx:5432/sslmonitor`)
   - **Save this** - you'll need it!

---

## STEP 5: Create Redis (2 min)

1. **Click** "New +" → "Redis"

2. **Configure**:
   - **Name**: `ssl-monitor-redis`
   - **Region**: Frankfurt
   - **Plan**: Free
   - **Max Memory Policy**: allkeys-lru

3. **Click** "Create Redis"

4. **IMPORTANT: Copy Internal Redis URL**:
   - Find "Internal Redis URL"
   - Copy it (looks like: `redis://red-xxxxx:6379`)
   - **Save this** - you'll need it!

---

## STEP 6: Create Backend Web Service (10 min)

1. **Click** "New +" → "Web Service"

2. **Connect Repository**:
   - Select "Build and deploy from a Git repository"
   - Choose `maydanov-dev/ssl-monitor`
   - Click "Connect"

3. **Configure Service**:
   
   **Basic Info**:
   - **Name**: `ssl-monitor-backend`
   - **Region**: Frankfurt
   - **Branch**: main
   - **Root Directory**: ./
   - **Environment**: Python

   **Build Settings**:
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && uvicorn app.main:app --host 0.0.0.0 --port $PORT`

   **Plan**:
   - **Instance Type**: Free

4. **Advanced Settings** → **Health Check Path**:
   - Set to: `/health`

5. **Environment Variables** (Click "Add Environment Variable"):
   
   ```
   DATABASE_URL = [paste Internal Database URL from Step 4]
   REDIS_URL = [paste Internal Redis URL from Step 5]
   STRIPE_SECRET_KEY = YOUR_STRIPE_SECRET_KEY_HERE
   STRIPE_PUBLISHABLE_KEY = pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
   PYTHON_VERSION = 3.11
   ```

   **Optional** (if you configured Telegram):
   ```
   TELEGRAM_BOT_TOKEN = your_bot_token_here
   TELEGRAM_CHAT_ID = your_chat_id_here
   ```

6. **Click** "Create Web Service"

7. **Wait** for deployment (~5-10 minutes)
   - Watch logs in real-time
   - Should see: "Application startup complete"
   - Status should turn to "Live"

8. **Copy your backend URL**:
   - Will be: `https://ssl-monitor-backend.onrender.com`

---

## STEP 7: Create Celery Worker (5 min)

1. **Click** "New +" → "Background Worker"

2. **Connect Repository**: `maydanov-dev/ssl-monitor`

3. **Configure**:
   - **Name**: `ssl-monitor-worker`
   - **Region**: Frankfurt
   - **Branch**: main
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && celery -A celery_worker worker --loglevel=info`

4. **Environment Variables** (same as backend):
   ```
   DATABASE_URL = [same as backend]
   REDIS_URL = [same as backend]
   TELEGRAM_BOT_TOKEN = [optional]
   ```

5. **Plan**: Free

6. **Create Background Worker**

---

## STEP 8: Create Celery Beat Scheduler (5 min)

1. **Click** "New +" → "Background Worker"

2. **Connect Repository**: `maydanov-dev/ssl-monitor`

3. **Configure**:
   - **Name**: `ssl-monitor-beat`
   - **Region**: Frankfurt
   - **Branch**: main
   - **Build Command**: `pip install -r backend/requirements.txt`
   - **Start Command**: `cd backend && celery -A celery_worker beat --loglevel=info`

4. **Environment Variables**:
   ```
   DATABASE_URL = [same as backend]
   REDIS_URL = [same as backend]
   ```

5. **Plan**: Free

6. **Create Background Worker**

---

## STEP 9: Test Your Deployment (5 min)

### Test from terminal:

```bash
# Test health check
curl https://ssl-monitor-backend.onrender.com/health

# Should return:
# {"status":"healthy","database":"connected"}

# Test billing plans
curl https://ssl-monitor-backend.onrender.com/billing/plans

# Should return 3 plans (Starter, Professional, Enterprise)

# Open API docs in browser
open https://ssl-monitor-backend.onrender.com/docs
```

### Or use the test script:

```bash
cd /home/vmaidaniuk/ssl-monitor
./test_production.sh https://ssl-monitor-backend.onrender.com
```

---

## STEP 10: Configure Cloudflare DNS (10 min)

### Get your Render IP/CNAME:

1. In Render backend service settings
2. Go to "Settings" tab
3. Scroll to "Custom Domains"
4. Note the instructions - Render will give you either:
   - CNAME target, OR
   - A record IP

### Configure in Cloudflare:

1. **Login to Cloudflare**: https://dash.cloudflare.com

2. **Select domain**: cloudsre.xyz

3. **Go to**: DNS → Records

4. **Add DNS Records** (see DNS_RECORDS.txt for details):

   **For Backend API**:
   ```
   Type: CNAME
   Name: api
   Target: ssl-monitor-backend.onrender.com
   Proxy: ON (orange cloud)
   TTL: Auto
   ```

   **For Root Domain** (if you want main site):
   ```
   Type: CNAME
   Name: @
   Target: ssl-monitor-backend.onrender.com
   Proxy: ON
   TTL: Auto
   ```

   **For WWW**:
   ```
   Type: CNAME
   Name: www
   Target: ssl-monitor-backend.onrender.com
   Proxy: ON
   TTL: Auto
   ```

5. **Save** all records

6. **Wait** 2-5 minutes for propagation

---

## STEP 11: Add Custom Domain in Render (5 min)

1. **In Render backend service**:
   - Go to "Settings" tab
   - Scroll to "Custom Domains"
   - Click "Add Custom Domain"

2. **Add domains**:
   - `api.cloudsre.xyz`
   - `cloudsre.xyz` (if you want)
   - `www.cloudsre.xyz` (if you want)

3. **Render will**:
   - Verify DNS records
   - Issue free SSL certificate
   - Take 5-10 minutes

4. **Wait** for "Verified" status

---

## STEP 12: Configure Stripe Webhooks (5 min)

1. **Stripe Dashboard**: https://dashboard.stripe.com

2. **Navigate to**: Developers → Webhooks

3. **Click**: "Add endpoint"

4. **Endpoint URL**: `https://api.cloudsre.xyz/billing/webhook`
   (or `https://ssl-monitor-backend.onrender.com/billing/webhook`)

5. **Select events**:
   - `checkout.session.completed`
   - `customer.subscription.created`
   - `customer.subscription.updated`
   - `customer.subscription.deleted`
   - `invoice.payment_succeeded`
   - `invoice.payment_failed`

6. **Click** "Add endpoint"

7. **Copy** "Signing secret" (starts with `whsec_...`)

8. **Add to Render**:
   - Go to backend service
   - Settings → Environment
   - Add: `STRIPE_WEBHOOK_SECRET = whsec_xxxxx`
   - Save changes
   - Service will auto-redeploy

---

## STEP 13: Final Testing (5 min)

### Test your live URLs:

```bash
# Test with Render URL
curl https://ssl-monitor-backend.onrender.com/health
curl https://ssl-monitor-backend.onrender.com/billing/plans

# Test with custom domain (after DNS propagates)
curl https://api.cloudsre.xyz/health
curl https://api.cloudsre.xyz/billing/plans

# Open in browser
open https://api.cloudsre.xyz/docs
```

### Test Stripe Checkout:

1. Open: https://api.cloudsre.xyz/docs
2. Find `/billing/create-checkout-session` endpoint
3. Click "Try it out"
4. Enter:
   ```json
   {
     "email": "test@example.com",
     "plan": "professional",
     "trial_days": 14
   }
   ```
5. Execute
6. Copy `checkout_url` from response
7. Open URL in browser
8. Should see Stripe Checkout page!

### Test SSL Monitoring:

1. Add test domain:
   ```bash
   curl -X POST https://api.cloudsre.xyz/domains/ \
     -H "Content-Type: application/json" \
     -d '{"name": "google.com", "alert_threshold_days": 30}'
   ```

2. Check SSL:
   ```bash
   curl -X POST https://api.cloudsre.xyz/domains/1/check
   ```

3. Should return SSL status with expiry date!

---

## ✅ Deployment Complete!

### Your Live URLs:

- **API**: https://ssl-monitor-backend.onrender.com
- **API (Custom)**: https://api.cloudsre.xyz
- **API Docs**: https://api.cloudsre.xyz/docs
- **Health**: https://api.cloudsre.xyz/health

### Services Running:

1. ✅ PostgreSQL Database
2. ✅ Redis Cache
3. ✅ Backend API (FastAPI)
4. ✅ Celery Worker (background tasks)
5. ✅ Celery Beat (scheduler)

### Next Steps:

1. **Test thoroughly** - all endpoints should work
2. **Share on LinkedIn** - use template from DEPLOY_NOW.md
3. **Email your network** - 10 people minimum
4. **Post on Reddit** - r/SideProject, r/devops
5. **Start customer outreach** - see FIRST_SALE_CHECKLIST.md
6. **Get first paying customer** - within 7 days!

---

## 🆘 Troubleshooting

### Error 521 - Web Server Is Down

**Causes**:
- Service not deployed yet (wait 10 minutes)
- Health check failing
- Environment variables missing

**Solutions**:
1. Check Render logs
2. Verify DATABASE_URL is set
3. Restart service in Render dashboard

### Database Connection Errors

**Check**:
- DATABASE_URL format is correct
- Database is running (check in Render)
- Network connectivity

**Fix**:
```bash
# Test connection from Render shell
psql $DATABASE_URL -c "SELECT 1"
```

### Stripe Webhook Failing

**Check**:
- Webhook URL is accessible
- STRIPE_WEBHOOK_SECRET is set correctly
- Events are selected in Stripe dashboard

**Fix**:
- Test webhook URL: `curl https://api.cloudsre.xyz/billing/webhook`
- Check Render logs for errors

---

## 📞 Support

If you get stuck:
1. Check logs in Render dashboard
2. Review TROUBLESHOOTING.md
3. Email: vla.maidaniuk@gmail.com

---

**🎉 Once deployed, you have a live SaaS business!**

**Next**: Get your first paying customer within 7 days!

