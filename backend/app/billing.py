from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from typing import Optional
import sys
import os
import logging

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db
from services.stripe_manager import stripe_manager, PLANS
from utils.telegram import (
    send_payment_success_alert,
    send_payment_failed_alert,
    send_new_user_alert
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["billing"])

@router.post("/create-checkout-session")
async def create_checkout_session(
    email: str,
    plan: str,
    trial_days: int = 7,
    db: Session = Depends(get_db)
):
    """Create a Stripe checkout session for subscription"""
    if plan not in PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Choose from: {', '.join(PLANS.keys())}"
        )
    
    try:
        session = stripe_manager.create_checkout_session(
            customer_email=email,
            plan_name=plan,
            trial_days=trial_days
        )
        
        return {
            "checkout_url": session.url,
            "session_id": session.id,
            "plan": plan,
            "trial_days": trial_days
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create checkout session: {str(e)}"
        )

@router.get("/plans")
async def get_plans():
    """Get all available pricing plans"""
    return {
        "plans": [
            {
                "id": plan_id,
                "name": plan_data["name"],
                "price": plan_data["price"] / 100,  # Convert cents to euros
                "currency": plan_data["currency"],
                "interval": plan_data["interval"],
                "features": plan_data["features"]
            }
            for plan_id, plan_data in PLANS.items()
        ]
    }

@router.post("/webhook")
async def stripe_webhook(request: Request):
    """Handle Stripe webhook events with Telegram notifications"""
    payload = await request.body()
    sig_header = request.headers.get('stripe-signature')
    
    try:
        event = stripe_manager.handle_webhook(payload, sig_header)
        event_type = event['type']
        
        # Handle specific events with Telegram notifications
        if event_type == 'checkout.session.completed':
            session = event['data']['object']
            email = session.get('customer_email', 'Unknown')
            plan = session.get('metadata', {}).get('plan_name', 'Unknown')
            
            # Send Telegram notification
            send_new_user_alert(
                email=email,
                trial_ends_at="7 days from now"
            )
            logger.info(f"New checkout completed: {email} - {plan}")
            
        elif event_type == 'invoice.payment_succeeded':
            invoice = event['data']['object']
            email = invoice.get('customer_email', 'Unknown')
            amount = invoice.get('amount_paid', 0) / 100  # Convert cents to euros
            currency = invoice.get('currency', 'EUR').upper()
            
            # Get plan from subscription
            plan = 'Unknown'
            if invoice.get('lines'):
                plan = invoice['lines']['data'][0].get('description', 'Unknown')
            
            # Send Telegram notification
            send_payment_success_alert(
                email=email,
                plan=plan,
                amount=amount,
                currency=currency
            )
            logger.info(f"Payment succeeded: {email} - {amount} {currency}")
            
        elif event_type == 'invoice.payment_failed':
            invoice = event['data']['object']
            email = invoice.get('customer_email', 'Unknown')
            plan = 'Unknown'
            if invoice.get('lines'):
                plan = invoice['lines']['data'][0].get('description', 'Unknown')
            
            reason = invoice.get('failure_message', 'Payment declined')
            
            # Send Telegram notification
            send_payment_failed_alert(
                email=email,
                plan=plan,
                reason=reason
            )
            logger.warning(f"Payment failed: {email} - {reason}")
        
        return {
            "status": "success",
            "event_type": event_type,
            "telegram_notified": True
        }
    except Exception as e:
        logger.error(f"Webhook error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.post("/create-promo-code")
async def create_promo_code(
    code: str,
    percent_off: int,
    duration: str = "once"
):
    """Create a promotional discount code"""
    try:
        promo = stripe_manager.create_promo_code(code, percent_off, duration)
        return {
            "code": promo.code,
            "percent_off": percent_off,
            "duration": duration,
            "active": promo.active
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create promo code: {str(e)}"
        )

@router.get("/subscription/{subscription_id}")
async def get_subscription(subscription_id: str):
    """Get subscription details"""
    try:
        subscription = stripe_manager.get_subscription(subscription_id)
        return {
            "id": subscription.id,
            "status": subscription.status,
            "current_period_end": subscription.current_period_end,
            "cancel_at_period_end": subscription.cancel_at_period_end,
            "plan": subscription.metadata.get('plan_name')
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Subscription not found: {str(e)}"
        )

@router.post("/subscription/{subscription_id}/cancel")
async def cancel_subscription(
    subscription_id: str,
    immediately: bool = False
):
    """Cancel a subscription"""
    try:
        subscription = stripe_manager.cancel_subscription(subscription_id, immediately)
        return {
            "status": "cancelled" if immediately else "will_cancel_at_period_end",
            "subscription_id": subscription.id
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cancel subscription: {str(e)}"
        )

