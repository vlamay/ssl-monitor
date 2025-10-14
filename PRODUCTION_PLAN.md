# 🚀 Production Deployment Plan - Все проекты

**Дата:** 12 октября 2025  
**Локация:** `/home/vmaidaniuk/Cursor/`

---

## 📋 ОБЗОР ПРОЕКТОВ

### Проект 1: **SSL Monitor Pro** (текущий)
- **Путь:** `/home/vmaidaniuk/Cursor/ssl-monitor-final/`
- **Статус:** ✅ 95% готов
- **Backend:** Render.com (deployed)
- **Frontend:** Cloudflare Pages (нужен deploy)
- **Домен:** cloudsre.xyz

### Проект 2: **Cloudere SaaS** (новый?)
- **Путь:** Нужно создать
- **Статус:** ⏳ Планируется
- **Stack:** Cloudflare Pages + Workers
- **Особенности:** 7-day trial + Stripe + Telegram

---

## 🔑 ДОСТУПНЫЕ КЛЮЧИ И ТОКЕНЫ

### Stripe (Test Keys)
```bash
STRIPE_PUBLISHABLE_KEY=pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
STRIPE_SECRET_KEY=sk_test_51SGoJM20i6fmlbYddqN7SFX5II50PU8FNXk3TddOnH6QipGMvXwsmUxvoOKFITR42B924oxrc12Mx5t9pAQMX6Q700Zv95jBJt
```

### Telegram Bots (2 разных)
```bash
# Bot 1 (для SSL Monitor?)
TELEGRAM_BOT_TOKEN=8343479392:AAH-XrM21TvjTt7YxG0IEYntP2RzTsxNPko

# Bot 2 (@UM_Agent_bot)
TELEGRAM_BOT_TOKEN=7409378539:AAHGan44vnafc8FOWgyF0FnE3mmHaYhdhrs
```

### Email
```bash
ADMIN_EMAIL=devops@upcz.cz
```

---

## 🎯 ПРИОРИТЕТНЫЕ ЗАДАЧИ

### 🔴 СРОЧНО: SSL Monitor Pro → Production

**Что нужно (2 часа):**

1. **Deploy Frontend на Cloudflare Pages** (30 мин)
   ```bash
   cd /home/vmaidaniuk/Cursor/ssl-monitor-final/frontend-modern
   # Подключить к Cloudflare Pages через GitHub
   ```

2. **Настроить DNS** (15 мин)
   ```
   CNAME @ → pages.dev
   CNAME www → pages.dev  
   CNAME status → render.com
   ```

3. **Добавить Stripe keys на Render** (10 мин)
   ```bash
   STRIPE_PUBLISHABLE_KEY=pk_test_...
   STRIPE_SECRET_KEY=sk_test_...
   ```

4. **Настроить Telegram bot** (15 мин)
   ```bash
   export TELEGRAM_BOT_TOKEN="8343479392:AAH-XrM21TvjTt7YxG0IEYntP2RzTsxNPko"
   # Получить CHAT_ID
   # Добавить на Render
   ```

5. **Production Testing** (30 мин)
   - Test full user flow
   - Add test domain
   - Check SSL monitoring
   - Test Stripe checkout
   - Verify Telegram alerts

---

## 🟡 ОПЦИОНАЛЬНО: Новый проект Cloudere SaaS

**Если хотите создать второй SaaS проект:**

### Структура проекта
```bash
mkdir -p ~/Cursor/cloudere-saas
cd ~/Cursor/cloudere-saas

# Создать структуру
mkdir -p {frontend,backend,config,docs}
```

### Особенности Cloudere
- ✅ 7-day free trial
- ✅ Stripe subscription
- ✅ Telegram notifications (@UM_Agent_bot)
- ✅ Cloudflare Workers backend
- ✅ React frontend
- ✅ Auto-block после trial без оплаты

### Stack
```
Frontend: React + Tailwind CSS + Cloudflare Pages
Backend: Cloudflare Workers (Node.js)
Auth: Supabase
Payments: Stripe
Notifications: Telegram
Database: Supabase PostgreSQL
```

---

## 🔧 ПРАКТИЧЕСКИЕ КОМАНДЫ

### Для SSL Monitor Pro (текущий проект)

#### 1. Обновить .env с вашими ключами
```bash
cd /home/vmaidaniuk/Cursor/ssl-monitor-final/backend
nano .env

# Добавить:
TELEGRAM_BOT_TOKEN=8343479392:AAH-XrM21TvjTt7YxG0IEYntP2RzTsxNPko
TELEGRAM_CHAT_ID=<ваш_chat_id>
STRIPE_SECRET_KEY=sk_test_51SGoJM20i6fmlbYddqN7SFX5II50PU8FNXk3TddOnH6QipGMvXwsmUxvoOKFITR42B924oxrc12Mx5t9pAQMX6Q700Zv95jBJt
STRIPE_PUBLISHABLE_KEY=pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
```

#### 2. Получить Telegram CHAT_ID
```python
# Запустить бота и отправить ему сообщение
python3 - <<'EOF'
import requests
token = "8343479392:AAH-XrM21TvjTt7YxG0IEYntP2RzTsxNPko"
r = requests.get(f"https://api.telegram.org/bot{token}/getUpdates")
print(r.json())
# Найти chat.id в ответе
EOF
```

#### 3. Test Telegram уведомления
```python
python3 - <<'EOF'
import requests
token = "8343479392:AAH-XrM21TvjTt7YxG0IEYntP2RzTsxNPko"
chat_id = "YOUR_CHAT_ID"  # Вставить свой
r = requests.post(
    f"https://api.telegram.org/bot{token}/sendMessage",
    json={"chat_id": chat_id, "text": "✅ SSL Monitor Pro - Test OK"}
)
print(r.json())
EOF
```

#### 4. Commit и push на Render
```bash
cd /home/vmaidaniuk/Cursor/ssl-monitor-final
git add .
git commit -m "production: add stripe + telegram config"
git push origin main
# Render auto-deploy
```

#### 5. Добавить env vars на Render.com
```
Dashboard → ssl-monitor-api → Environment
Add:
- STRIPE_SECRET_KEY=sk_test_...
- STRIPE_PUBLISHABLE_KEY=pk_test_...
- TELEGRAM_BOT_TOKEN=8343479392:AAH...
- TELEGRAM_CHAT_ID=<your_id>
```

#### 6. Deploy Frontend на Cloudflare Pages
```bash
# В Cloudflare Dashboard:
1. Pages → Create a project
2. Connect to Git → выбрать ssl-monitor-final
3. Build settings:
   - Build command: (empty)
   - Build output directory: /frontend-modern
   - Root directory: frontend-modern
4. Environment variables:
   - VITE_API_URL=https://status.cloudsre.xyz
5. Deploy
```

#### 7. Configure DNS в Cloudflare
```
DNS → Add record:

Type    Name    Target                              Proxy
CNAME   @       ssl-monitor-final.pages.dev         Yes
CNAME   www     ssl-monitor-final.pages.dev         Yes
CNAME   status  ssl-monitor-api.onrender.com        Yes
```

#### 8. Health check production
```bash
curl https://cloudsre.xyz
curl https://status.cloudsre.xyz/health
curl https://status.cloudsre.xyz/statistics
```

---

## 🆕 ДЛЯ СОЗДАНИЯ НОВОГО ПРОЕКТА (Cloudere)

### Быстрый старт
```bash
# 1. Создать проект
mkdir -p ~/Cursor/cloudere-saas && cd ~/Cursor/cloudere-saas

# 2. Инициализация
npm create vite@latest frontend -- --template react
mkdir backend

# 3. .env файл
cat > .env <<'EOF'
# Stripe
STRIPE_PUBLIC_KEY=pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
STRIPE_SECRET_KEY=sk_test_51SGoJM20i6fmlbYddqN7SFX5II50PU8FNXk3TddOnH6QipGMvXwsmUxvoOKFITR42B924oxrc12Mx5t9pAQMX6Q700Zv95jBJt

# Telegram
TELEGRAM_BOT_TOKEN=7409378539:AAHGan44vnafc8FOWgyF0FnE3mmHaYhdhrs
TELEGRAM_CHAT_ID=<your_chat_id>

# Config
TRIAL_DAYS=7
ADMIN_EMAIL=devops@upcz.cz
FRONTEND_URL=https://cloudere.xyz
EOF

# 4. Git
git init
echo ".env" >> .gitignore
echo "node_modules" >> .gitignore
```

### Cloudflare Worker для backend
```javascript
// backend/worker.js
import Stripe from 'stripe';

export default {
  async fetch(request, env) {
    const stripe = new Stripe(env.STRIPE_SECRET_KEY);
    const url = new URL(request.url);
    
    // Create checkout session
    if (url.pathname === '/api/checkout' && request.method === 'POST') {
      const { priceId } = await request.json();
      
      const session = await stripe.checkout.sessions.create({
        payment_method_types: ['card'],
        line_items: [{ price: priceId, quantity: 1 }],
        mode: 'subscription',
        subscription_data: {
          trial_period_days: 7,
        },
        success_url: `${env.FRONTEND_URL}/success`,
        cancel_url: `${env.FRONTEND_URL}/pricing`,
      });
      
      return new Response(JSON.stringify({ url: session.url }), {
        headers: { 'Content-Type': 'application/json' },
      });
    }
    
    // Stripe webhook
    if (url.pathname === '/api/webhook' && request.method === 'POST') {
      const body = await request.text();
      const sig = request.headers.get('stripe-signature');
      
      const event = stripe.webhooks.constructEvent(
        body,
        sig,
        env.STRIPE_WEBHOOK_SECRET
      );
      
      // Handle events
      switch (event.type) {
        case 'checkout.session.completed':
          await notifyTelegram(env, `💰 New subscription: ${event.data.object.customer_email}`);
          break;
        case 'customer.subscription.trial_will_end':
          await notifyTelegram(env, `⏰ Trial ending tomorrow: ${event.data.object.customer_email}`);
          break;
        case 'invoice.payment_failed':
          await notifyTelegram(env, `❌ Payment failed: ${event.data.object.customer_email}`);
          break;
      }
      
      return new Response('OK', { status: 200 });
    }
    
    return new Response('Not Found', { status: 404 });
  },
};

async function notifyTelegram(env, message) {
  await fetch(`https://api.telegram.org/bot${env.TELEGRAM_BOT_TOKEN}/sendMessage`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: env.TELEGRAM_CHAT_ID,
      text: message,
    }),
  });
}
```

### Deploy Cloudflare Worker
```bash
npm install -g wrangler
wrangler login
wrangler init
wrangler publish

# Add secrets
wrangler secret put STRIPE_SECRET_KEY
wrangler secret put TELEGRAM_BOT_TOKEN
wrangler secret put TELEGRAM_CHAT_ID
```

---

## 📊 СРАВНЕНИЕ ПРОЕКТОВ

| Параметр | SSL Monitor Pro | Cloudere SaaS |
|----------|-----------------|---------------|
| **Статус** | ✅ 95% готов | ⏳ Планируется |
| **Backend** | FastAPI (Render) | CF Workers |
| **Frontend** | HTML+Tailwind | React+Tailwind |
| **База** | PostgreSQL | Supabase |
| **Auth** | Нет (v2.0) | Supabase Auth |
| **Платежи** | Stripe ✅ | Stripe ✅ |
| **Trial** | 14 дней | 7 дней |
| **Telegram** | ✅ Настроить | ✅ Готов |
| **Домен** | cloudsre.xyz | cloudere.xyz |
| **Hosting** | Render + CF | Только CF |
| **Стоимость** | €0/мес | €0/мес |

---

## 🎯 РЕКОМЕНДАЦИИ

### Вариант 1: Завершить SSL Monitor Pro (рекомендую)
**Преимущества:**
- ✅ Уже 95% готов
- ✅ Протестирован
- ✅ Полная документация
- ✅ 2 часа до launch

**Шаги:**
1. Deploy frontend (30 мин)
2. Configure Telegram (15 мин)
3. Add Stripe keys (10 мин)
4. Testing (30 мин)
5. **LAUNCH!** 🚀

### Вариант 2: Создать Cloudere SaaS
**Преимущества:**
- ✅ Полностью на Cloudflare (быстрее)
- ✅ 7-day trial (короче цикл)
- ✅ Supabase Auth (готовая аутентификация)

**Недостатки:**
- ⏳ Нужно создавать с нуля (~2 недели)
- ⏳ Нет готового кода
- ⏳ Нужно тестировать

### Вариант 3: Оба проекта параллельно
**Не рекомендую**, потому что:
- Разделение фокуса
- Два проекта на поддержке
- Меньше шансов на успех каждого

---

## ✅ ЧЕКЛИСТ: SSL Monitor Pro → Production (СЕГОДНЯ)

### Backend (Render.com)
- [x] API deployed
- [x] PostgreSQL running
- [x] Redis running
- [ ] Add TELEGRAM_BOT_TOKEN env var
- [ ] Add TELEGRAM_CHAT_ID env var
- [ ] Add STRIPE_SECRET_KEY env var
- [ ] Test health endpoint

### Frontend (Cloudflare Pages)
- [ ] Create Pages project
- [ ] Connect GitHub repo
- [ ] Set build directory: frontend-modern
- [ ] Add environment variables
- [ ] Deploy
- [ ] Test site

### DNS (Cloudflare)
- [ ] Add CNAME @ → pages.dev
- [ ] Add CNAME www → pages.dev
- [ ] Add CNAME status → render.com
- [ ] Enable proxy
- [ ] Wait for propagation (5-10 min)

### Telegram
- [ ] Get CHAT_ID
- [ ] Test bot message
- [ ] Add to Render env vars
- [ ] Test notification from app

### Stripe
- [ ] Create webhook endpoint
- [ ] Add webhook URL to Stripe
- [ ] Test checkout flow
- [ ] Test webhook events

### Final Testing
- [ ] Open https://cloudsre.xyz
- [ ] Add test domain
- [ ] Trigger SSL check
- [ ] Check statistics
- [ ] Test Stripe payment
- [ ] Verify Telegram alert
- [ ] ✅ LAUNCH!

---

## 🚀 СЛЕДУЮЩИЕ ШАГИ

**ПРЯМО СЕЙЧАС (выбрать один):**

### A) Завершить SSL Monitor Pro
```bash
# Я помогу:
1. Deploy frontend на Cloudflare
2. Настроить Telegram
3. Добавить Stripe keys
4. Запустить в production
```

### B) Создать Cloudere SaaS
```bash
# Я создам:
1. Новую структуру проекта
2. Cloudflare Worker backend
3. React frontend
4. Интеграцию Stripe + Telegram
```

### C) Что-то другое?
Скажите, что именно нужно!

---

**Что делаем?** 🤔

1. ⚡ **Завершаем SSL Monitor Pro** (2 часа → launch) ← Рекомендую!
2. 🆕 **Создаём Cloudere SaaS** (2 недели → launch)
3. 📋 **Другой план**

---

*Создано: 12 октября 2025*  
*Локация: /home/vmaidaniuk/Cursor/ssl-monitor-final/*

