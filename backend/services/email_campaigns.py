import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Email configuration
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', '587'))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'noreply@sslmonitor.pro')

class EmailCampaigns:
    """Email marketing and engagement campaigns"""
    
    def __init__(self):
        self.smtp_host = SMTP_HOST
        self.smtp_port = SMTP_PORT
        self.smtp_user = SMTP_USER
        self.smtp_password = SMTP_PASSWORD
        self.from_email = FROM_EMAIL
    
    def send_email(self, to_email: str, subject: str, html_body: str, text_body: str = None):
        """Send an email"""
        try:
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text version
            if text_body:
                part1 = MIMEText(text_body, 'plain')
                msg.attach(part1)
            
            # Add HTML version
            part2 = MIMEText(html_body, 'html')
            msg.attach(part2)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                if self.smtp_user and self.smtp_password:
                    server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            logger.info(f"Email sent to {to_email}: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    def send_welcome_email(self, user_email: str, user_name: str = None):
        """Send welcome email after signup"""
        subject = "🚀 Welcome to SSL Monitor Pro!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .steps {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .step {{ margin: 15px 0; padding: 15px; border-left: 4px solid #667eea; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to SSL Monitor Pro!</h1>
                    <p>Your SSL certificate monitoring starts now</p>
                </div>
                <div class="content">
                    <p>Hi{' ' + user_name if user_name else ''}!</p>
                    
                    <p>Thanks for starting your 7-day free trial. You now have access to professional SSL certificate monitoring that will help you avoid costly downtime.</p>
                    
                    <div class="steps">
                        <h3>🚀 Get Started in 3 Easy Steps:</h3>
                        
                        <div class="step">
                            <strong>1. Add Your First Domain</strong><br>
                            Go to your dashboard and add the domains you want to monitor. We'll immediately check their SSL certificates.
                        </div>
                        
                        <div class="step">
                            <strong>2. Configure Alert Channels</strong><br>
                            Set up Telegram, Slack, or email notifications so you never miss an expiring certificate.
                        </div>
                        
                        <div class="step">
                            <strong>3. Invite Your Team</strong><br>
                            Collaborate with your team members and ensure everyone stays informed.
                        </div>
                    </div>
                    
                    <center>
                        <a href="http://localhost/index.html" class="cta-button">Go to Dashboard →</a>
                    </center>
                    
                    <h3>💡 Pro Tips:</h3>
                    <ul>
                        <li>Set alert thresholds to 30 days for critical sites</li>
                        <li>Use API access to integrate with your existing tools</li>
                        <li>Check the history tab to track certificate changes</li>
                    </ul>
                    
                    <p>Need help? Just reply to this email - we're here to help!</p>
                    
                    <p>Best regards,<br>
                    The SSL Monitor Pro Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Welcome to SSL Monitor Pro!
        
        Hi{' ' + user_name if user_name else ''}!
        
        Thanks for starting your 7-day free trial. Here's how to get started:
        
        1. Add Your First Domain
        Go to your dashboard and add the domains you want to monitor.
        
        2. Configure Alert Channels
        Set up Telegram, Slack, or email notifications.
        
        3. Invite Your Team
        Collaborate with your team members.
        
        Dashboard: http://localhost/index.html
        
        Need help? Reply to this email!
        
        Best regards,
        The SSL Monitor Pro Team
        """
        
        return self.send_email(user_email, subject, html_body, text_body)
    
    def send_trial_ending_reminder(self, user_email: str, days_left: int, user_name: str = None):
        """Send reminder when trial is ending"""
        subject = f"⏰ Your SSL Monitor trial ends in {days_left} days"
        
        discount_code = "SAVE20" if days_left <= 3 else None
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #ff6b6b; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; font-weight: bold; }}
                .stats {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .promo {{ background: #00d4aa; color: white; padding: 15px; border-radius: 8px; text-align: center; font-size: 1.2rem; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>⏰ Don't Lose Your Setup!</h1>
                    <p>Your trial ends in {days_left} days</p>
                </div>
                <div class="content">
                    <p>Hi{' ' + user_name if user_name else ''}!</p>
                    
                    <p>Your SSL Monitor Pro trial is ending soon. Don't lose access to:</p>
                    
                    <div class="stats">
                        <h3>Your SSL Monitoring Setup:</h3>
                        <ul>
                            <li>✓ All your configured domains</li>
                            <li>✓ Alert channels and notifications</li>
                            <li>✓ Historical SSL certificate data</li>
                            <li>✓ Team members and permissions</li>
                        </ul>
                    </div>
                    
                    {f'''
                    <div class="promo">
                        🎉 Special Offer: Use code <strong>{discount_code}</strong> for 20% off!
                    </div>
                    ''' if discount_code else ''}
                    
                    <center>
                        <a href="http://localhost/pricing.html" class="cta-button">Upgrade Now →</a>
                    </center>
                    
                    <p>Keep your websites secure and avoid costly SSL expiry incidents.</p>
                    
                    <p>Questions? We're here to help!</p>
                    
                    <p>Best regards,<br>
                    The SSL Monitor Pro Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
        Your SSL Monitor trial ends in {days_left} days
        
        Hi{' ' + user_name if user_name else ''}!
        
        Don't lose your SSL monitoring setup:
        - All your configured domains
        - Alert channels and notifications
        - Historical SSL certificate data
        - Team members and permissions
        
        {'Special Offer: Use code ' + discount_code + ' for 20% off!' if discount_code else ''}
        
        Upgrade now: http://localhost/pricing.html
        
        Best regards,
        The SSL Monitor Pro Team
        """
        
        return self.send_email(user_email, subject, html_body, text_body)
    
    def send_ssl_expiry_alert(self, user_email: str, domain: str, days_left: int):
        """Send alert when SSL certificate is expiring"""
        urgency = "🚨 CRITICAL" if days_left <= 7 else "⚠️ WARNING"
        subject = f"{urgency}: SSL certificate for {domain} expires in {days_left} days"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {'#ef4444' if days_left <= 7 else '#f59e0b'}; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .domain-box {{ background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid {'#ef4444' if days_left <= 7 else '#f59e0b'}; }}
                .cta-button {{ display: inline-block; background: #667eea; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{urgency}</h1>
                    <h2>SSL Certificate Expiring Soon</h2>
                </div>
                <div class="content">
                    <div class="domain-box">
                        <h3>🌐 Domain: {domain}</h3>
                        <p><strong>Expires in: {days_left} days</strong></p>
                        <p>Take action now to avoid downtime and security warnings!</p>
                    </div>
                    
                    <h3>Immediate Actions:</h3>
                    <ol>
                        <li>Renew your SSL certificate</li>
                        <li>Install the new certificate</li>
                        <li>Verify installation in SSL Monitor dashboard</li>
                    </ol>
                    
                    <center>
                        <a href="http://localhost/index.html" class="cta-button">View Dashboard →</a>
                    </center>
                    
                    <p><small>This is an automated alert from SSL Monitor Pro</small></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_body)
    
    def send_upgrade_success(self, user_email: str, plan: str):
        """Send email after successful upgrade"""
        subject = "🎉 Welcome to SSL Monitor Pro!"
        
        html_body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #00d4aa; color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Payment Successful!</h1>
                    <p>Welcome to the {plan.capitalize()} plan</p>
                </div>
                <div class="content">
                    <p>Thank you for upgrading to SSL Monitor Pro {plan.capitalize()} plan!</p>
                    
                    <p>Your payment has been processed successfully. You now have full access to all premium features.</p>
                    
                    <p>Receipt and invoice have been sent to your email.</p>
                    
                    <p>If you have any questions, don't hesitate to reach out!</p>
                    
                    <p>Best regards,<br>
                    The SSL Monitor Pro Team</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(user_email, subject, html_body)

# Global instance
email_campaigns = EmailCampaigns()

