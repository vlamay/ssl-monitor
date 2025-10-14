# 🔐 GitHub Secrets Setup Guide

## 🚀 **QUICK SETUP (5 minutes)**

### **1. Перейди в GitHub Repository Settings**
```
https://github.com/vlamay/ssl-monitor/settings/secrets/actions
```

### **2. Добавь эти secrets:**

#### **🔑 ОБЯЗАТЕЛЬНЫЕ SECRETS:**

**Telegram Bot (для уведомлений):**
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=123456789
```

**Render API (для деплоя):**
```
RENDER_API_KEY=rnd_xxxxxxxxxxxxx
RENDER_SERVICE_ID=srv-xxxxxxxxxxxxx
```

#### **🔧 ОПЦИОНАЛЬНЫЕ SECRETS:**

**Database (если не в Render):**
```
DATABASE_URL=postgresql://user:pass@host:5432/db
UPSTASH_REDIS_REST_URL=https://xxx.upstash.io
UPSTASH_REDIS_REST_TOKEN=your_token
```

**Security:**
```
SECRET_KEY=your_secret_key_here
```

---

## 📱 **КАК ПОЛУЧИТЬ TELEGRAM CREDENTIALS:**

### **1. Создай Telegram Bot:**
1. Открой Telegram
2. Найди @BotFather
3. Отправь: `/newbot`
4. Название: `SSL Monitor Alerts`
5. Username: `ssl_monitor_alerts_bot`
6. **Скопируй токен** (выглядит как `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)

### **2. Получи CHAT_ID:**
1. Найди @userinfobot
2. Отправь любое сообщение
3. **Скопируй свой ID** (выглядит как `123456789`)

---

## 🚀 **КАК ПОЛУЧИТЬ RENDER CREDENTIALS:**

### **1. Получи API Key:**
1. Иди на https://dashboard.render.com/
2. Account Settings → API Keys
3. Create API Key
4. Name: `GitHub Actions`
5. **Скопируй token** (начинается с `rnd_`)

### **2. Получи Service ID:**
1. Открой свой сервис в Render
2. URL будет: `https://dashboard.render.com/web/srv-XXXXX`
3. **srv-XXXXX** это и есть SERVICE_ID

---

## ✅ **ПРОВЕРКА НАСТРОЙКИ:**

### **1. Добавь secrets в GitHub:**
```
Repository → Settings → Secrets and variables → Actions → New repository secret
```

### **2. Тестовый деплой:**
```bash
# Commit изменения
git add .
git commit -m "Fix CI/CD and add secrets"
git push origin main

# Проверь GitHub Actions
# https://github.com/vlamay/ssl-monitor/actions
```

### **3. Проверь уведомления:**
- Telegram должен получить уведомление о деплое
- Render должен начать новый деплой

---

## 🚨 **ЕСЛИ ЧТО-ТО НЕ РАБОТАЕТ:**

### **Проблема: Тесты не проходят**
```bash
# Решение: Тесты уже исправлены, должны проходить
```

### **Проблема: Missing secrets**
```bash
# Решение: Добавь все обязательные secrets выше
```

### **Проблема: Telegram не работает**
```bash
# Решение: Проверь токен и chat_id
curl -X GET "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe"
```

### **Проблема: Render не деплоит**
```bash
# Решение: Проверь API key и service ID
curl -H "Authorization: Bearer <YOUR_API_KEY>" https://api.render.com/v1/services
```

---

## 🎯 **ГОТОВО К ДЕПЛОЮ!**

После настройки secrets:
1. ✅ Push в main branch
2. ✅ GitHub Actions запустится автоматически
3. ✅ Деплой в Render начнется
4. ✅ Telegram получит уведомление

**Timeline: 5 минут настройка + 10 минут деплой = 15 минут до production!**
