# 🔗 CURSOR + GITLAB ИНТЕГРАЦИЯ

**Дата:** 13 октября 2025  
**Проект:** SSL Monitor Pro  
**GitLab:** http://192.168.1.10/root/ssl-monitor-pro  

---

## 🎯 ТЕКУЩИЙ СТАТУС

✅ **GitLab remote уже настроен!**
```
gitlab: http://root:glpat-6xB--zr0yzQzyeuFcxaMYG86MQp1OjEH.01.0w0bnoard@192.168.1.10/root/ssl-monitor-pro.git
origin: http://192.168.1.10/root/ssl-monitor-pro.git
```

---

## 🚀 СПОСОБЫ РАБОТЫ С GITLAB ИЗ CURSOR

### 1️⃣ **ЧЕРЕЗ CURSOR TERMINAL (рекомендуется)**

#### Основные команды:
```bash
cd /home/vmaidaniuk/Cursor/ssl-monitor-final

# Просмотр статуса
git status

# Добавить изменения
git add .

# Создать коммит
git commit -m "Описание изменений"

# Отправить в GitLab
git push gitlab main

# Получить изменения из GitLab
git pull gitlab main

# Переключиться на другую ветку
git checkout -b feature/new-feature
git push gitlab feature/new-feature
```

#### Работа с ветками:
```bash
# Создать новую ветку
git checkout -b feature/awesome-feature

# Переключиться между ветками
git checkout main
git checkout feature/awesome-feature

# Отправить ветку в GitLab
git push gitlab feature/awesome-feature

# Создать Merge Request (через GitLab UI)
```

### 2️⃣ **ЧЕРЕЗ CURSOR UI**

#### В Cursor:
1. **Source Control** (Ctrl+Shift+G)
2. **Changes** - просмотр изменений
3. **Commit** - создать коммит
4. **Push/Pull** - синхронизация

#### Настройка Git в Cursor:
```json
// В settings.json
{
  "git.defaultCloneDirectory": "/home/vmaidaniuk/Cursor",
  "git.enableSmartCommit": true,
  "git.confirmSync": false,
  "git.autofetch": true
}
```

### 3️⃣ **ЧЕРЕЗ GITLAB WEB UI**

#### Создание Merge Request:
1. Открыть: http://192.168.1.10/root/ssl-monitor-pro
2. **Merge Requests** → **New merge request**
3. Выбрать ветки
4. Заполнить описание
5. **Create merge request**

---

## 🔧 НАСТРОЙКА GITLAB RUNNER ДЛЯ CI/CD

### Установка GitLab Runner:
```bash
# Скачать GitLab Runner
curl -L --output /usr/local/bin/gitlab-runner https://gitlab-runner-downloads.s3.amazonaws.com/latest/binaries/gitlab-runner-linux-amd64

# Сделать исполняемым
sudo chmod +x /usr/local/bin/gitlab-runner

# Создать пользователя
sudo useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash

# Установить
sudo gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner

# Запустить
sudo gitlab-runner start
```

### Регистрация Runner:
```bash
sudo gitlab-runner register
```

**Параметры:**
```
GitLab instance URL: http://192.168.1.10/
Registration token: [получить из GitLab: Settings > CI/CD > Runners]
Description: Local Docker Runner
Tags: docker,local
Executor: docker
Default Docker image: python:3.12
```

### Проверка Runner:
```bash
# Статус
sudo gitlab-runner status

# Список runners
sudo gitlab-runner list
```

---

## 📋 WORKFLOW РАЗРАБОТКИ

### 1. **Создание новой функции:**
```bash
# 1. Создать ветку
git checkout -b feature/new-monitoring-feature

# 2. Разработать в Cursor
# (редактирование файлов)

# 3. Проверить изменения
git status
git diff

# 4. Добавить изменения
git add .

# 5. Создать коммит
git commit -m "feat: add new monitoring feature

- Added new SSL monitoring endpoint
- Updated dashboard UI
- Added tests for new functionality"

# 6. Отправить в GitLab
git push gitlab feature/new-monitoring-feature

# 7. Создать Merge Request через GitLab UI
```

### 2. **Исправление багов:**
```bash
# 1. Создать ветку для багфикса
git checkout -b bugfix/fix-ssl-certificate-parsing

# 2. Исправить баг
# (редактирование в Cursor)

# 3. Добавить тест
# (создать тест для исправления)

# 4. Коммит
git add .
git commit -m "fix: resolve SSL certificate parsing issue

- Fixed certificate validation logic
- Added error handling for malformed certificates
- Updated tests to cover edge cases

Fixes #123"

# 5. Push и MR
git push gitlab bugfix/fix-ssl-certificate-parsing
```

### 3. **Горячие фиксы:**
```bash
# 1. Создать hotfix ветку от main
git checkout main
git pull gitlab main
git checkout -b hotfix/critical-security-fix

# 2. Быстрое исправление
# (минимальные изменения)

# 3. Коммит
git commit -m "hotfix: critical security vulnerability

- Fixed XSS vulnerability in dashboard
- Updated input validation
- Immediate fix required

Security: HIGH PRIORITY"

# 4. Push и срочный MR
git push gitlab hotfix/critical-security-fix
```

---

## 🐳 DOCKER РАЗРАБОТКА

### Локальная разработка:
```bash
# Запуск dev окружения
docker-compose -f docker-compose.dev.yml up

# Или через Makefile
make dev-up
make dev-logs
make dev-down

# Запуск тестов
make test

# Линтинг
make lint
```

### CI/CD Pipeline:
```yaml
# .gitlab-ci.yml уже настроен
stages:
  - test
  - build
  - deploy

# Автоматически запустится при push
```

---

## 🔐 УПРАВЛЕНИЕ СЕКРЕТАМИ

### Environment Variables:
```bash
# Создать .env файл
cp env.example .env

# Отредактировать
nano .env

# НЕ коммитить .env в git!
echo ".env" >> .gitignore
```

### GitLab CI Variables:
1. GitLab → Settings → CI/CD → Variables
2. Добавить переменные:
   - `DATABASE_URL`
   - `REDIS_URL`
   - `SECRET_KEY`
   - `STRIPE_SECRET_KEY`
   - `TELEGRAM_BOT_TOKEN`

---

## 📊 МОНИТОРИНГ И ОТЛАДКА

### Логи CI/CD:
1. GitLab → CI/CD → Pipelines
2. Выбрать pipeline
3. Просмотр логов каждого job

### Локальная отладка:
```bash
# Запуск с отладкой
docker-compose -f docker-compose.dev.yml up --build

# Логи backend
docker-compose -f docker-compose.dev.yml logs backend

# Логи frontend
docker-compose -f docker-compose.dev.yml logs frontend

# Войти в контейнер
docker-compose -f docker-compose.dev.yml exec backend bash
```

### Тестирование:
```bash
# Unit тесты
make test-unit

# Integration тесты
make test-integration

# E2E тесты
make test-e2e

# Все тесты
make test
```

---

## 🎯 ЛУЧШИЕ ПРАКТИКИ

### 1. **Commit Messages:**
```
feat: add new SSL monitoring endpoint
fix: resolve certificate validation bug
docs: update API documentation
style: format code according to standards
refactor: improve error handling logic
test: add tests for new functionality
chore: update dependencies
```

### 2. **Branch Naming:**
```
feature/ssl-certificate-monitoring
bugfix/dashboard-loading-issue
hotfix/security-vulnerability
docs/api-documentation-update
refactor/database-connection-pool
```

### 3. **Code Review:**
- Создавать MR для всех изменений
- Добавлять описание изменений
- Указывать связанные issues
- Запрашивать review у коллег
- Проверять CI/CD pipeline

### 4. **Testing:**
- Покрывать новый код тестами
- Запускать тесты перед push
- Использовать linting и formatting
- Проверять security vulnerabilities

---

## 🚨 TROUBLESHOOTING

### Проблемы с Git:
```bash
# Конфликты merge
git status
git diff
git mergetool

# Отмена изменений
git checkout -- filename
git reset --hard HEAD

# Очистка веток
git branch -d feature/old-feature
git push gitlab --delete feature/old-feature
```

### Проблемы с Docker:
```bash
# Пересборка образов
docker-compose -f docker-compose.dev.yml build --no-cache

# Очистка контейнеров
docker-compose -f docker-compose.dev.yml down -v
docker system prune -a

# Проверка логов
docker-compose -f docker-compose.dev.yml logs -f
```

### Проблемы с CI/CD:
```bash
# Локальный запуск pipeline
gitlab-runner exec docker test

# Отладка runner
sudo gitlab-runner --debug run
```

---

## 📚 ПОЛЕЗНЫЕ КОМАНДЫ

### Git Aliases:
```bash
# Добавить в ~/.gitconfig
[alias]
    co = checkout
    br = branch
    ci = commit
    st = status
    unstage = reset HEAD --
    last = log -1 HEAD
    visual = !gitk
    lg = log --oneline --graph --all
```

### Cursor Shortcuts:
```
Ctrl+Shift+G  - Source Control
Ctrl+Shift+P  - Command Palette
Ctrl+`        - Terminal
F1            - Quick Actions
Ctrl+Shift+F  - Global Search
```

### GitLab URLs:
```
Проект:       http://192.168.1.10/root/ssl-monitor-pro
Issues:       http://192.168.1.10/root/ssl-monitor-pro/-/issues
MR:           http://192.168.1.10/root/ssl-monitor-pro/-/merge_requests
CI/CD:        http://192.168.1.10/root/ssl-monitor-pro/-/pipelines
Settings:     http://192.168.1.10/root/ssl-monitor-pro/-/settings
```

---

## 🎉 ГОТОВО К РАБОТЕ!

### Быстрый старт:
```bash
cd /home/vmaidaniuk/Cursor/ssl-monitor-final

# Проверить статус
git status

# Создать новую ветку
git checkout -b feature/my-new-feature

# Разработать в Cursor
# (редактирование файлов)

# Коммит и push
git add .
git commit -m "feat: my awesome new feature"
git push gitlab feature/my-new-feature

# Создать MR через GitLab UI
```

### Следующие шаги:
1. ✅ GitLab remote настроен
2. ⏳ Установить GitLab Runner
3. ⏳ Настроить CI/CD Variables
4. ⏳ Создать первый MR
5. ⏳ Запустить первый pipeline

---

**Создано:** 13 октября 2025  
**Автор:** AI Agent (Claude Sonnet 4.5)  
**Проект:** SSL Monitor Pro - Cursor + GitLab Integration
