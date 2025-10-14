# 💳 Stripe Production Setup

## 1. Создать Products в Stripe Dashboard

Перейти: https://dashboard.stripe.com/products

### Product 1: Starter Plan
- Name: SSL Monitor - Starter
- Price: €19.00 EUR / month
- Trial: 7 days
- Features metadata:
  - max_domains: 10
  - email_alerts: true

### Product 2: Professional Plan
- Name: SSL Monitor - Professional
- Price: €49.00 EUR / month
- Trial: 7 days
- Features metadata:
  - max_domains: 50
  - multi_channel_alerts: true
  - priority_support: true

### Product 3: Enterprise Plan
- Name: SSL Monitor - Enterprise
- Price: €149.00 EUR / month
- Trial: 7 days
- Features metadata:
  - max_domains: -1 (unlimited)
  - custom_integration: true
  - sla: true

## 2. Настроить Webhook

### Webhook URL
```
https://status.cloudsre.xyz/billing/webhook
```

### Events to subscribe
- ✅ checkout.session.completed
- ✅ customer.subscription.created
- ✅ customer.subscription.updated
- ✅ customer.subscription.deleted
- ✅ invoice.payment_succeeded
- ✅ invoice.payment_failed

### После создания
1. Скопировать Webhook Signing Secret
2. Добавить в Render Environment:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```

## 3. Test Mode → Live Mode

После тестирования:
1. Переключить Stripe на Live mode
2. Создать те же products в Live mode
3. Обновить keys в Render:
   - STRIPE_PUBLISHABLE_KEY=pk_live_xxx
   - STRIPE_SECRET_KEY=sk_live_xxx
4. Обновить Webhook URL на Live endpoint

## 4. Тестирование

```bash
# Test checkout (используйте test card: 4242 4242 4242 4242)
curl -X POST https://status.cloudsre.xyz/billing/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "plan": "starter",
    "trial_days": 14
  }'
```
