# 🚀 Render.com Commands - Правильные настройки

## ✅ Build Command (для всех сервисов):
```bash
pip install -r backend/requirements.txt
```

## ✅ Start Commands:

### Backend Web Service:
```bash
cd backend && gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT
```

### Альтернативный вариант (если gunicorn не работает):
```bash
cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

### Celery Worker:
```bash
cd backend && celery -A celery_worker worker --loglevel=info
```

### Celery Beat:
```bash
cd backend && celery -A celery_worker beat --loglevel=info
```

## 🔧 Environment Variables:
```
DATABASE_URL=postgresql://ssluser:password@dpg-xxxxx:5432/sslmonitor
REDIS_URL=redis://red-xxxxx:6379
STRIPE_SECRET_KEY=sk_test_51SGoJM20i6fmlbYddqN7SFX5II50PU8FNXk3TddOnH6QipGMvXwsmUxvoOKFITR42B924oxrc12Mx5t9pAQMX6Q700Zv95jBJt
STRIPE_PUBLISHABLE_KEY=pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
PYTHON_VERSION=3.11
```

## 🎯 Health Check Path:
```
/health
```

## 📝 Важные заметки:
- ✅ gunicorn добавлен в requirements.txt
- ✅ Используйте gunicorn для production
- ✅ Если gunicorn не работает, используйте uvicorn альтернативу
- ✅ Все команды протестированы

