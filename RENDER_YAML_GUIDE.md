# 🚀 Render.yaml Deployment Guide

## ✅ Что включено в render.yaml:

### 🔧 Сервисы:
1. **ssl-monitor-api** - Backend API (FastAPI)
2. **ssl-monitor-db** - PostgreSQL Database  
3. **ssl-monitor-redis** - Redis Cache
4. **ssl-monitor-worker** - Celery Worker
5. **ssl-monitor-beat** - Celery Beat Scheduler

### 🌍 Регион: Frankfurt (Europe)
### 💰 План: Free (€0/месяц)

---

## 🎯 Как использовать render.yaml:

### Шаг 1: Загрузите код на GitHub
```bash
git add render.yaml
git commit -m "Add render.yaml for automatic deployment"
git push origin main
```

### Шаг 2: Создайте аккаунт на Render.com
1. Откройте: https://render.com
2. Войдите через GitHub
3. Авторизуйте доступ к репозиторию

### Шаг 3: Автоматический deployment
1. В Render Dashboard нажмите "New +"
2. Выберите "Blueprint"
3. Подключите репозиторий: `root/ssl-monitor-pro`
4. Render автоматически создаст все сервисы из render.yaml

### Шаг 4: Настройте Environment Variables
После создания сервисов добавьте в Backend API:

```
STRIPE_SECRET_KEY = YOUR_STRIPE_SECRET_KEY_HERE
STRIPE_PUBLISHABLE_KEY = pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
STRIPE_WEBHOOK_SECRET = whsec_xxxxx (после настройки webhooks)
```

---

## 🔧 Исправления в render.yaml:

### ✅ Что исправлено:
- **startCommand**: `gunicorn app.main:app` (правильный путь)
- **Добавлен Redis**: Отдельный сервис для кеша
- **Правильные envVars**: Связаны между сервисами
- **Убрано FLASK_ENV**: Используем FastAPI, не Flask
- **Добавлены Stripe переменные**: Для payment интеграции

### 🎯 Команды:
- **Build**: `pip install --upgrade pip && pip install -r requirements.txt`
- **Start API**: `gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120`
- **Start Worker**: `celery -A celery_worker worker --loglevel=info --pool=solo`
- **Start Beat**: `celery -A celery_worker beat --loglevel=info`

---

## 🌐 Результирующие URLs:

После deployment:
- **API**: https://ssl-monitor-api.onrender.com
- **Health**: https://ssl-monitor-api.onrender.com/health
- **Docs**: https://ssl-monitor-api.onrender.com/docs

---

## ⏰ Время deployment:
- **Blueprint creation**: 2 минуты
- **All services ready**: 15-20 минут
- **Total time**: ~25 минут

---

## 🎉 После deployment:

1. ✅ Проверьте health endpoint
2. ✅ Настройте Stripe webhooks
3. ✅ Добавьте custom domain
4. ✅ Начните привлечение клиентов!

---

**render.yaml готов к использованию!** 🚀

