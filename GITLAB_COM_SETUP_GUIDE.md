# GitLab.com Setup Guide

## 🎯 Новая стратегия: GitLab.com вместо синхронизации

### ✅ Преимущества GitLab.com
- **Официальная поддержка Render** - 100% совместимость
- **Нет проблем с доступом** - публичный GitLab.com
- **Полная функциональность** - все возможности GitLab
- **Простота настройки** - не нужна синхронизация

### 📋 План действий

#### 1️⃣ Создать проект на GitLab.com
1. Зайти на https://gitlab.com/sre.engineer.vm
2. Нажать "New project"
3. Выбрать "Import project"
4. Выбрать "GitHub"
5. Подключить GitHub аккаунт
6. Импортировать репозиторий `vlamay/ssl-monitor`

#### 2️⃣ Настроить проект
- **Название:** `ssl-monitor-pro`
- **Описание:** `SSL Monitor Pro - Production Ready`
- **Видимость:** Public
- **Namespace:** `sre.engineer.vm`

#### 3️⃣ Обновить Render
- **Repository URL:** `https://gitlab.com/sre.engineer.vm/ssl-monitor-pro.git`
- **Branch:** `main`
- **Root Directory:** (пустой)
- **Build Command:** `pip install -r backend/requirements.txt`
- **Start Command:** `cd backend && python -m uvicorn main:app --host 0.0.0.0 --port 10000`

#### 4️⃣ Протестировать деплой
- Сохранить настройки в Render
- Запустить Manual Deploy
- Проверить логи деплоя
- Проверить работоспособность

### 🔧 Технические детали

#### GitLab.com URL формат
```
https://gitlab.com/USERNAME/PROJECT.git
```

#### Render совместимость
- ✅ HTTPS URL поддерживается
- ✅ SSH URL поддерживается  
- ✅ Deploy Tokens поддерживаются
- ✅ Webhooks поддерживаются

### 📖 Пошаговая инструкция

#### Шаг 1: Импорт из GitHub
1. **Зайти в GitLab.com:** https://gitlab.com/sre.engineer.vm
2. **New project** → **Import project**
3. **GitHub** → **Connect your GitHub account**
4. **Выбрать репозиторий:** `vlamay/ssl-monitor`
5. **Project name:** `ssl-monitor-pro`
6. **Visibility:** Public
7. **Import project**

#### Шаг 2: Обновить Render
1. **Render Dashboard** → **Ваш сервис**
2. **Settings** → **Repository**
3. **Repository URL:** `https://gitlab.com/sre.engineer.vm/ssl-monitor-pro.git`
4. **Branch:** `main`
5. **Save Changes**
6. **Manual Deploy**

#### Шаг 3: Проверка
1. **Проверить деплой:** Render Dashboard → Deployments
2. **Проверить логи:** View logs
3. **Проверить работоспособность:** Health check endpoint
4. **Smoke tests:** Запустить тесты

### 🚀 Преимущества нового подхода

#### Простота
- Один репозиторий вместо синхронизации
- Прямое подключение Render к GitLab.com
- Нет дополнительных настроек

#### Надежность  
- GitLab.com стабилен и быстр
- Render официально поддерживает GitLab.com
- Нет проблем с доступом

#### Функциональность
- Полный GitLab CI/CD
- Issues и Merge Requests
- Wiki и Pages
- Container Registry

### 🔍 Альтернативные варианты

#### Вариант 1: Прямой импорт (рекомендуется)
- Импортировать из GitHub в GitLab.com
- Обновить Render на GitLab.com URL

#### Вариант 2: Создание с нуля
- Создать пустой проект в GitLab.com
- Загрузить код локально
- Push в GitLab.com

#### Вариант 3: Mirror (для будущего)
- Настроить mirror между GitHub и GitLab.com
- Автоматическая синхронизация

### 📞 Поддержка

Если что-то не работает:
1. Проверить права доступа к GitLab.com
2. Проверить настройки Render
3. Проверить логи деплоя
4. Проверить health check

### 🎯 Следующие шаги

1. ✅ Создать GitLab.com профиль (готово)
2. 🔄 Импортировать проект из GitHub
3. 🔄 Обновить Render на GitLab.com URL
4. 🔄 Протестировать деплой
5. 🔄 Запустить smoke tests
