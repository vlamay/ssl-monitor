# 💳 Stripe Dashboard Setup Guide

## Quick Setup (10 minutes)

### Step 1: Create Products

Go to: https://dashboard.stripe.com/test/products

#### Product 1: Starter Plan
```
Name: SSL Monitor - Starter
Description: Perfect for small businesses monitoring up to 10 domains
Price: €19.00 EUR / month
Billing period: Monthly
Trial period: 7 days
```

**Metadata:**
```
plan_type: starter
max_domains: 10
features: email_alerts,basic_dashboard
```

#### Product 2: Professional Plan
```
Name: SSL Monitor - Professional  
Description: For growing teams monitoring up to 50 domains
Price: €49.00 EUR / month
Billing period: Monthly
Trial period: 7 days
```

**Metadata:**
```
plan_type: professional
max_domains: 50
features: multi_channel_alerts,analytics,priority_support
```

#### Product 3: Enterprise Plan
```
Name: SSL Monitor - Enterprise
Description: Unlimited domains with enterprise features
Price: €149.00 EUR / month
Billing period: Monthly
Trial period: 7 days
```

**Metadata:**
```
plan_type: enterprise
max_domains: unlimited
features: custom_integration,sla,dedicated_support
```

---

### Step 2: Configure Webhook

Go to: https://dashboard.stripe.com/test/webhooks

**Webhook URL:**
```
https://status.cloudsre.xyz/billing/webhook
```

**Events to subscribe:**
- ✅ `checkout.session.completed`
- ✅ `customer.subscription.created`
- ✅ `customer.subscription.updated`
- ✅ `customer.subscription.deleted`
- ✅ `invoice.payment_succeeded`
- ✅ `invoice.payment_failed`

**After creation:**
1. Click on the webhook
2. Copy the **Signing secret** (starts with `whsec_`)
3. Add to Render environment:
   ```
   STRIPE_WEBHOOK_SECRET=whsec_xxxxxxxxxxxxx
   ```

---

### Step 3: Get API Keys

Go to: https://dashboard.stripe.com/test/apikeys

**Copy these keys:**
```
Publishable key: pk_test_51SGoJM20i6fmlbYduMC9YLdC5PU1TEE9i1MOIM8mGcyAZY1Lx3TYuu02w8zGHbKsSRVTMuWUaz1yVBbHUG8Iivro00XaWGmEmY

Secret key: sk_test_51SGoJM20i6fmlbYddqN7SFX5II50PU8FNXk3TddOnH6QipGMvXwsmUxvoOKFITR42B924oxrc12Mx5t9pAQMX6Q700Zv95jBJt
```

---

### Step 4: Test Checkout

Use test card: **4242 4242 4242 4242**
- Any future expiry date
- Any 3-digit CVC
- Any postal code

---

### Step 5: Switch to Live Mode (After Testing)

1. Repeat Steps 1-3 in **Live mode**
2. Update environment variables:
   ```
   STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
   STRIPE_SECRET_KEY=sk_live_xxxxx
   STRIPE_WEBHOOK_SECRET=whsec_live_xxxxx
   ```

---

## Telegram Notifications

When configured, you'll receive Telegram alerts for:

- 🆕 **New Customer:** When checkout completes
- 💳 **Payment Success:** When invoice paid
- ❌ **Payment Failed:** When payment fails
- ⏰ **Trial Ending:** 1 day before trial ends

**Your Chat ID:** 8159854958  
**Bot:** @CloudereMonitorBot

---

## Testing Webhook Locally

If testing locally, use Stripe CLI:

```bash
stripe listen --forward-to localhost:8000/billing/webhook
```

This will give you a webhook signing secret for local testing.

---

## Quick Verification

Test your setup:

```bash
# Test checkout session creation
curl -X POST https://status.cloudsre.xyz/billing/create-checkout-session \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "plan": "starter",
    "trial_days": 14
  }'
```

Expected response:
```json
{
  "checkout_url": "https://checkout.stripe.com/c/pay/...",
  "session_id": "cs_test_...",
  "plan": "starter",
  "trial_days": 14
}
```

---

## Support

If you encounter issues:
- Check Stripe Dashboard → Logs
- Check Render logs
- Verify webhook signature in logs
- Test with Stripe CLI

**Email:** vla.maidaniuk@gmail.com

