# 📁 SSL Monitor Pro - Project Structure

## 🎯 ROOT DIRECTORY SETUP FOR RENDER.COM

**Important**: В `render.yaml` указано `rootDir: backend`  
Это означает, что **все команды Render.com выполняются из директории `backend/`**

---

## 📂 ПОЛНАЯ СТРУКТУРА ПРОЕКТА

```
ssl-monitor-final/
│
├── 📁 backend/                          ← ROOT для Render.com
│   ├── 📁 app/
│   │   ├── __init__.py
│   │   ├── main.py                      ← FastAPI приложение
│   │   ├── billing.py                   ← Billing endpoints
│   │   └── config.py                    ← ✅ Конфигурация (DATABASE_URL cleaning)
│   │
│   ├── 📁 models/
│   │   └── __init__.py                  ← SQLAlchemy модели
│   │
│   ├── 📁 services/
│   │   ├── ssl_service.py               ← SSL certificate checking
│   │   ├── telegram_bot.py              ← Telegram notifications
│   │   ├── referral_system.py           ← Referral codes
│   │   └── email_campaigns.py           ← Email marketing
│   │
│   ├── database.py                      ← ✅ Database connection (с load_dotenv)
│   ├── schemas.py                       ← Pydantic schemas
│   ├── celery_worker.py                 ← Celery tasks
│   ├── wsgi.py                          ← WSGI entry point (не используется)
│   │
│   ├── requirements.txt                 ← ✅ Python dependencies (без gunicorn)
│   ├── runtime.txt                      ← ✅ Python version: 3.11.10
│   ├── .env                             ← Environment variables (локально)
│   ├── Dockerfile                       ← Docker config (не используется на Render)
│   └── venv/                            ← Virtual environment (локально)
│
├── 📁 frontend/
│   ├── index.html                       ← Dashboard
│   ├── pricing.html                     ← Pricing page
│   ├── 📁 landing/
│   │   └── index.html                   ← Landing page
│   ├── 📁 css/
│   │   └── style.css
│   └── 📁 js/
│       ├── app.js
│       └── analytics.js
│
├── 📁 database/
│   └── init.sql                         ← PostgreSQL init script
│
├── 📁 scripts/
│   └── (deployment scripts)
│
├── 📁 config/
│   └── (configuration files)
│
├── render.yaml                          ← ✅ Render.com configuration
├── docker-compose.yml                   ← Docker Compose (локально)
├── .gitignore
├── README.md
│
└── 📋 DOCUMENTATION:
    ├── LOCAL_DEVELOPMENT_SETUP.md       ← Локальная разработка
    ├── TESTING_RESULTS.md               ← Результаты тестирования
    ├── RENDER_FIX_INSTRUCTIONS.md       ← Render.com deployment
    ├── QUICKSTART.md
    ├── MONETIZATION_GUIDE.md
    └── DEPLOYMENT_SUMMARY.md
```

---

## 🚀 RENDER.COM ВАЖНАЯ ИНФОРМАЦИЯ

### Root Directory = `backend`

Когда Render.com запускает ваше приложение:

1. **Working Directory**: `/opt/render/project/src/backend`
2. **Build Command**: `pip install -r requirements.txt`
   - Ищет файл: `backend/requirements.txt` ✅
3. **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Ищет модуль: `backend/app/main.py` ✅

---

## ✅ КРИТИЧЕСКИЕ ФАЙЛЫ ДЛЯ RENDER.COM

### 1. `backend/requirements.txt`
```txt
fastapi==0.100.0
uvicorn[standard]==0.23.2
sqlalchemy==2.0.20
psycopg2-binary==2.9.7
redis==5.0.1
celery==5.3.1
cryptography==41.0.4
requests==2.31.0
python-multipart==0.0.6
pydantic==1.10.12
python-dotenv==1.0.0
alembic==1.12.0
stripe==5.5.0
PyJWT==2.8.0
passlib==1.7.4
bcrypt==4.0.1
python-jose[cryptography]==3.3.0
```

**✅ НЕТ gunicorn** - FastAPI работает только с uvicorn!

---

### 2. `backend/runtime.txt`
```txt
python-3.11.10
```

**Зачем**: Render.com по умолчанию может использовать Python 3.13, который несовместим с Pydantic 1.10.12

---

### 3. `backend/app/config.py`
```python
from dotenv import load_dotenv
load_dotenv()

def get_database_url():
    url = os.getenv("DATABASE_URL", "")
    url = url.strip('"').strip("'")  # Убираем кавычки
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url
```

**Зачем**: 
- Render.com может добавлять кавычки в DATABASE_URL
- Старые версии PostgreSQL используют `postgres://` вместо `postgresql://`

---

### 4. `backend/database.py`
```python
from dotenv import load_dotenv
load_dotenv()  # ✅ Загружает .env файл

def get_clean_database_url():
    url = os.getenv("DATABASE_URL", "...")
    url = url.strip('"').strip("'")
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)
    return url

DATABASE_URL = get_clean_database_url()
engine = create_engine(DATABASE_URL)
```

**Зачем**: Гарантирует правильное подключение к PostgreSQL

---

### 5. `render.yaml`
```yaml
services:
  - type: web
    name: ssl-monitor-api
    env: python
    rootDir: backend          # ← ВСЕ КОМАНДЫ ИЗ backend/
    buildCommand: pip install --upgrade pip && pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT --workers 4
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: DATABASE_URL
        fromDatabase:
          name: ssl-monitor-db
          property: connectionString
```

---

## 📝 PATHS ОТНОСИТЕЛЬНО ROOT DIRECTORY

Когда `rootDir: backend`, все пути интерпретируются так:

| Указан путь | Реальный путь на Render |
|-------------|------------------------|
| `requirements.txt` | `backend/requirements.txt` ✅ |
| `app/main.py` | `backend/app/main.py` ✅ |
| `database.py` | `backend/database.py` ✅ |
| `.env` | `backend/.env` ✅ |
| `runtime.txt` | `backend/runtime.txt` ✅ |

---

## 🔧 КАК РАБОТАЕТ DEPLOYMENT

### Step 1: Clone Repository
```bash
git clone https://192.168.1.10/root/ssl-monitor-pro.git
cd ssl-monitor
```

### Step 2: Change to Root Directory
```bash
cd backend  # ← rootDir из render.yaml
```

### Step 3: Build
```bash
pip install --upgrade pip
pip install -r requirements.txt  # backend/requirements.txt
```

### Step 4: Start
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
# Ищет: backend/app/main.py ✅
```

---

## ⚠️ ЧАСТЫЕ ОШИБКИ

### ❌ Ошибка 1: "requirements.txt not found"
**Причина**: `rootDir` не указан или неправильный  
**Решение**: В `render.yaml` должно быть `rootDir: backend`

### ❌ Ошибка 2: "module 'app' has no attribute 'app'"
**Причина**: Неправильный startCommand  
**Решение**: `uvicorn app.main:app` (не `gunicorn`)

### ❌ Ошибка 3: "postgres:// URL not supported"
**Причина**: Старый формат DATABASE_URL  
**Решение**: `config.py` автоматически конвертирует

### ❌ Ошибка 4: "Pydantic requires Rust compiler"
**Причина**: Python 3.13 + Pydantic 2.x  
**Решение**: `runtime.txt` с Python 3.11.10 + Pydantic 1.10.12

---

## ✅ CHECKLIST ДЛЯ RENDER.COM

Перед deployment убедитесь:

- [x] ✅ `render.yaml` существует в корне проекта
- [x] ✅ `rootDir: backend` указан в render.yaml
- [x] ✅ `backend/requirements.txt` существует
- [x] ✅ `backend/runtime.txt` существует (python-3.11.10)
- [x] ✅ `backend/app/main.py` существует
- [x] ✅ `backend/app/config.py` существует
- [x] ✅ `backend/database.py` имеет load_dotenv()
- [x] ✅ Нет gunicorn в requirements.txt
- [x] ✅ startCommand использует uvicorn

---

## 🎯 ПРОВЕРКА СТРУКТУРЫ

### Команды для проверки:
```bash
# Проверить что все файлы на месте
ls -la backend/requirements.txt
ls -la backend/runtime.txt
ls -la backend/app/main.py
ls -la backend/app/config.py
ls -la backend/database.py

# Проверить содержимое requirements.txt
cat backend/requirements.txt | grep -E "fastapi|uvicorn|pydantic"

# Проверить что НЕТ gunicorn
cat backend/requirements.txt | grep gunicorn
# Не должно ничего найти
```

---

## 📞 SUPPORT

**Структура проекта корректна и готова для Render.com!**

Все файлы находятся в правильных местах:
- ✅ `backend/` - root directory для Render
- ✅ `backend/requirements.txt` - зависимости
- ✅ `backend/app/main.py` - FastAPI app
- ✅ `backend/runtime.txt` - Python 3.11.10

**Render.com deployment должен пройти успешно!** 🚀


