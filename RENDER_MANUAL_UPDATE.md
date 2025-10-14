# 🚨 RENDER MANUAL UPDATE - КРИТИЧНО!

## ПРОБЛЕМА
Render все еще использует GitHub вместо GitLab:
- ❌ **Текущий источник**: `https://github.com/vlamay/ssl-monitor`
- ✅ **Нужный источник**: `http://192.168.1.10/root/ssl-monitor-pro.git`

## РУЧНОЕ ИСПРАВЛЕНИЕ

### 1️⃣ ОТКРЫТЬ RENDER DASHBOARD
Перейти: https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg

### 2️⃣ ПЕРЕЙТИ В SETTINGS
- Нажать **Settings** в левом меню
- Выбрать **Build & Deploy**

### 3️⃣ ОБНОВИТЬ REPOSITORY
- Найти секцию **Repository**
- Нажать **Update Repository**
- Выбрать **Public Git Repository**
- Ввести URL: `http://192.168.1.10/root/ssl-monitor-pro.git`
- Branch: `main`
- Нажать **Save Changes**

### 4️⃣ ЗАПУСТИТЬ DEPLOYMENT
- Нажать **Manual Deploy** (справа вверху)
- Выбрать **Deploy latest commit**
- Дождаться завершения

## ПРОВЕРКА РЕЗУЛЬТАТА

### ✅ УСПЕШНОЕ ОБНОВЛЕНИЕ
В логах должно быть:
```
==> Cloning from http://192.168.1.10/root/ssl-monitor-pro.git
```

### ❌ ЕСЛИ НЕ РАБОТАЕТ
- Проверить доступность GitLab: `curl -I http://192.168.1.10`
- Попробовать через домен: `http://gitlab.trustforge.uk/root/ssl-monitor-pro.git`

## АЛЬТЕРНАТИВНЫЕ URL

Если IP не работает, попробовать:
1. `http://gitlab.trustforge.uk/root/ssl-monitor-pro.git`
2. `https://gitlab.trustforge.uk/root/ssl-monitor-pro.git` (если SSL настроен)

## РЕЗУЛЬТАТ
После успешного обновления:
- ✅ Render будет использовать GitLab
- ✅ Автоматические deployments из GitLab
- ✅ Полная интеграция CI/CD
- ✅ Решение проблемы с MimeText импортом

## МОНИТОРИНГ
- Dashboard: https://dashboard.render.com/web/srv-d3lbqje3jp1c73ej7csg
- Health: https://ssl-monitor-api.onrender.com/health
