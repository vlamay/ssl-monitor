# 🚀 SSL Monitor Pro - Local Development Setup

## ✅ SETUP COMPLETED!

Локальная среда разработки полностью настроена и работает!

---

## 📊 УСТАНОВЛЕННЫЕ КОМПОНЕНТЫ

### 1. **PostgreSQL 16**
- ✅ Установлен и настроен
- ✅ Порт: **5433** (не стандартный 5432!)
- ✅ База данных: `sslmonitor`
- ✅ Пользователь: `sslmonitor_user`
- ✅ Таблицы: `domains`, `ssl_checks`

### 2. **Redis 7**
- ✅ Установлен и работает
- ✅ Порт: **6379**
- ✅ Используется для Celery message broker

### 3. **Python Environment**
- ✅ Python 3.12
- ✅ Виртуальное окружение: `/home/vmaidaniuk/ssl-monitor-final/backend/venv`
- ✅ Все зависимости установлены

### 4. **FastAPI Backend**
- ✅ Запущен на `http://localhost:8000`
- ✅ API docs: `http://localhost:8000/docs`
- ✅ Health check: `http://localhost:8000/health`

---

## 🔧 КОНФИГУРАЦИЯ

### `.env` файл (`backend/.env`):
```ini
# Database - PostgreSQL использует порт 5433
DATABASE_URL=postgresql://sslmonitor_user@localhost:5433/sslmonitor

# Redis
REDIS_URL=redis://localhost:6379/0

# Secret Key
SECRET_KEY=dev-secret-key-change-in-production-12345678

# Frontend/Backend URLs
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Stripe Test Keys
STRIPE_SECRET_KEY=sk_test_51SGoJM20i6fmlbYddqN7SFX5II50PU8FNXk3TddOnH6QipGMvXwsmUxvoOKFITR42B924oxrc12Mx5t9pAQMX6Q700Zv95jBJt
STRIPE_PUBLISHABLE_KEY=pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
STRIPE_WEBHOOK_SECRET=whsec_test_placeholder

# Telegram (опционально)
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
```

---

## 🚀 КАК ЗАПУСТИТЬ

### 1. **Запустить PostgreSQL:**
```bash
sudo systemctl start postgresql
```

### 2. **Запустить Redis:**
```bash
sudo redis-server --daemonize yes --port 6379
```

### 3. **Запустить Backend:**
```bash
cd /home/vmaidaniuk/ssl-monitor-final/backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 4. **Запустить Celery Worker (в отдельном терминале):**
```bash
cd /home/vmaidaniuk/ssl-monitor-final/backend
source venv/bin/activate
celery -A celery_worker worker --loglevel=info
```

### 5. **Запустить Celery Beat (в отдельном терминале):**
```bash
cd /home/vmaidaniuk/ssl-monitor-final/backend
source venv/bin/activate
celery -A celery_worker beat --loglevel=info
```

---

## 🧪 ТЕСТИРОВАНИЕ API

### Health Check:
```bash
curl http://localhost:8000/health
```

### Создать домен:
```bash
curl -X POST "http://localhost:8000/domains/" \
  -H "Content-Type: application/json" \
  -d '{"name": "google.com"}'
```

### Список доменов:
```bash
curl http://localhost:8000/domains/
```

### Проверить SSL:
```bash
curl -X POST "http://localhost:8000/domains/1/check"
```

### Статус SSL:
```bash
curl http://localhost:8000/domains/1/ssl-status
```

### Статистика:
```bash
curl http://localhost:8000/statistics
```

---

## 📁 СТРУКТУРА ПРОЕКТА

```
ssl-monitor-final/
├── backend/
│   ├── app/
│   │   ├── main.py          # FastAPI приложение
│   │   └── billing.py       # Billing API endpoints
│   ├── models/
│   │   └── __init__.py      # SQLAlchemy модели
│   ├── services/
│   │   ├── ssl_service.py   # SSL проверки
│   │   ├── telegram_bot.py  # Telegram уведомления
│   │   ├── referral_system.py
│   │   └── email_campaigns.py
│   ├── database.py          # Database connection
│   ├── schemas.py           # Pydantic schemas
│   ├── celery_worker.py     # Celery tasks
│   ├── requirements.txt     # Python dependencies
│   ├── .env                 # Environment variables
│   └── venv/                # Virtual environment
├── frontend/
│   ├── index.html           # Dashboard
│   ├── pricing.html         # Pricing page
│   ├── landing/
│   │   └── index.html       # Landing page
│   ├── css/
│   │   └── style.css
│   └── js/
│       ├── app.js
│       └── analytics.js
└── ...
```

---

## 🗄️ DATABASE SCHEMA

### `domains` table:
```sql
CREATE TABLE domains (
    id SERIAL PRIMARY KEY,
    name VARCHAR UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    alert_threshold_days INTEGER DEFAULT 30
);
```

### `ssl_checks` table:
```sql
CREATE TABLE ssl_checks (
    id SERIAL PRIMARY KEY,
    domain_id INTEGER REFERENCES domains(id),
    checked_at TIMESTAMP DEFAULT NOW(),
    expires_in INTEGER,
    is_valid BOOLEAN,
    error_message TEXT,
    issuer VARCHAR,
    subject VARCHAR,
    not_valid_before TIMESTAMP,
    not_valid_after TIMESTAMP
);
```

---

## 🔍 ПОЛЕЗНЫЕ КОМАНДЫ

### PostgreSQL:
```bash
# Подключиться к БД
psql -U sslmonitor_user -d sslmonitor

# Список таблиц
\dt

# Просмотр записей
SELECT * FROM domains;
SELECT * FROM ssl_checks;

# Выход
\q
```

### Redis:
```bash
# Проверить подключение
redis-cli ping

# Мониторинг команд
redis-cli monitor

# Очистить все данные (осторожно!)
redis-cli FLUSHALL
```

### Python/Django:
```bash
# Активировать venv
source venv/bin/activate

# Установить новую зависимость
pip install <package>
pip freeze > requirements.txt

# Деактивировать venv
deactivate
```

---

## 🐛 TROUBLESHOOTING

### Проблема: PostgreSQL не запускается
```bash
sudo systemctl status postgresql
sudo journalctl -xeu postgresql
```

### Проблема: Redis не запускается
```bash
# Проверить процесс
ps aux | grep redis

# Остановить старый процесс
sudo pkill redis-server

# Запустить снова
sudo redis-server --daemonize yes --port 6379
```

### Проблема: Backend не подключается к БД
```bash
# Проверить DATABASE_URL в .env
cat backend/.env | grep DATABASE_URL

# Проверить порт PostgreSQL
ss -tulpn | grep 5433
```

### Проблема: Import errors
```bash
# Переустановить venv
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## 📚 API DOCUMENTATION

### Автоматическая документация:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Основные endpoints:

#### Domains:
- `POST /domains/` - Добавить домен
- `GET /domains/` - Список доменов
- `GET /domains/{id}` - Получить домен
- `PATCH /domains/{id}` - Обновить домен
- `DELETE /domains/{id}` - Удалить домен

#### SSL Checks:
- `POST /domains/{id}/check` - Проверить SSL
- `GET /domains/{id}/ssl-status` - Статус SSL
- `GET /domains/{id}/checks` - История проверок

#### Billing:
- `GET /billing/plans` - Тарифные планы
- `POST /billing/create-checkout-session` - Создать сессию оплаты
- `POST /billing/webhook` - Stripe webhook

#### Statistics:
- `GET /statistics` - Общая статистика

---

## 🎯 NEXT STEPS

1. **Frontend Development**:
   - Настроить frontend (HTML/JS или React)
   - Подключить к API
   - Добавить аутентификацию

2. **Celery Tasks**:
   - Настроить периодические проверки
   - Добавить email уведомления
   - Интегрировать Telegram bot

3. **Testing**:
   - Написать unit tests
   - Написать integration tests
   - Добавить CI/CD

4. **Production Deployment**:
   - Задеплоить на Render.com
   - Настроить custom domain
   - Настроить мониторинг

---

## ✅ CHECKLIST

- [x] PostgreSQL установлен и работает
- [x] Redis установлен и работает
- [x] Python зависимости установлены
- [x] .env файл создан
- [x] База данных создана
- [x] Таблицы созданы
- [x] Backend запущен и работает
- [x] API endpoints тестируются
- [ ] Celery worker запущен
- [ ] Celery beat запущен
- [ ] Frontend настроен
- [ ] Stripe webhooks настроены
- [ ] Telegram bot настроен

---

## 📞 SUPPORT

Если возникли проблемы:
1. Проверьте логи backend
2. Проверьте .env файл
3. Проверьте что PostgreSQL и Redis работают
4. Проверьте firewall rules

**Email**: vla.maidaniuk@gmail.com  
**Tel**: +420 721 579 603

---

🎉 **Локальная среда полностью готова к разработке!**


