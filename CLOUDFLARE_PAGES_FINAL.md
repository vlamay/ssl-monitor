# ☁️ Cloudflare Pages Deployment - Final Guide

## Quick Deploy (10 minutes)

### Step 1: Create Project

1. Go to: https://dash.cloudflare.com → Pages
2. Click: **Create a project**
3. Click: **Connect to Git**

### Step 2: Connect GitHub

1. Select: **GitHub**
2. Authorize Cloudflare
3. Select repository: `ssl-monitor-final` (or your repo name)
4. Click: **Begin setup**

### Step 3: Build Configuration

```
Project name: ssl-monitor-prod
Production branch: main
```

**Build settings:**
```
Framework preset: None
Build command: (leave empty)
Build output directory: /frontend-modern
Root directory: (leave empty)
```

**Environment variables:**
```
NODE_ENV=production
```

### Step 4: Deploy

1. Click: **Save and Deploy**
2. Wait 2-3 minutes for deployment
3. Get deployment URL: `https://ssl-monitor-prod.pages.dev`

### Step 5: Custom Domain

1. Go to: **Custom domains**
2. Click: **Set up a custom domain**
3. Enter: `cloudsre.xyz`
4. Click: **Continue**
5. Cloudflare will create DNS records automatically

**Add www subdomain:**
1. Click: **Add a domain**
2. Enter: `www.cloudsre.xyz`
3. Click: **Activate domain**

### Step 6: DNS Records

Cloudflare automatically creates:
```
Type    Name    Target                              Proxy
CNAME   @       ssl-monitor-prod.pages.dev          Yes
CNAME   www     ssl-monitor-prod.pages.dev          Yes
```

**Manually add backend CNAME:**
```
Type    Name    Target                              Proxy
CNAME   status  ssl-monitor-api.onrender.com        Yes
```

### Step 7: SSL Certificate

- **Automatic:** Cloudflare Universal SSL
- **Wait:** 5-10 minutes for activation
- **Check:** https://cloudsre.xyz should work with HTTPS

---

## Verification

Test all URLs:

```bash
# Frontend
curl -I https://cloudsre.xyz
# Expected: 200 OK

# Frontend www
curl -I https://www.cloudsre.xyz
# Expected: 200 OK

# Backend API
curl https://status.cloudsre.xyz/health
# Expected: {"status":"healthy"}

# API docs
curl -I https://status.cloudsre.xyz/docs
# Expected: 200 OK
```

---

## Redeploy (if needed)

### Automatic redeploy:
- Push to `main` branch
- Cloudflare auto-deploys in 2-3 minutes

### Manual redeploy:
1. Go to: Cloudflare Pages → Deployments
2. Click: **Retry deployment**

---

## Frontend Configuration

**Frontend is already configured!**

File: `frontend-modern/js/app.js`
```javascript
const API_BASE = window.location.hostname === 'localhost' 
    ? 'http://localhost:8000' 
    : 'https://status.cloudsre.xyz';  // ✅ Production API
```

No build step needed - it's pure HTML/CSS/JS!

---

## Troubleshooting

### Issue: 404 on custom domain
**Solution:** Wait 10-15 minutes for DNS propagation

### Issue: Mixed content warnings
**Solution:** Ensure all resources use HTTPS (already done)

### Issue: API CORS errors
**Solution:** Check backend CORS settings include `https://cloudsre.xyz`

### Issue: Deployment fails
**Solution:** 
- Check build output directory is correct
- Verify index.html exists in frontend-modern/
- Check Cloudflare Pages logs

---

## Page Rules (Optional)

For better performance:

1. Go to: Cloudflare → Page Rules
2. Add rule: `cloudsre.xyz/*`
   - **Cache Level:** Standard
   - **Browser Cache TTL:** 4 hours
   - **Edge Cache TTL:** 2 hours

---

## Analytics (Optional)

Enable Cloudflare Web Analytics:

1. Go to: Cloudflare → Web Analytics
2. Click: **Add a site**
3. Enter: `cloudsre.xyz`
4. Copy tracking code
5. Add to `frontend-modern/index.html` before `</body>`

---

## Security Headers (Optional)

Add security headers in Cloudflare → Transform Rules:

```
X-Frame-Options: DENY
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
Referrer-Policy: strict-origin-when-cross-origin
```

---

## Status Check

After deployment, verify:

- ✅ https://cloudsre.xyz loads
- ✅ https://www.cloudsre.xyz loads
- ✅ https://status.cloudsre.xyz/health returns OK
- ✅ Dashboard can communicate with API
- ✅ SSL certificate is valid
- ✅ No console errors

---

## Next Steps

1. ✅ Frontend deployed
2. ✅ Custom domain configured
3. ⏳ Test adding a domain in dashboard
4. ⏳ Test Stripe checkout flow
5. ⏳ Verify Telegram notifications

---

**Your Frontend is Live!** 🎉

**URLs:**
- Frontend: https://cloudsre.xyz
- API: https://status.cloudsre.xyz
- Docs: https://status.cloudsre.xyz/docs

**Support:** vla.maidaniuk@gmail.com

