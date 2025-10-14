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
