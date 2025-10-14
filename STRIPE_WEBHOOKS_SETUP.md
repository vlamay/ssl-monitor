# 💳 Stripe Webhooks Configuration Guide

## 🎯 ЦЕЛЬ
Настроить Stripe webhooks для обработки платежей и подписок

---

## 📋 PREREQUISITES

- ✅ Backend deployed на Render.com
- ✅ DNS настроен: `status.cloudsre.xyz`
- ✅ Stripe account создан: https://dashboard.stripe.com

---

## 🚀 ПОШАГОВАЯ НАСТРОЙКА

### ШАГ 1: Создать Webhook Endpoint в Stripe

1. **Откройте Stripe Dashboard:**
   ```
   https://dashboard.stripe.com/test/webhooks
   ```

2. **Click "Add endpoint"**

3. **Endpoint URL:**
   ```
   https://status.cloudsre.xyz/billing/webhook
   ```

4. **Description:**
   ```
   SSL Monitor Pro - Production Webhook
   ```

5. **Events to send:**
   
   **Выберите эти события:**
   - ✅ `checkout.session.completed`
   - ✅ `customer.subscription.created`
   - ✅ `customer.subscription.updated`
   - ✅ `customer.subscription.deleted`
   - ✅ `invoice.payment_succeeded`
   - ✅ `invoice.payment_failed`
   - ✅ `customer.created`
   - ✅ `customer.updated`

6. **Click "Add endpoint"**

---

### ШАГ 2: Получить Signing Secret

После создания webhook endpoint:

1. **Click на созданный endpoint**

2. **Найдите "Signing secret":**
   ```
   whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```

3. **Click "Reveal"** и скопируйте

---

### ШАГ 3: Обновить Environment Variables на Render

1. **Откройте Render Dashboard:**
   ```
   https://dashboard.render.com
   ```

2. **Найдите service:** `ssl-monitor-api`

3. **Settings → Environment**

4. **Найдите или добавьте переменные:**

   ```
   STRIPE_SECRET_KEY=sk_test_51SGoJM20i6fmlbYddqN7SFX5II50PU8FNXk3TddOnH6QipGMvXwsmUxvoOKFITR42B924oxrc12Mx5t9pAQMX6Q700Zv95jBJt
   
   STRIPE_PUBLISHABLE_KEY=pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY
   
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   ```
   
   **Замените `whsec_xxx...` на ваш реальный Signing Secret!**

5. **Click "Save Changes"**

6. **Render автоматически перезапустит service (~2 минуты)**

---

### ШАГ 4: Тестирование Webhook

**В Stripe Dashboard:**

1. **Webhooks → ваш endpoint → "Send test webhook"**

2. **Выберите event:** `checkout.session.completed`

3. **Click "Send test webhook"**

4. **Проверьте результат:**
   - Status should be: `200 OK` ✅
   - Response time: ~100-500ms

**В Render Dashboard:**

1. **Logs → Найдите запись:**
   ```
   INFO: POST /billing/webhook HTTP/1.1 200 OK
   ```

---

## 🔧 WEBHOOK ENDPOINT IMPLEMENTATION

Ваш backend уже имеет webhook endpoint в `backend/app/billing.py`:

```python
@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            # Handle successful checkout
            pass
        elif event['type'] == 'customer.subscription.created':
            # Handle new subscription
            pass
        # ... etc
        
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

---

## 🧪 TESTING PRODUCTION WEBHOOKS

### Test 1: Checkout Session

1. **Создайте тестовую оплату:**
   ```bash
   curl -X POST https://status.cloudsre.xyz/billing/create-checkout-session \
     -H "Content-Type: application/json" \
     -d '{"price_id": "price_starter", "customer_email": "test@example.com"}'
   ```

2. **Откройте полученный URL**

3. **Используйте тестовую карту:**
   ```
   Card number: 4242 4242 4242 4242
   Expiry: 12/34
   CVC: 123
   ```

4. **Complete payment**

5. **Проверьте webhook в Stripe Dashboard:**
   - Webhooks → Events
   - Должен быть `checkout.session.completed` ✅

---

### Test 2: Failed Payment

1. **Используйте карту с declined:**
   ```
   Card: 4000 0000 0000 0002
   ```

2. **Проверьте event:** `invoice.payment_failed`

---

## 📊 WEBHOOK EVENTS FLOW

```
User completes payment on frontend
         ↓
    Stripe processes payment
         ↓
    Stripe sends webhook to:
    https://status.cloudsre.xyz/billing/webhook
         ↓
    Backend validates signature
         ↓
    Backend processes event
         ↓
    Update database (user subscription)
         ↓
    Send confirmation email
         ↓
    Return 200 OK to Stripe
```

---

## 🔐 SECURITY

### Webhook Signature Verification

**ВАЖНО:** Всегда проверяйте подпись webhook:

```python
event = stripe.Webhook.construct_event(
    payload, 
    sig_header, 
    STRIPE_WEBHOOK_SECRET  # ← Обязательно!
)
```

**Это защищает от:**
- Поддельных webhook requests
- Replay attacks
- Unauthorized access

---

## 🐛 TROUBLESHOOTING

### Error: "No signature found"

**Причина:** STRIPE_WEBHOOK_SECRET не установлен

**Решение:**
```bash
# Render Dashboard → Environment Variables
STRIPE_WEBHOOK_SECRET=whsec_your_secret_here
```

### Error: "Invalid signature"

**Причина:** Неправильный STRIPE_WEBHOOK_SECRET

**Решение:**
1. Скопируйте Signing Secret из Stripe Dashboard
2. Обновите в Render
3. Перезапустите service

### Webhook Returns 400/500

**Причина:** Ошибка в обработке event

**Решение:**
1. Проверьте Render logs
2. Найдите traceback
3. Исправьте код
4. Push на GitHub
5. Render auto-deploy

### Webhook Not Receiving Events

**Причина:** DNS не настроен или endpoint недоступен

**Решение:**
```bash
# Проверьте доступность endpoint
curl https://status.cloudsre.xyz/billing/webhook

# Должен вернуть 405 Method Not Allowed (это нормально для GET)
```

---

## 📈 MONITORING WEBHOOKS

### Stripe Dashboard

**Webhooks → ваш endpoint:**
- ✅ Status: Enabled
- ✅ Success rate: >95%
- ✅ Avg response time: <500ms
- ✅ Recent attempts: Success

### Render Logs

**Найдите webhook requests:**
```
INFO: POST /billing/webhook - 200 OK
INFO: Stripe event: checkout.session.completed
INFO: Processing subscription for customer: cus_xxx
```

---

## 🎯 PRODUCTION WEBHOOK CHECKLIST

После настройки проверьте:

- [ ] Webhook endpoint создан в Stripe
- [ ] Signing secret скопирован
- [ ] STRIPE_WEBHOOK_SECRET добавлен в Render
- [ ] Render service перезапущен
- [ ] Test webhook отправлен успешно
- [ ] Production payment протестирован
- [ ] Events логируются в Render
- [ ] Database обновляется корректно

---

## 🔄 PRODUCTION vs TEST MODE

### Test Mode (Development)
```
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_test_...

Webhook URL: https://status.cloudsre.xyz/billing/webhook
Card: 4242 4242 4242 4242
```

### Live Mode (Production)
```
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_live_...

Webhook URL: https://status.cloudsre.xyz/billing/webhook
Card: Real customer cards
```

**Переход на Live Mode:**
1. Stripe Dashboard → Toggle to "Live mode"
2. Create new webhook endpoint (live mode)
3. Update STRIPE_SECRET_KEY и STRIPE_WEBHOOK_SECRET
4. Redeploy на Render

---

## 💰 PRICING INTEGRATION

После настройки webhooks, подключите pricing page:

**Frontend:**
```javascript
// Checkout session
const response = await api.createCheckoutSession({
    price_id: 'price_starter',  // or price_professional
    customer_email: 'user@example.com'
});

// Redirect to Stripe Checkout
window.location.href = response.url;
```

**Backend обработает:**
1. `checkout.session.completed` - создаст subscription
2. `invoice.payment_succeeded` - подтвердит оплату
3. `customer.subscription.created` - активирует account

---

## 📞 SUPPORT

**Stripe Documentation:**
- Webhooks: https://stripe.com/docs/webhooks
- Testing: https://stripe.com/docs/webhooks/test
- Events: https://stripe.com/docs/api/events

**Contact:**
- Email: vla.maidaniuk@gmail.com
- Phone: +420 721 579 603

---

## ✅ SUCCESS CRITERIA

**Webhooks работают когда:**

1. ✅ Stripe Dashboard показывает "Success" для test webhooks
2. ✅ Render logs показывают incoming webhook requests
3. ✅ Database обновляется после payment events
4. ✅ Users получают access после оплаты
5. ✅ Subscriptions активируются корректно

---

## 🎉 ГОТОВО!

**После настройки webhooks ваш SSL Monitor Pro:**

✅ Полностью функциональный backend  
✅ Beautiful frontend  
✅ Payment processing готов  
✅ Subscriptions management работает  
✅ Production ready!

**Можно начинать привлекать клиентов!** 🚀

---

**Last Updated:** October 12, 2025  
**Status:** ✅ Ready for Configuration


