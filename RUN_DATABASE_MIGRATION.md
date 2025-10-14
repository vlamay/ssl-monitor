# 🗄️ DATABASE MIGRATION - MANUAL STEPS

## ⚠️ **ВАЖНО: Выполняется вручную на Render Dashboard**

Автоматическая миграция через код невозможна по соображениям безопасности.
Нужно выполнить SQL скрипт вручную через Render Dashboard.

---

## 📋 **ИНСТРУКЦИЯ**

### **Шаг 1: Открыть Render Dashboard**
1. Перейти на https://dashboard.render.com
2. Найти PostgreSQL сервис: **ssl-monitor-db** (или ваше имя)
3. Нажать **Connect** → **External Connection**

### **Шаг 2: Подключиться через psql**

**Вариант A: Через Terminal (Linux/Mac)**
```bash
psql postgresql://ssl_admin:YOUR_PASSWORD@dpg-xxxxx.oregon-postgres.render.com:5432/ssl_monitor
```

**Вариант B: Через Render Shell**
1. В Render Dashboard → Database → **Shell** tab
2. Автоматически подключится к БД

### **Шаг 3: Запустить миграцию**

**Скопируйте и выполните весь SQL из файла:**
`backend/migrations/001_user_profiles.sql`

Или выполните прямо из файла:
```bash
# Если есть локальный доступ к файлу
\i /path/to/ssl-monitor-final/backend/migrations/001_user_profiles.sql

# Или скопируйте содержимое и вставьте в Shell
```

### **Шаг 4: Проверка**

После выполнения SQL проверьте что таблицы созданы:

```sql
-- Проверка таблиц
\dt user_profiles
\dt language_change_log

-- Должны вернуть:
-- Table "public.user_profiles"
-- Table "public.language_change_log"

-- Проверка индексов
\di idx_user_profiles_*

-- Проверка views
\dv language_distribution
\dv recent_language_changes

-- Тестовый запрос
SELECT * FROM language_distribution;
-- Должен вернуть пустой результат (пока нет пользователей)
```

### **Шаг 5: Готово!** ✅

Если все команды выполнились без ошибок - миграция завершена успешно!

---

## 🚨 **В СЛУЧАЕ ОШИБОК**

### **Ошибка: "relation already exists"**
```sql
-- Таблица уже существует, все в порядке
-- Можно пропустить или удалить и пересоздать:
DROP TABLE IF EXISTS language_change_log CASCADE;
DROP TABLE IF EXISTS user_profiles CASCADE;
-- Затем запустить миграцию заново
```

### **Ошибка: "permission denied"**
- Убедитесь что используете правильного пользователя (ssl_admin)
- Проверьте что подключены к правильной БД

---

## ✅ **АЛЬТЕРНАТИВА: Миграция через код (на Render)**

Render автоматически создаст таблицы при первом запуске, если они описаны в SQLAlchemy моделях.

Файл `backend/models/user_profile.py` уже содержит модели, поэтому:
- При первом запуске FastAPI на Render
- SQLAlchemy создаст таблицы автоматически
- Если использовать `Base.metadata.create_all(bind=engine)`

**НО**: Views и triggers не создадутся автоматически, нужен SQL скрипт.

---

## 📝 **БЫСТРАЯ МИГРАЦИЯ (если есть доступ к командной строке)**

```bash
# Один командой (замените на свой DATABASE_URL)
export DATABASE_URL="postgresql://ssl_admin:PASSWORD@dpg-xxx.oregon-postgres.render.com:5432/ssl_monitor"

psql $DATABASE_URL < backend/migrations/001_user_profiles.sql

# Проверка
psql $DATABASE_URL -c "\dt user_profiles"
```

---

**После успешной миграции переходите к деплою кода на Render!**
