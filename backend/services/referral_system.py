from datetime import datetime
import hashlib
import random
import string

class ReferralSystem:
    """Referral program management"""
    
    def __init__(self):
        self.discount_percent = 10
        self.commission_percent = 20
    
    def generate_referral_code(self, user_id: int, user_email: str) -> str:
        """Generate unique referral code for user"""
        # Create code from user ID
        code = f"SSL{user_id:06d}"
        return code
    
    def generate_custom_code(self, custom_name: str) -> str:
        """Generate custom referral code"""
        # Clean and format custom name
        clean_name = ''.join(c for c in custom_name.upper() if c.isalnum())
        code = f"SSL_{clean_name[:10]}"
        return code
    
    def create_referral(self, user_id: int, user_email: str, custom_code: str = None):
        """Create referral entry for user"""
        if custom_code:
            code = self.generate_custom_code(custom_code)
        else:
            code = self.generate_referral_code(user_id, user_email)
        
        return {
            "user_id": user_id,
            "referral_code": code,
            "discount_percent": self.discount_percent,
            "commission_percent": self.commission_percent,
            "created_at": datetime.utcnow(),
            "total_referrals": 0,
            "total_revenue": 0,
            "active": True
        }
    
    def apply_referral_discount(self, referral_code: str, checkout_session_data: dict):
        """Apply discount when referral code is used"""
        # This would integrate with Stripe to apply the discount
        discount_data = {
            "referral_code": referral_code,
            "discount_percent": self.discount_percent,
            "applied_at": datetime.utcnow()
        }
        return discount_data
    
    def calculate_commission(self, subscription_amount: int) -> int:
        """Calculate commission for referrer"""
        commission = int(subscription_amount * self.commission_percent / 100)
        return commission
    
    def track_referral_signup(self, referral_code: str, new_user_email: str, 
                              subscription_plan: str, subscription_amount: int):
        """Track when someone signs up using referral code"""
        commission = self.calculate_commission(subscription_amount)
        
        return {
            "referral_code": referral_code,
            "new_user_email": new_user_email,
            "subscription_plan": subscription_plan,
            "subscription_amount": subscription_amount,
            "commission_earned": commission,
            "signup_date": datetime.utcnow(),
            "status": "pending"  # pending, paid, cancelled
        }
    
    def generate_referral_link(self, referral_code: str, base_url: str = "http://localhost"):
        """Generate referral link"""
        return f"{base_url}/pricing.html?ref={referral_code}"
    
    def get_referral_stats(self, user_id: int):
        """Get referral statistics for user"""
        # This would query database for actual stats
        return {
            "user_id": user_id,
            "referral_code": f"SSL{user_id:06d}",
            "total_referrals": 0,
            "successful_conversions": 0,
            "total_commission_earned": 0,
            "pending_commission": 0,
            "referral_link": self.generate_referral_link(f"SSL{user_id:06d}")
        }
    
    def validate_referral_code(self, referral_code: str) -> bool:
        """Validate if referral code exists and is active"""
        # This would check against database
        if referral_code.startswith("SSL") and len(referral_code) >= 9:
            return True
        return False

# Global instance
referral_system = ReferralSystem()

# Example usage:
if __name__ == '__main__':
    # Create referral for user
    referral = referral_system.create_referral(
        user_id=1,
        user_email="john@example.com"
    )
    print(f"Referral Code: {referral['referral_code']}")
    print(f"Referral Link: {referral_system.generate_referral_link(referral['referral_code'])}")
    
    # Track signup
    signup = referral_system.track_referral_signup(
        referral_code="SSL000001",
        new_user_email="jane@example.com",
        subscription_plan="professional",
        subscription_amount=4900  # €49 in cents
    )
    print(f"Commission Earned: €{signup['commission_earned']/100:.2f}")

