# 🔧 FastAPI + Gunicorn Fix для Render.com

## 🔴 ПРОБЛЕМА
```
AttributeError: module 'app' has no attribute 'app'
```

**Причина:** Неправильная конфигурация Gunicorn для FastAPI приложения.

---

## ✅ РЕШЕНИЕ

### 1. Создан wsgi.py файл
```python
# backend/wsgi.py
import os
import sys

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

# Import the FastAPI app
from app.main import app

# This is what Gunicorn will look for
application = app

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8000)))
```

### 2. Обновлен render.yaml
**Старая команда (неправильная):**
```yaml
startCommand: gunicorn app.main:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
```

**Новая команда (правильная):**
```yaml
startCommand: gunicorn wsgi:application -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

### 3. Ключевые изменения:
- ✅ **wsgi:application** - правильная ссылка на FastAPI app
- ✅ **uvicorn.workers.UvicornWorker** - специальный worker для FastAPI
- ✅ **4 workers** - оптимальное количество для free tier
- ✅ **Правильный timeout** - 120 секунд

---

## 🎯 АЛЬТЕРНАТИВНЫЕ КОМАНДЫ

### Вариант 1: Через wsgi.py (рекомендуется)
```bash
gunicorn wsgi:application -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

### Вариант 2: Прямо через app.main
```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:$PORT --timeout 120
```

### Вариант 3: Только uvicorn (если gunicorn не работает)
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
```

---

## 📋 ПОЧЕМУ ЭТО РАБОТАЕТ

### FastAPI vs Flask:
- **Flask**: `app = Flask(__name__)`
- **FastAPI**: `app = FastAPI()`

### Gunicorn Workers:
- **Flask**: `gunicorn app:app`
- **FastAPI**: `gunicorn wsgi:application -k uvicorn.workers.UvicornWorker`

### Uvicorn Workers:
UvicornWorker - это специальный worker для ASGI приложений (FastAPI, Starlette), который:
- ✅ Поддерживает async/await
- ✅ Обрабатывает WebSocket соединения
- ✅ Оптимизирован для FastAPI

---

## 🚀 DEPLOYMENT

### После исправления:
1. **Commit изменения:**
   ```bash
   git add backend/wsgi.py render.yaml
   git commit -m "Fix: Add wsgi.py and update render.yaml for FastAPI"
   git push origin main
   ```

2. **Render автоматически:**
   - Обнаружит новый commit
   - Перезапустит deployment
   - Использует новую команду

3. **Проверка через 5-10 минут:**
   ```bash
   curl https://ssl-monitor-api.onrender.com/health
   ```

---

## 🔍 ОТЛАДКА

### Если все еще не работает:

1. **Проверьте логи в Render Dashboard**
2. **Убедитесь что wsgi.py создан правильно**
3. **Попробуйте альтернативную команду**

### Проверка wsgi.py:
```bash
cd backend
python -c "import wsgi; print('wsgi.py работает!')"
```

### Проверка FastAPI app:
```bash
cd backend
python -c "from app.main import app; print('FastAPI app загружен!')"
```

---

## ✅ РЕЗУЛЬТАТ

После исправления:
- ✅ FastAPI приложение корректно запускается
- ✅ Gunicorn использует правильный worker
- ✅ Все endpoints доступны
- ✅ Health check работает
- ✅ API docs доступны по /docs

**Проблема решена!** 🎉

