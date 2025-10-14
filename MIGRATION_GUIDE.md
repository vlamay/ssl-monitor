# 🔄 SSL Monitor Pro: Полная миграция GitHub → GitLab

## 📋 Оглавление
1. [Текущая ситуация](#текущая-ситуация)
2. [План миграции](#план-миграции)
3. [Подготовка](#подготовка)
4. [Миграция кода](#миграция-кода)
5. [Настройка внешних сервисов](#настройка-внешних-сервисов)
6. [Тестирование](#тестирование)
7. [Отключение GitHub](#отключение-github)
8. [Чеклист](#чеклист)

---

## 📊 Текущая ситуация

### ✅ Что работает сейчас (GitHub):
```
GitHub Repository: root/ssl-monitor-pro
├── Backend deployed → Render.com (auto-deploy from GitHub)
├── Frontend deployed → Cloudflare Pages (auto-deploy from GitHub)
├── GitLab CI/CD → CI/CD pipeline активен
├── Webhooks → GitHub webhooks для деплоя
└── Production → Живая система с пользователями
```

### 🎯 Цель миграции (GitLab):
```
GitLab Repository: root/ssl-monitor-pro
├── Backend deployed → Render.com (auto-deploy from GitLab)
├── Frontend deployed → Cloudflare Pages (auto-deploy from GitLab)
├── GitLab CI/CD → Pipeline активен
├── Webhooks → GitLab webhooks для деплоя
└── Production → Плавный переход без downtime
```

---

## 📝 План миграции (2-3 часа работы)

### Phase 1: Подготовка (30 минут)
- [ ] Backup текущего состояния GitHub
- [ ] Проверка GitLab репозитория
- [ ] Подготовка credentials
- [ ] Документирование текущих настроек

### Phase 2: GitLab настройка (45 минут)
- [ ] Настройка CI/CD Variables в GitLab
- [ ] Проверка .gitlab-ci.yml
- [ ] Тестовый запуск pipeline
- [ ] Настройка Protected Branches

### Phase 3: Внешние сервисы (60 минут)
- [ ] Render.com - переключение на GitLab
- [ ] Cloudflare Pages - переключение на GitLab
- [ ] Stripe Webhooks - обновление URLs
- [ ] Telegram Bot - обновление URLs
- [ ] Slack - обновление URLs

### Phase 4: Тестирование (30 минут)
- [ ] Проверка CI/CD pipeline
- [ ] Тестовый деплой
- [ ] Smoke tests production
- [ ] Rollback план

### Phase 5: Переключение (15 минут)
- [ ] Финальный деплой с GitLab
- [ ] Отключение GitHub auto-deploy
- [ ] Архивация GitHub репозитория

---

## 🔧 PHASE 1: Подготовка

### Задача 1.1: Backup GitHub настроек

**Что сохранить:**

```bash
# 1. Сохранить список GitHub Secrets
echo "📝 GitHub Secrets Backup"
echo "========================"
echo "RENDER_DEPLOY_HOOK_URL"
echo "CLOUDFLARE_API_TOKEN"
echo "STRIPE_SECRET_KEY"
echo "STRIPE_WEBHOOK_SECRET"
echo "TELEGRAM_BOT_TOKEN"
echo "SLACK_WEBHOOK_URL"
echo "SENTRY_DSN"
# ... и другие

# 2. Сохранить GitLab CI/CD workflows
mkdir -p backup/github-actions
cp -r .github/workflows backup/github-actions/

# 3. Сохранить текущие URLs и настройки
cat > backup/github-config.txt <<EOF
# GitHub Repository Info
Repo: https://192.168.1.10/root/ssl-monitor-pro
SSH: http://192.168.1.10/root/ssl-monitor-pro.git

# Render.com
Backend URL: https://ssl-monitor-api.onrender.com
Deploy Hook: [сохранить из GitHub Secrets]

# Cloudflare Pages
Frontend URL: https://cloudsre.xyz
Project: ssl-monitor-pro

# Webhooks
Stripe: https://ssl-monitor-api.onrender.com/api/v1/stripe/webhook
Telegram: https://ssl-monitor-api.onrender.com/api/v1/telegram/webhook
Slack: https://ssl-monitor-api.onrender.com/api/v1/slack/webhook
EOF
```

### Задача 1.2: Проверка GitLab репозитория

```bash
# 1. Проверить текущий remote
git remote -v

# Должно быть:
# gitlab  http://root:TOKEN@192.168.1.10/root/ssl-monitor-pro.git (fetch)
# gitlab  http://root:TOKEN@192.168.1.10/root/ssl-monitor-pro.git (push)

# 2. Проверить синхронизацию
git fetch gitlab
git status

# 3. Проверить что все файлы на месте
ls -la
```

### Задача 1.3: Подготовка credentials

**Создать файл для хранения credentials:**

```bash
# 1. Создать безопасный файл
touch .migration-secrets
chmod 600 .migration-secrets

# 2. Заполнить всеми secrets из GitHub
# См. .migration-secrets.template для примера
```

---

## ⚙️ PHASE 2: GitLab настройка

### Задача 2.1: Настройка CI/CD Variables в GitLab

**Где:** GitLab → Settings → CI/CD → Variables

**Команда для массового добавления:**

```bash
# 1. Проверить что .migration-secrets заполнен
cat .migration-secrets

# 2. Запустить скрипт
./scripts/setup-gitlab-vars.sh

# 3. Проверить в GitLab UI
# GitLab → Settings → CI/CD → Variables
```

### Задача 2.2: Проверка .gitlab-ci.yml

**Проверить что все stages корректны:**

```bash
# Проверить синтаксис
cat .gitlab-ci.yml

# Проверить что используются правильные переменные
grep -E '\$[A-Z_]+' .gitlab-ci.yml

# Должны быть все переменные из setup-gitlab-vars.sh
```

**Тестовый запуск pipeline:**

```bash
# 1. Создать тестовую ветку
git checkout -b test-gitlab-pipeline

# 2. Закоммитить изменение
echo "# Test pipeline" >> README.md
git add README.md
git commit -m "test: trigger GitLab pipeline"

# 3. Push в GitLab
git push gitlab test-gitlab-pipeline

# 4. Проверить pipeline в GitLab
# GitLab → CI/CD → Pipelines
# Должен запуститься pipeline с 4 stages: test, build, deploy, notify

# 5. Если успешно - удалить тестовую ветку
git checkout main
git branch -D test-gitlab-pipeline
git push gitlab --delete test-gitlab-pipeline
```

### Задача 2.3: Настройка Protected Branches

**В GitLab UI:**

1. Settings → Repository → Protected Branches
2. Protect branch: `main`
3. Allowed to merge: `Maintainers`
4. Allowed to push: `No one`
5. Allowed to force push: ❌ Disabled

---

## 🔌 PHASE 3: Настройка внешних сервисов

### Задача 3.1: Render.com - переключение на GitLab

**🎯 Цель:** Перенаправить Render.com деплой с GitHub на GitLab

**Опция A: Через Render.com UI (рекомендуется)**

1. **Зайти в Render.com Dashboard:**
   - https://dashboard.render.com
   - Найти сервис: `ssl-monitor-api`

2. **Settings → Build & Deploy:**
   ```
   Текущее (GitHub):
   Repository: 192.168.1.10/root/ssl-monitor-pro
   Branch: main
   Auto-Deploy: Yes
   
   Изменить на (GitLab):
   Repository: MANUAL - мы будем использовать Deploy Hook
   Branch: main
   Auto-Deploy: Via GitLab CI/CD
   ```

3. **Получить Deploy Hook URL:**
   - Settings → Deploy Hook
   - Copy URL: `https://api.render.com/deploy/srv-xxxxx?key=xxxxx`
   - Сохранить в GitLab Variables как `RENDER_DEPLOY_HOOK_URL`

4. **Отключить GitHub Auto-Deploy:**
   - Settings → Build & Deploy
   - Auto-Deploy: **Disabled**
   - Manual Deploy Only: **Enabled**

**Тестирование:**

```bash
# Тест деплоя через Deploy Hook
curl -X POST https://api.render.com/deploy/srv-xxxxx?key=xxxxx

# Проверить статус в Render Dashboard
# Должен начаться новый deploy
```

---

### Задача 3.2: Cloudflare Pages - переключение на GitLab

**🎯 Цель:** Перенаправить Cloudflare Pages деплой с GitHub на GitLab

**Метод 1: Прямая интеграция GitLab (если доступна)**

1. **Cloudflare Dashboard:**
   - Pages → ssl-monitor-pro → Settings
   - Build Configuration

2. **Disconnet GitHub:**
   - Source → Disconnect GitHub

3. **Connect GitLab:**
   - Source → Connect to Git
   - Select: GitLab
   - Repository: `root/ssl-monitor-pro`
   - Branch: `main`
   - Build command: `npm run build`
   - Build output directory: `frontend-modern/dist`

**Метод 2: Direct Upload через GitLab CI/CD (если GitLab интеграция недоступна)**

```yaml
# В .gitlab-ci.yml уже есть:
deploy-frontend:
  stage: deploy
  image: node:18-alpine
  before_script:
    - npm install -g wrangler
  script:
    - cd frontend-modern
    - npm ci
    - npm run build
    - npx wrangler pages publish dist --project-name=ssl-monitor-pro
  only:
    - main
  when: manual
```

**Настройка Wrangler:**

```bash
# 1. Создать Cloudflare API Token
# Cloudflare → My Profile → API Tokens → Create Token
# Template: "Edit Cloudflare Workers"
# Permissions: Account.Cloudflare Pages:Edit

# 2. Добавить в GitLab Variables
# CLOUDFLARE_API_TOKEN = your-token
# CLOUDFLARE_ACCOUNT_ID = your-account-id

# 3. Проверить деплой
git commit --allow-empty -m "test: trigger Cloudflare deploy"
git push gitlab main

# В GitLab Pipeline → Manual Jobs → deploy-frontend → Run
```

---

### Задача 3.3: Stripe Webhooks - обновление URLs

**🎯 Цель:** Webhooks продолжают работать (URLs не меняются)

**Проверка:**

```bash
# Stripe Webhooks URLs НЕ меняются, т.к. они указывают на Render.com
# https://ssl-monitor-api.onrender.com/api/v1/stripe/webhook

# Проверить что webhook endpoint работает
curl https://ssl-monitor-api.onrender.com/api/v1/stripe/webhook
# Должен вернуть 405 Method Not Allowed (это OK, т.к. GET не разрешен)
```

**Если нужно обновить:**

1. **Stripe Dashboard:**
   - Developers → Webhooks
   - Найти webhook для SSL Monitor Pro
   - Endpoint URL: `https://ssl-monitor-api.onrender.com/api/v1/stripe/webhook`
   - Events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`

2. **Проверить Webhook Secret:**
   - Copy Signing Secret
   - Обновить в GitLab Variables: `STRIPE_WEBHOOK_SECRET`

**Тестирование:**

```bash
# Отправить тестовый webhook из Stripe Dashboard
# Stripe → Developers → Webhooks → Send test webhook
# Event: checkout.session.completed
```

---

### Задача 3.4: Telegram Bot - обновление URLs

**🎯 Цель:** Telegram webhook продолжает работать

**Проверка webhook URL:**

```bash
# Проверить текущий webhook
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"

# Должен вернуть:
# {
#   "url": "https://ssl-monitor-api.onrender.com/api/v1/telegram/webhook",
#   "has_custom_certificate": false,
#   "pending_update_count": 0
# }
```

**Если нужно обновить:**

```bash
# Установить webhook (если не установлен)
curl -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
  -d "url=https://ssl-monitor-api.onrender.com/api/v1/telegram/webhook"

# Проверить
curl "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/getWebhookInfo"
```

**Тестирование:**

```bash
# Отправить тестовое сообщение боту в Telegram
# /start
# /status
# /help

# Проверить что бот отвечает
```

---

### Задача 3.5: Slack - обновление URLs

**🎯 Цель:** Slack webhooks продолжают работать

**Проверка:**

```bash
# Тестовое уведомление в Slack
curl -X POST $SLACK_WEBHOOK_URL \
  -H 'Content-Type: application/json' \
  -d '{
    "text": "🧪 Test: GitLab Migration Complete",
    "blocks": [
      {
        "type": "section",
        "text": {
          "type": "mrkdwn",
          "text": "*SSL Monitor Pro* - GitLab Migration Test\n✅ All systems operational"
        }
      }
    ]
  }'

# Проверить что сообщение пришло в Slack
```

**Slack App настройки:**

1. **Slack API Dashboard:**
   - https://api.slack.com/apps
   - Найти SSL Monitor Pro app

2. **Event Subscriptions:**
   - Request URL: `https://ssl-monitor-api.onrender.com/api/v1/slack/events`
   - Verified: ✅

3. **Slash Commands:**
   - `/ssl-status` → `https://ssl-monitor-api.onrender.com/api/v1/slack/commands`

---

## 🧪 PHASE 4: Тестирование

### Задача 4.1: Проверка GitLab CI/CD Pipeline

**Полный тест pipeline:**

```bash
# 1. Создать feature ветку
git checkout -b test/full-pipeline

# 2. Сделать изменение
echo "# Test full pipeline" >> TESTING.md
git add TESTING.md
git commit -m "test: full CI/CD pipeline test"

# 3. Push в GitLab
git push gitlab test/full-pipeline

# 4. Проверить в GitLab:
# - CI/CD → Pipelines
# - Должны пройти все stages:
#   ✅ test (backend-tests, frontend-tests, security-scan)
#   ✅ build (build-backend, build-frontend)
#   ✅ deploy (deploy-production, deploy-frontend) - MANUAL
#   ✅ notify (notify-slack, notify-telegram)

# 5. Если все ОК - merge в main
git checkout main
git merge test/full-pipeline
git push gitlab main
```

### Задача 4.2: Тестовый деплой

**Ручной деплой через GitLab:**

```bash
# 1. В GitLab Pipeline
# CI/CD → Pipelines → Latest → deploy-production → Manual Job → Run

# 2. Ждать завершения деплоя

# 3. Проверить что backend обновился
curl https://ssl-monitor-api.onrender.com/health

# Должен вернуть:
# {
#   "status": "healthy",
#   "timestamp": 1697219858,
#   "checks": {
#     "database": "ok",
#     "redis": "ok",
#     "ssl_checker": "ok"
#   }
# }

# 4. Проверить frontend
curl https://cloudsre.xyz
# Должен вернуть 200 OK
```

### Задача 4.3: Smoke Tests Production

**Критические проверки:**

```bash
# Запустить smoke tests
./scripts/smoke-tests.sh

# Должны пройти все тесты:
# ✅ Backend Health Check
# ✅ API Documentation
# ✅ Frontend Homepage
# ✅ Database Connection
# ✅ Redis Connection
# ✅ SSL Checker Service
# ✅ Stripe Webhook Endpoint
# ✅ Telegram Webhook Endpoint
# ✅ Slack Webhook Endpoint
# ✅ Frontend Static Assets
# ✅ API Response Time
# ✅ Frontend Response Time
# ✅ HTTPS Certificate
# ✅ Database Migration Status
```

### Задача 4.4: Rollback Plan

**Если что-то пошло не так:**

```bash
# Запустить rollback
./scripts/rollback-to-github.sh

# Следуйте инструкциям в скрипте
# Это вернет систему к GitHub
```

---

## ✂️ PHASE 5: Отключение GitHub

### Задача 5.1: Финальный деплой с GitLab

**После успешных smoke tests:**

```bash
# 1. Убедиться что все работает
./scripts/smoke-tests.sh

# 2. Создать финальный release
git checkout main
git tag -a v1.0.0-gitlab -m "Release: Full migration to GitLab"
git push gitlab main --tags

# 3. Запустить финальный deploy через GitLab
# GitLab → CI/CD → Pipelines → Run Pipeline
# Branch: main
# → deploy-production → Run

# 4. Ждать завершения и проверить
./scripts/smoke-tests.sh
```

### Задача 5.2: Отключение GitHub Auto-Deploy

**Render.com:**

```bash
# Вручную в Render Dashboard:
# 1. Зайти в ssl-monitor-api service
# 2. Settings → Build & Deploy
# 3. Auto-Deploy: Disabled ✅
# 4. Manual Deploy Only: Enabled ✅
```

**Cloudflare Pages:**

```bash
# Вручную в Cloudflare Dashboard:
# 1. Pages → ssl-monitor-pro
# 2. Settings → Build & Deploy
# 3. Disconnect GitHub ✅
# 4. (GitLab уже подключен через CI/CD)
```

### Задача 5.3: Архивация GitHub Repository

**⚠️ НЕ УДАЛЯТЬ СРАЗУ! Архивировать на 30 дней**

```bash
# 1. В GitHub Repository Settings:
# Settings → Options → Danger Zone → Archive this repository

# ИЛИ через GitHub CLI:
gh repo archive root/ssl-monitor-pro

# 2. Создать финальный backup
git clone http://192.168.1.10/root/ssl-monitor-pro.git backup-github-ssl-monitor
tar -czf backup-github-ssl-monitor-$(date +%Y%m%d).tar.gz backup-github-ssl-monitor/

# 3. Сохранить backup в безопасное место
# - External HDD
# - Cloud storage (Google Drive, Dropbox)
# - NAS storage

# 4. Добавить README в GitHub repo
cat > backup-github-ssl-monitor/ARCHIVED.md <<EOF
# ⚠️ ARCHIVED REPOSITORY

This repository has been migrated to GitLab.

**New Location:**
- GitLab: http://192.168.1.10/root/ssl-monitor-pro
- Production: https://cloudsre.xyz

**Migration Date:** $(date +%Y-%m-%d)

**Reason:** Full migration to self-hosted GitLab for better control and CI/CD

**Backup:** This is a read-only archive for reference purposes.

---

For any questions, contact: your-email@example.com
EOF

git -C backup-github-ssl-monitor add ARCHIVED.md
git -C backup-github-ssl-monitor commit -m "docs: mark repository as archived"
git -C backup-github-ssl-monitor push origin main
```

### Задача 5.4: Обновление документации

**Обновить все ссылки на GitHub → GitLab:**

```bash
# Запустить скрипт обновления ссылок
./scripts/update-links.sh

# Проверить изменения
git diff

# Закоммитить
git add .
git commit -m "docs: update all GitHub links to GitLab"
git push gitlab main
```

---

## ✅ ПОЛНЫЙ ЧЕКЛИСТ МИГРАЦИИ

### Pre-Migration Checklist

- [ ] **Backup создан**
  - [ ] GitHub repo склонирован локально
  - [ ] GitLab CI/CD workflows сохранены
  - [ ] Все secrets записаны в `.migration-secrets`
  - [ ] URLs и настройки задокументированы

- [ ] **GitLab готов**
  - [ ] Репозиторий создан в GitLab
  - [ ] Git remote настроен
  - [ ] Код синхронизирован с GitHub
  - [ ] `.gitlab-ci.yml` проверен

- [ ] **Credentials готовы**
  - [ ] Render.com API key
  - [ ] Cloudflare API token
  - [ ] Все environment variables собраны
  - [ ] GitLab access token получен

---

### GitLab Setup Checklist

- [ ] **CI/CD Variables настроены**
  - [ ] `./scripts/setup-gitlab-vars.sh` запущен
  - [ ] Все 30+ переменных добавлены в GitLab
  - [ ] Проверены в GitLab UI (Settings → CI/CD → Variables)
  - [ ] Sensitive переменные помечены как masked

- [ ] **Pipeline тестирование**
  - [ ] Тестовая ветка создана
  - [ ] Pipeline запустился успешно
  - [ ] Все stages прошли: test, build, deploy, notify
  - [ ] Docker images собрались и загрузились в Registry

- [ ] **Protected Branches**
  - [ ] Branch `main` защищен
  - [ ] Merge только для Maintainers
  - [ ] Push запрещен напрямую
  - [ ] Force push отключен

---

### External Services Checklist

- [ ] **Render.com**
  - [ ] GitHub auto-deploy отключен
  - [ ] Deploy Hook URL получен и добавлен в GitLab
  - [ ] Тестовый deploy через webhook работает
  - [ ] Environment variables проверены
  - [ ] Health check endpoint работает

- [ ] **Cloudflare Pages**
  - [ ] GitHub disconnected (если используете Direct Upload)
  - [ ] Wrangler настроен в GitLab CI/CD
  - [ ] API token добавлен в GitLab Variables
  - [ ] Тестовый deploy работает
  - [ ] Custom domain работает (cloudsre.xyz)

- [ ] **Stripe**
  - [ ] Webhooks URLs проверены (не меняются)
  - [ ] Webhook endpoint работает
  - [ ] Signing secret актуален
  - [ ] Тестовый webhook отправлен и обработан

- [ ] **Telegram**
  - [ ] Webhook URL проверен
  - [ ] Бот отвечает на команды
  - [ ] Уведомления работают
  - [ ] Bot token в GitLab Variables

- [ ] **Slack**
  - [ ] Webhook URL работает
  - [ ] Тестовое уведомление отправлено
  - [ ] Event subscriptions проверены
  - [ ] Slash commands работают

- [ ] **Sentry**
  - [ ] DSN в GitLab Variables
  - [ ] Error tracking работает
  - [ ] Releases настроены на GitLab
  - [ ] Source maps загружаются

---

### Testing Checklist

- [ ] **Pipeline Tests**
  - [ ] Backend tests проходят
  - [ ] Frontend tests проходят
  - [ ] Security scanning работает
  - [ ] Coverage >70%

- [ ] **Smoke Tests**
  - [ ] `./scripts/smoke-tests.sh` запущен
  - [ ] Backend health check: ✅
  - [ ] Frontend доступен: ✅
  - [ ] Database connected: ✅
  - [ ] Redis connected: ✅
  - [ ] All webhooks work: ✅

- [ ] **End-to-End Tests**
  - [ ] User registration работает
  - [ ] Login работает
  - [ ] Domain добавление работает
  - [ ] SSL check работает
  - [ ] Notifications отправляются
  - [ ] Payments работают (Stripe test mode)

- [ ] **Performance Tests**
  - [ ] API response time <200ms
  - [ ] Frontend load time <2s
  - [ ] SSL check <10s
  - [ ] No errors in browser console
  - [ ] No errors in Sentry

---

### Production Deployment Checklist

- [ ] **Pre-Deploy**
  - [ ] All smoke tests passed
  - [ ] All environment variables set
  - [ ] Database migrations ready
  - [ ] Rollback plan documented

- [ ] **Deploy**
  - [ ] GitLab Pipeline triggered
  - [ ] All stages completed successfully
  - [ ] Backend deployed to Render
  - [ ] Frontend deployed to Cloudflare
  - [ ] Health checks passing

- [ ] **Post-Deploy**
  - [ ] Smoke tests run again
  - [ ] User notifications sent
  - [ ] Monitoring active (Sentry, Prometheus)
  - [ ] No critical errors in logs

- [ ] **Verification**
  - [ ] Production URL works: https://cloudsre.xyz
  - [ ] API works: https://ssl-monitor-api.onrender.com
  - [ ] User login works
  - [ ] SSL monitoring works
  - [ ] Payments work
  - [ ] All integrations work (Telegram, Slack, Stripe)

---

### GitHub Shutdown Checklist

- [ ] **Pre-Shutdown**
  - [ ] GitLab fully operational for 7+ days
  - [ ] Zero critical issues
  - [ ] All users migrated
  - [ ] All data migrated

- [ ] **Disable GitHub**
  - [ ] GitHub auto-deploy disabled on Render
  - [ ] GitHub disconnected from Cloudflare
  - [ ] GitLab CI/CD workflows disabled
  - [ ] GitHub webhooks disabled

- [ ] **Archive GitHub**
  - [ ] Full backup created
  - [ ] Backup stored securely (3 locations)
  - [ ] ARCHIVED.md added to GitHub repo
  - [ ] Repository marked as archived
  - [ ] Team notified of archive

- [ ] **Documentation**
  - [ ] All links updated (GitHub → GitLab)
  - [ ] README updated
  - [ ] CONTRIBUTING updated
  - [ ] Wiki updated (if exists)

---

## 📊 ПОСТМИГРАЦИОННЫЙ МОНИТОРИНГ

### Week 1 после миграции

**Ежедневные проверки:**

```bash
#!/bin/bash
# scripts/daily-health-check.sh

echo "📊 Daily Health Check - $(date)"
echo "================================"

# 1. GitLab Pipeline Status
echo "1️⃣ GitLab Pipeline Status:"
curl -s "http://192.168.1.10/api/v4/projects/root%2Fssl-monitor-pro/pipelines?per_page=1" \
  -H "PRIVATE-TOKEN: $GITLAB_TOKEN" | jq '.[0] | {status, created_at}'

# 2. Production Health
echo ""
echo "2️⃣ Production Health:"
curl -s https://ssl-monitor-api.onrender.com/health | jq '.'

# 3. Error Rate (from Sentry)
echo ""
echo "3️⃣ Error Rate (last 24h):"
# Проверить Sentry dashboard вручную

# 4. User Activity
echo ""
echo "4️⃣ Active Users (last 24h):"
# Проверить analytics dashboard

# 5. SSL Checks Count
echo ""
echo "5️⃣ SSL Checks Performed:"
# Проверить database metrics

echo ""
echo "✅ Daily check complete"
```

**Метрики для отслеживания:**

| Метрика | Target | Дни 1-3 | Дни 4-7 |
|---------|--------|---------|---------|
| Pipeline Success Rate | >95% | ___% | ___% |
| API Response Time | <200ms | ___ms | ___ms |
| Error Rate | <0.1% | ___% | ___% |
| Uptime | >99.9% | ___% | ___% |
| Deploy Time | <10min | ___min | ___min |

### Week 2-4: Stabilization

**Weekly Review Checklist:**

- [ ] **Week 2 Review**
  - [ ] No critical incidents
  - [ ] All metrics within targets
  - [ ] User feedback collected
  - [ ] Team comfortable with GitLab

- [ ] **Week 3 Review**
  - [ ] Performance stable
  - [ ] CI/CD optimized
  - [ ] Documentation complete
  - [ ] Training completed

- [ ] **Week 4 Review**
  - [ ] Migration officially complete
  - [ ] GitHub backup archived
  - [ ] Lessons learned documented
  - [ ] Success metrics published

---

## 🚨 TROUBLESHOOTING

### Проблема 1: Pipeline fails на GitLab

**Симптомы:**
- Pipeline fails на stage `test` или `build`
- Errors в logs

**Решение:**

```bash
# 1. Проверить logs в GitLab
# CI/CD → Pipelines → Failed Pipeline → Job Logs

# 2. Типичные проблемы:
# a) Missing environment variables
echo "Check: Settings → CI/CD → Variables"

# b) Docker build fails
echo "Check: Dockerfile syntax and dependencies"

# c) Tests fail
echo "Check: Test database connection and fixtures"

# 3. Локальный тест
# Запустить pipeline locally с gitlab-runner
gitlab-runner exec docker backend-tests
```

---

### Проблема 2: Render.com не деплоится

**Симптомы:**
- Deploy hook вызван, но deploy не начинается
- Render shows old code

**Решение:**

```bash
# 1. Проверить Deploy Hook URL
echo $RENDER_DEPLOY_HOOK_URL
# Должен быть: https://api.render.com/deploy/srv-xxxxx?key=xxxxx

# 2. Проверить что GitHub auto-deploy выключен
# Render Dashboard → Settings → Auto-Deploy: OFF

# 3. Manual trigger
curl -X POST $RENDER_DEPLOY_HOOK_URL

# 4. Проверить Render logs
# Render Dashboard → Logs → Deploy Logs
```

---

### Проблема 3: Cloudflare Pages не обновляется

**Симптомы:**
- GitLab pipeline успешен, но frontend старый
- Cloudflare shows old version

**Решение:**

```bash
# 1. Проверить Wrangler authentication
npx wrangler whoami

# 2. Manual deploy
cd frontend-modern
npm run build
npx wrangler pages publish dist --project-name=ssl-monitor-pro

# 3. Проверить Cloudflare Cache
# Cloudflare Dashboard → Caching → Purge Everything

# 4. Проверить GitLab job logs
# CI/CD → Pipelines → deploy-frontend → View Logs
```

---

### Проблема 4: Webhooks не работают

**Симптомы:**
- Stripe/Telegram/Slack webhooks fail
- 404 or 500 errors

**Решение:**

```bash
# 1. Проверить что backend deployed
curl https://ssl-monitor-api.onrender.com/health

# 2. Проверить webhook endpoints
curl https://ssl-monitor-api.onrender.com/api/v1/stripe/webhook
# Должен вернуть 405 (Method Not Allowed) - это OK для GET

# 3. Проверить webhook signatures
# В backend logs должны быть webhook events

# 4. Re-configure webhooks
# Stripe: Developers → Webhooks → Edit endpoint
# Telegram: /setWebhook command
# Slack: Event Subscriptions → Re-verify URL
```

---

### Проблема 5: Environment Variables не работают

**Симптомы:**
- Backend errors: "Environment variable X not found"
- Features не работают

**Решение:**

```bash
# 1. Проверить в GitLab
# Settings → CI/CD → Variables
# Должны быть ВСЕ переменные из setup-gitlab-vars.sh

# 2. Проверить на Render.com
# Service → Environment → Environment Variables
# Должны быть все переменные

# 3. Re-deploy с новыми переменными
curl -X POST $RENDER_DEPLOY_HOOK_URL

# 4. Проверить logs
# Render Dashboard → Logs
# Искать: "Loading environment variables"
```

---

## 📝 ФИНАЛЬНЫЙ ЧЕКЛИСТ

**Перед тем как отключить GitHub полностью:**

- [ ] ✅ GitLab работает стабильно 30+ дней
- [ ] ✅ Все metrics в норме (uptime, errors, performance)
- [ ] ✅ Zero critical incidents за последние 2 недели
- [ ] ✅ Все stakeholders уведомлены и согласны
- [ ] ✅ Backup GitHub создан и проверен (restore test)
- [ ] ✅ Документация полностью обновлена
- [ ] ✅ Team комфортно работает с GitLab
- [ ] ✅ Rollback plan протестирован
- [ ] ✅ Monitoring настроен и работает
- [ ] ✅ Все интеграции работают
- [ ] ✅ Users не испытывают проблем
- [ ] ✅ Performance лучше или равна GitHub setup

**Когда ВСЕ пункты выполнены:**

```bash
# 1. Создать финальный backup
./scripts/final-backup.sh

# 2. Archive GitHub repository
gh repo archive root/ssl-monitor-pro

# 3. Update README
echo "✅ Repository archived. New home: GitLab" > README.md
git -C backup-github-ssl-monitor add README.md
git -C backup-github-ssl-monitor commit -m "Archive repository"
git -C backup-github-ssl-monitor push origin main

# 4. Send notifications
echo "🎉 GitHub → GitLab migration complete!"
# Notify team, users, stakeholders
```

---

## 🎉 SUCCESS CRITERIA

**Миграция считается успешной если:**

1. **Technical:**
   - ✅ GitLab CI/CD pipeline работает без ошибок
   - ✅ Все deploys успешны (backend + frontend)
   - ✅ Zero downtime во время миграции
   - ✅ Все integrations работают (Stripe, Telegram, Slack)
   - ✅ Performance равна или лучше GitHub

2. **Operational:**
   - ✅ Team может работать с GitLab без проблем
   - ✅ Deploy процесс понятен и задокументирован
   - ✅ Monitoring и alerting настроены
   - ✅ Incident response plan готов

3. **Business:**
   - ✅ Zero user complaints
   - ✅ No service disruption
   - ✅ All features работают
   - ✅ Payments processing normally
   - ✅ SSL monitoring uninterrupted

---

## 📚 ДОПОЛНИТЕЛЬНЫЕ РЕСУРСЫ

### Документация

- **GitLab CI/CD:** https://docs.gitlab.com/ee/ci/
- **Render.com Webhooks:** https://render.com/docs/deploy-hooks
- **Cloudflare Pages:** https://developers.cloudflare.com/pages/
- **Wrangler CLI:** https://developers.cloudflare.com/workers/wrangler/

### Скрипты

Все скрипты для миграции:
```
scripts/
├── setup-gitlab-vars.sh       # Настройка GitLab Variables
├── setup-render.sh            # Настройка Render.com
├── smoke-tests.sh             # Smoke tests production
├── rollback-to-github.sh      # Rollback plan
├── update-links.sh            # Обновление ссылок
├── daily-health-check.sh      # Ежедневные проверки
└── final-backup.sh            # Финальный backup
```

### Contacts

**В случае проблем:**
- GitLab Support: http://192.168.1.10/help
- Render Support: https://render.com/support
- Cloudflare Support: https://support.cloudflare.com
- Team Lead: [your-email@example.com]

---

## ✅ ГОТОВЫ К МИГРАЦИИ?

**Проверьте готовность:**

```bash
# Быстрая проверка готовности
./scripts/migration-readiness-check.sh
```

**Если готовы:**

```bash
# 1. Заполнить .migration-secrets реальными значениями
# 2. Запустить: ./scripts/setup-gitlab-vars.sh
# 3. Следовать Phase 1-5 из этого гайда
```
