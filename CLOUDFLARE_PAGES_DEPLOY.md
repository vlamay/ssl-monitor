# 🌐 Cloudflare Pages Deployment Guide

## 🎯 ЦЕЛЬ
Задеплоить frontend на Cloudflare Pages и подключить к домену cloudsre.xyz

---

## 📋 ПОШАГОВАЯ ИНСТРУКЦИЯ

### ШАГ 1: Подготовка GitHub Repository

✅ **Уже выполнено!** Код загружен в:
```
https://192.168.1.10/root/ssl-monitor-pro
```

Директория frontend: `frontend-modern/`

---

### ШАГ 2: Создать Cloudflare Pages Project

1. **Откройте Cloudflare Dashboard:**
   ```
   https://dash.cloudflare.com
   ```

2. **Перейдите в Pages:**
   - Слева: "Workers & Pages"
   - Нажмите: "Create application"
   - Выберите: "Pages"
   - Нажмите: "Connect to Git"

3. **Подключите GitHub:**
   - Авторизуйте Cloudflare в GitHub
   - Выберите репозиторий: `ssl-monitor`
   - Нажмите: "Begin setup"

4. **Настройте Build:**
   ```
   Project name: ssl-monitor-frontend
   Production branch: main
   Build command: (оставьте пустым)
   Build output directory: frontend-modern
   ```

5. **Environment Variables (пусто для статики):**
   - Не требуется для статического frontend

6. **Нажмите "Save and Deploy"**

---

### ШАГ 3: Получить URL от Cloudflare Pages

После deployment (~2-3 минуты) вы получите URL вида:
```
https://ssl-monitor-frontend.pages.dev
```

**Протестируйте:**
- Landing: https://ssl-monitor-frontend.pages.dev
- Dashboard: https://ssl-monitor-frontend.pages.dev/dashboard.html

---

### ШАГ 4: Настроить Custom Domain (cloudsre.xyz)

1. **В Cloudflare Pages Dashboard:**
   - Откройте ваш project: `ssl-monitor-frontend`
   - Перейдите: "Custom domains"
   - Нажмите: "Set up a custom domain"

2. **Добавьте домены:**
   
   **Для корневого домена:**
   ```
   Domain: cloudsre.xyz
   ```
   
   **Для поддомена:**
   ```
   Domain: www.cloudsre.xyz
   ```

3. **Cloudflare автоматически:**
   - Создаст CNAME записи
   - Выдаст SSL сертификат
   - Настроит CDN

4. **DNS Records (автоматически создаются):**
   ```
   Type: CNAME
   Name: @
   Target: ssl-monitor-frontend.pages.dev
   Proxy: ✅ Proxied (оранжевое облако)
   
   Type: CNAME
   Name: www
   Target: ssl-monitor-frontend.pages.dev
   Proxy: ✅ Proxied
   ```

---

### ШАГ 5: Настроить Backend API на Subdomain

**Backend URL:** `https://status.cloudsre.xyz`

1. **В Cloudflare DNS:**
   - Перейдите: DNS → Records
   - Нажмите: "Add record"

2. **Создайте CNAME для API:**
   ```
   Type: CNAME
   Name: status
   Target: ssl-monitor-api.onrender.com
   Proxy status: ✅ Proxied (оранжевое облако)
   TTL: Auto
   ```

3. **Сохраните**

---

### ШАГ 6: Обновить Render.com Environment Variables

1. **Откройте Render Dashboard:**
   ```
   https://dashboard.render.com
   ```

2. **Найдите service:** `ssl-monitor-api`

3. **Settings → Environment:**
   
   **Обновите/добавьте:**
   ```
   FRONTEND_URL=https://cloudsre.xyz
   BACKEND_URL=https://status.cloudsre.xyz
   ```

4. **Save Changes** → Render автоматически перезапустит service

---

### ШАГ 7: Проверка DNS Propagation

Подождите 2-5 минут, затем проверьте:

```bash
# Проверить DNS записи
dig cloudsre.xyz
dig www.cloudsre.xyz
dig status.cloudsre.xyz

# Проверить доступность
curl -I https://cloudsre.xyz
curl -I https://status.cloudsre.xyz/health
```

**Ожидаемые результаты:**
- `cloudsre.xyz` → Cloudflare Pages (frontend)
- `www.cloudsre.xyz` → Cloudflare Pages (frontend)
- `status.cloudsre.xyz` → Render.com (backend API)

---

### ШАГ 8: Тестирование Full Stack

1. **Откройте Landing Page:**
   ```
   https://cloudsre.xyz
   ```

2. **Откройте Dashboard:**
   ```
   https://cloudsre.xyz/dashboard.html
   ```

3. **Проверьте API:**
   ```bash
   # Health check
   curl https://status.cloudsre.xyz/health
   
   # Statistics
   curl https://status.cloudsre.xyz/statistics
   
   # Domains
   curl https://status.cloudsre.xyz/domains/
   ```

4. **Тестируйте в браузере:**
   - Откройте dashboard
   - Добавьте домен (например: google.com)
   - Проверьте SSL
   - Посмотрите статистику

---

## 🔧 TROUBLESHOOTING

### Проблема 1: CORS Errors

**Symptom:** Console shows "CORS policy blocked"

**Solution:**
```python
# backend/app/main.py уже обновлён
allow_origins=[
    "https://cloudsre.xyz",
    "https://www.cloudsre.xyz",
    "https://status.cloudsre.xyz",
    "*"
]
```

Push changes и Render auto-deploy.

---

### Проблема 2: 404 Not Found on API

**Symptom:** API requests return 404

**Check:**
1. DNS records правильные
2. Render service работает
3. URL в `js/app.js` правильный

**Fix:**
```javascript
// js/app.js - уже обновлён
const API_BASE = 'https://status.cloudsre.xyz';
```

---

### Проблема 3: Mixed Content (HTTP/HTTPS)

**Symptom:** Browser blocks HTTP requests from HTTPS page

**Solution:** Все URLs должны быть HTTPS:
- ✅ Frontend: https://cloudsre.xyz
- ✅ Backend: https://status.cloudsre.xyz

---

### Проблема 4: DNS Not Resolving

**Check propagation:**
```bash
# Online tools:
https://www.whatsmydns.net/#CNAME/cloudsre.xyz
https://www.whatsmydns.net/#CNAME/status.cloudsre.xyz
```

**Wait:** DNS propagation может занять до 24 часов (обычно 5-10 минут)

---

## 📊 FINAL DNS CONFIGURATION

После всех настроек ваши DNS records должны выглядеть так:

```
# Cloudflare DNS Records for cloudsre.xyz

Type: CNAME
Name: @
Target: ssl-monitor-frontend.pages.dev
Proxy: ✅ Proxied

Type: CNAME
Name: www
Target: ssl-monitor-frontend.pages.dev
Proxy: ✅ Proxied

Type: CNAME
Name: status
Target: ssl-monitor-api.onrender.com
Proxy: ✅ Proxied
```

---

## ✅ CHECKLIST

### Cloudflare Pages:
- [ ] GitHub repository подключен
- [ ] Build settings настроены
- [ ] Project задеплоен
- [ ] Custom domain cloudsre.xyz добавлен
- [ ] SSL сертификат активен (автоматически)

### DNS Records:
- [ ] @ → Cloudflare Pages
- [ ] www → Cloudflare Pages
- [ ] status → Render.com API

### Backend:
- [ ] CORS настроен для cloudsre.xyz
- [ ] FRONTEND_URL обновлён
- [ ] BACKEND_URL обновлён
- [ ] Service перезапущен

### Testing:
- [ ] https://cloudsre.xyz загружается
- [ ] https://cloudsre.xyz/dashboard.html работает
- [ ] https://status.cloudsre.xyz/health возвращает 200
- [ ] Dashboard загружает домены
- [ ] Можно добавить домен
- [ ] SSL check работает
- [ ] Статистика отображается

---

## 🚀 DEPLOYMENT TIMELINE

| Шаг | Время | Действие |
|-----|-------|----------|
| 1 | 0 мин | Commit + Push код |
| 2 | 2-3 мин | Cloudflare Pages build |
| 3 | 1 мин | Добавить custom domain |
| 4 | 1 мин | Настроить DNS records |
| 5 | 5-10 мин | DNS propagation |
| 6 | 2 мин | Обновить Render env vars |
| 7 | 5 мин | Render redeploy |
| 8 | 2 мин | Тестирование |

**ИТОГО: ~20-30 минут до полностью рабочего production!**

---

## 🎯 SUCCESS CRITERIA

После успешного deployment:

✅ **Frontend:**
- https://cloudsre.xyz - landing page загружается
- https://cloudsre.xyz/dashboard.html - dashboard работает
- Responsive на всех устройствах

✅ **Backend:**
- https://status.cloudsre.xyz/health - returns 200 OK
- https://status.cloudsre.xyz/docs - Swagger UI доступен

✅ **Integration:**
- Dashboard загружает домены из API
- Можно добавлять/удалять домены
- SSL checks работают
- Статистика обновляется
- Нет CORS ошибок в console

---

## 📞 SUPPORT

**Email:** vla.maidaniuk@gmail.com  
**Phone:** +420 721 579 603  
**GitHub:** https://192.168.1.10/root/ssl-monitor-pro

---

## 🎉 ГОТОВО!

После выполнения всех шагов ваш SSL Monitor Pro будет полностью доступен на:

**🌐 Frontend:** https://cloudsre.xyz  
**🔧 API:** https://status.cloudsre.xyz  
**📖 Docs:** https://status.cloudsre.xyz/docs

**Production ready!** 🚀


