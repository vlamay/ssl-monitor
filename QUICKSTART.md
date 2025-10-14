# SSL Monitor - Быстрый старт

## ✅ Система успешно запущена!

Все сервисы работают:
- ✅ PostgreSQL Database (port 5432)
- ✅ Redis Cache (port 6379)
- ✅ FastAPI Backend (port 8000)
- ✅ Celery Worker (background)
- ✅ Celery Beat Scheduler (background)
- ✅ Frontend Dashboard (port 80)

## 🌐 Доступ к системе

### Web Dashboard
Откройте в браузере: **http://localhost**

### API Documentation
Интерактивная документация Swagger: **http://localhost:8000/docs**

Альтернативная документация ReDoc: **http://localhost:8000/redoc**

## 🧪 Тестирование API через curl

### 1. Health Check
```bash
curl http://localhost:8000/health
```

### 2. Список всех доменов
```bash
curl http://localhost:8000/domains/
```

### 3. Добавить новый домен
```bash
curl -X POST "http://localhost:8000/domains/" \
  -H "Content-Type: application/json" \
  -d '{"name": "example.com", "alert_threshold_days": 30}'
```

### 4. Проверить SSL сертификат
```bash
curl -X POST "http://localhost:8000/domains/1/check"
```

### 5. Получить статус SSL
```bash
curl http://localhost:8000/domains/1/ssl-status
```

### 6. История проверок
```bash
curl http://localhost:8000/domains/1/checks
```

### 7. Общая статистика
```bash
curl http://localhost:8000/statistics
```

### 8. Удалить домен
```bash
curl -X DELETE http://localhost:8000/domains/1
```

## 📊 Управление Docker

### Просмотр логов
```bash
# Все сервисы
sudo docker-compose logs -f

# Только backend
sudo docker-compose logs -f backend

# Только celery worker
sudo docker-compose logs -f celery-worker
```

### Остановить систему
```bash
sudo docker-compose stop
```

### Запустить систему
```bash
sudo docker-compose start
```

### Полностью остановить и удалить контейнеры
```bash
sudo docker-compose down
```

### Пересобрать контейнеры
```bash
sudo docker-compose up -d --build
```

### Проверить статус контейнеров
```bash
sudo docker-compose ps
```

## 🔔 Настройка Telegram уведомлений

1. Создайте Telegram бота через @BotFather:
   - Откройте Telegram
   - Найдите @BotFather
   - Отправьте команду `/newbot`
   - Следуйте инструкциям
   - Сохраните токен бота

2. Получите Chat ID:
   - Отправьте сообщение вашему боту
   - Откройте в браузере: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Найдите `"chat":{"id": XXXXXXX}` - это ваш Chat ID

3. Добавьте переменные окружения:
   ```bash
   # Создайте файл .env
   cp .env.example .env
   
   # Отредактируйте .env и добавьте:
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_CHAT_ID=your_chat_id_here
   ```

4. Перезапустите сервисы:
   ```bash
   sudo docker-compose restart celery-worker celery-beat
   ```

## 🗄️ Доступ к базе данных

```bash
# Подключение к PostgreSQL
sudo docker-compose exec postgres psql -U ssluser -d sslmonitor

# Полезные SQL команды:
# Посмотреть все домены
SELECT * FROM domains;

# Посмотреть последние проверки
SELECT * FROM ssl_checks ORDER BY checked_at DESC LIMIT 10;

# Статистика по домену
SELECT 
  d.name, 
  COUNT(s.id) as total_checks,
  MAX(s.checked_at) as last_check
FROM domains d
LEFT JOIN ssl_checks s ON d.id = s.domain_id
GROUP BY d.id, d.name;
```

## 🐛 Troubleshooting

### Проблема: Backend не запускается
```bash
# Проверьте логи
sudo docker-compose logs backend

# Пересоберите контейнер
sudo docker-compose up -d --build backend
```

### Проблема: База данных не подключается
```bash
# Проверьте статус PostgreSQL
sudo docker-compose ps postgres

# Проверьте логи
sudo docker-compose logs postgres

# Перезапустите
sudo docker-compose restart postgres
```

### Проблема: Celery worker не работает
```bash
# Проверьте Redis
sudo docker-compose ps redis
sudo docker-compose logs redis

# Перезапустите worker
sudo docker-compose restart celery-worker celery-beat
```

### Проблема: Фронтенд не загружается
```bash
# Проверьте Nginx
sudo docker-compose logs frontend

# Перезапустите
sudo docker-compose restart frontend
```

## 📈 Мониторинг производительности

### Просмотр использования ресурсов
```bash
sudo docker stats
```

### Очистка старых данных
Celery автоматически очищает записи старше 90 дней каждую ночь в 2:00 AM.

Ручная очистка:
```bash
sudo docker-compose exec postgres psql -U ssluser -d sslmonitor -c "
DELETE FROM ssl_checks 
WHERE checked_at < NOW() - INTERVAL '90 days';
"
```

## 🎯 Следующие шаги

1. ✅ Настройте Telegram уведомления
2. ✅ Добавьте свои домены через Dashboard или API
3. ✅ Настройте мониторинг (проверки выполняются каждый час автоматически)
4. ✅ Изучите API документацию: http://localhost:8000/docs
5. ✅ При готовности - деплой на Render.com (см. README.md)

## 🚀 Деплой в продакшен

См. подробные инструкции в `README.md` - раздел "Deployment to Render.com"

## 💡 Полезные ссылки

- **Frontend Dashboard**: http://localhost
- **API Docs (Swagger)**: http://localhost:8000/docs
- **API Docs (ReDoc)**: http://localhost:8000/redoc
- **API Health Check**: http://localhost:8000/health
- **GitHub Repository**: (add your repo link here)

## 🆘 Поддержка

Если возникли проблемы:
1. Проверьте логи: `sudo docker-compose logs`
2. Убедитесь, что все порты свободны (80, 8000, 5432, 6379)
3. Проверьте, что Docker daemon запущен: `sudo systemctl status docker`

---

**Готово!** Ваша SSL мониторинг платформа работает 🎉

Протестированные домены:
- ✅ google.com (SSL expires in 64 days - HEALTHY)
- ✅ github.com
- ✅ stackoverflow.com

Вы можете добавлять новые домены через веб-интерфейс или API!

