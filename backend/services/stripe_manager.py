import stripe
from datetime import datetime
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Stripe configuration
stripe.api_key = os.getenv('STRIPE_SECRET_KEY', 'YOUR_STRIPE_SECRET_KEY_HERE')

# Pricing plans (we'll create these products in Stripe)
PLANS = {
    'starter': {
        'name': 'Starter',
        'price': 1900,  # €19.00 in cents
        'currency': 'eur',
        'interval': 'month',
        'features': {
            'max_domains': 10,
            'email_alerts': True,
            'telegram_alerts': False,
            'slack_alerts': False,
            'api_access': False,
            'history_days': 7,
            'support_level': 'email'
        }
    },
    'professional': {
        'name': 'Professional',
        'price': 4900,  # €49.00 in cents
        'currency': 'eur',
        'interval': 'month',
        'features': {
            'max_domains': 50,
            'email_alerts': True,
            'telegram_alerts': True,
            'slack_alerts': True,
            'api_access': True,
            'history_days': 90,
            'support_level': 'priority'
        }
    },
    'enterprise': {
        'name': 'Enterprise',
        'price': 14900,  # €149.00 in cents
        'currency': 'eur',
        'interval': 'month',
        'features': {
            'max_domains': -1,  # unlimited
            'email_alerts': True,
            'telegram_alerts': True,
            'slack_alerts': True,
            'api_access': True,
            'history_days': 365,
            'support_level': '24/7_phone'
        }
    }
}

class StripeManager:
    """Stripe payment and subscription management"""
    
    def __init__(self):
        self.stripe = stripe
    
    def create_or_get_product(self, plan_name: str):
        """Create or retrieve Stripe product for a plan"""
        plan = PLANS.get(plan_name)
        if not plan:
            raise ValueError(f"Invalid plan: {plan_name}")
        
        try:
            # Search for existing product
            products = stripe.Product.list(limit=100)
            for product in products.data:
                if product.name == f"SSL Monitor - {plan['name']}":
                    logger.info(f"Found existing product: {product.id}")
                    return product
            
            # Create new product if not found
            product = stripe.Product.create(
                name=f"SSL Monitor - {plan['name']}",
                description=f"{plan['name']} plan for SSL certificate monitoring",
                metadata={'plan_type': plan_name}
            )
            
            logger.info(f"Created new product: {product.id}")
            return product
            
        except Exception as e:
            logger.error(f"Error creating/getting product: {str(e)}")
            raise
    
    def create_or_get_price(self, plan_name: str):
        """Create or retrieve Stripe price for a plan"""
        plan = PLANS.get(plan_name)
        if not plan:
            raise ValueError(f"Invalid plan: {plan_name}")
        
        try:
            product = self.create_or_get_product(plan_name)
            
            # Search for existing price
            prices = stripe.Price.list(product=product.id, limit=100)
            for price in prices.data:
                if price.unit_amount == plan['price'] and price.active:
                    logger.info(f"Found existing price: {price.id}")
                    return price
            
            # Create new price if not found
            price = stripe.Price.create(
                product=product.id,
                unit_amount=plan['price'],
                currency=plan['currency'],
                recurring={'interval': plan['interval']},
                metadata={'plan_type': plan_name}
            )
            
            logger.info(f"Created new price: {price.id}")
            return price
            
        except Exception as e:
            logger.error(f"Error creating/getting price: {str(e)}")
            raise
    
    def create_customer(self, email: str, name: str = None, metadata: dict = None):
        """Create a Stripe customer"""
        try:
            customer = stripe.Customer.create(
                email=email,
                name=name,
                description=f"SSL Monitor customer since {datetime.utcnow().date()}",
                metadata=metadata or {}
            )
            logger.info(f"Created customer: {customer.id}")
            return customer
        except Exception as e:
            logger.error(f"Error creating customer: {str(e)}")
            raise
    
    def create_checkout_session(self, customer_email: str, plan_name: str, 
                                success_url: str = None, cancel_url: str = None,
                                trial_days: int = 7):
        """Create a Stripe Checkout session for subscription"""
        try:
            price = self.create_or_get_price(plan_name)
            plan = PLANS[plan_name]
            
            if not success_url:
                success_url = 'http://localhost/success?session_id={CHECKOUT_SESSION_ID}'
            if not cancel_url:
                cancel_url = 'http://localhost/pricing'
            
            session = stripe.checkout.Session.create(
                customer_email=customer_email,
                payment_method_types=['card'],
                line_items=[{
                    'price': price.id,
                    'quantity': 1,
                }],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                subscription_data={
                    'trial_period_days': trial_days,
                    'metadata': {
                        'plan_name': plan_name,
                        'max_domains': plan['features']['max_domains']
                    }
                },
                allow_promotion_codes=True,  # Enable promo codes
                metadata={'plan_name': plan_name}
            )
            
            logger.info(f"Created checkout session: {session.id}")
            return session
            
        except Exception as e:
            logger.error(f"Error creating checkout session: {str(e)}")
            raise
    
    def create_subscription(self, customer_id: str, plan_name: str, trial_days: int = 7):
        """Create a subscription directly (without checkout)"""
        try:
            price = self.create_or_get_price(plan_name)
            
            subscription = stripe.Subscription.create(
                customer=customer_id,
                items=[{'price': price.id}],
                trial_period_days=trial_days,
                metadata={'plan_name': plan_name}
            )
            
            logger.info(f"Created subscription: {subscription.id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error creating subscription: {str(e)}")
            raise
    
    def cancel_subscription(self, subscription_id: str, immediately: bool = False):
        """Cancel a subscription"""
        try:
            if immediately:
                subscription = stripe.Subscription.delete(subscription_id)
            else:
                subscription = stripe.Subscription.modify(
                    subscription_id,
                    cancel_at_period_end=True
                )
            
            logger.info(f"Cancelled subscription: {subscription_id}")
            return subscription
            
        except Exception as e:
            logger.error(f"Error cancelling subscription: {str(e)}")
            raise
    
    def get_subscription(self, subscription_id: str):
        """Get subscription details"""
        try:
            return stripe.Subscription.retrieve(subscription_id)
        except Exception as e:
            logger.error(f"Error getting subscription: {str(e)}")
            raise
    
    def create_promo_code(self, code: str, percent_off: int, duration: str = 'once'):
        """Create a promotional discount code"""
        try:
            # Create coupon first
            coupon = stripe.Coupon.create(
                percent_off=percent_off,
                duration=duration,  # 'once', 'repeating', or 'forever'
                name=f"{percent_off}% off"
            )
            
            # Create promo code
            promo_code = stripe.PromotionCode.create(
                coupon=coupon.id,
                code=code,
                active=True
            )
            
            logger.info(f"Created promo code: {code}")
            return promo_code
            
        except Exception as e:
            logger.error(f"Error creating promo code: {str(e)}")
            raise
    
    def handle_webhook(self, payload: bytes, sig_header: str):
        """Handle Stripe webhook events"""
        webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, webhook_secret
            )
        except ValueError as e:
            logger.error("Invalid payload")
            raise
        except stripe.error.SignatureVerificationError as e:
            logger.error("Invalid signature")
            raise
        
        # Handle different event types
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            self._handle_checkout_completed(session)
        
        elif event['type'] == 'customer.subscription.created':
            subscription = event['data']['object']
            self._handle_subscription_created(subscription)
        
        elif event['type'] == 'customer.subscription.updated':
            subscription = event['data']['object']
            self._handle_subscription_updated(subscription)
        
        elif event['type'] == 'customer.subscription.deleted':
            subscription = event['data']['object']
            self._handle_subscription_deleted(subscription)
        
        elif event['type'] == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            self._handle_payment_succeeded(invoice)
        
        elif event['type'] == 'invoice.payment_failed':
            invoice = event['data']['object']
            self._handle_payment_failed(invoice)
        
        return event
    
    def _handle_checkout_completed(self, session):
        """Handle successful checkout"""
        logger.info(f"Checkout completed: {session.id}")
        # Update user's subscription status in database
        pass
    
    def _handle_subscription_created(self, subscription):
        """Handle new subscription"""
        logger.info(f"Subscription created: {subscription.id}")
        # Activate user's account
        pass
    
    def _handle_subscription_updated(self, subscription):
        """Handle subscription update"""
        logger.info(f"Subscription updated: {subscription.id}")
        # Update user's plan/limits
        pass
    
    def _handle_subscription_deleted(self, subscription):
        """Handle subscription cancellation"""
        logger.info(f"Subscription deleted: {subscription.id}")
        # Deactivate user's account or downgrade to free
        pass
    
    def _handle_payment_succeeded(self, invoice):
        """Handle successful payment"""
        logger.info(f"Payment succeeded: {invoice.id}")
        # Send receipt, extend subscription
        pass
    
    def _handle_payment_failed(self, invoice):
        """Handle failed payment"""
        logger.info(f"Payment failed: {invoice.id}")
        # Send payment failure email
        pass

# Global instance
stripe_manager = StripeManager()

# Initialize products and prices on startup
def initialize_stripe_products():
    """Initialize all Stripe products and prices"""
    logger.info("Initializing Stripe products and prices...")
    for plan_name in PLANS.keys():
        try:
            stripe_manager.create_or_get_price(plan_name)
            logger.info(f"✓ {plan_name} plan ready")
        except Exception as e:
            logger.error(f"✗ Failed to initialize {plan_name}: {str(e)}")

if __name__ == '__main__':
    # Run initialization
    initialize_stripe_products()
    
    # Create some test promo codes
    try:
        stripe_manager.create_promo_code('SAVE20', 20, 'once')
        stripe_manager.create_promo_code('LAUNCH50', 50, 'once')
        logger.info("✓ Promo codes created")
    except:
        logger.info("Promo codes already exist")

