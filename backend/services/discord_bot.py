"""
Discord Bot Service for SSL Monitor Pro
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import discord
from discord.ext import commands, tasks
import aiohttp
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Domain, User, NotificationSettings
from ..config import settings

logger = logging.getLogger(__name__)

class SSLMonitorBot(commands.Bot):
    """Discord bot for SSL certificate monitoring"""
    
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.guilds = True
        intents.members = True
        
        super().__init__(
            command_prefix='!ssl ',
            intents=intents,
            help_command=None,
            description="SSL Monitor Pro - Professional SSL certificate monitoring bot"
        )
        
        self.db_session = next(get_db())
        self.initial_extensions = [
            'cogs.ssl_monitor',
            'cogs.server_management',
            'cogs.analytics',
            'cogs.notifications'
        ]
    
    async def setup_hook(self):
        """Called when the bot is starting up"""
        logger.info("SSL Monitor Bot is starting up...")
        
        # Load extensions
        for extension in self.initial_extensions:
            try:
                await self.load_extension(extension)
                logger.info(f"Loaded extension: {extension}")
            except Exception as e:
                logger.error(f"Failed to load extension {extension}: {e}")
        
        # Start background tasks
        self.ssl_monitor_task.start()
        self.cleanup_task.start()
    
    async def on_ready(self):
        """Called when the bot is ready"""
        logger.info(f'{self.user} has connected to Discord!')
        logger.info(f'Bot is in {len(self.guilds)} guilds')
        
        # Set bot presence
        activity = discord.Activity(
            type=discord.ActivityType.watching,
            name="SSL certificates"
        )
        await self.change_presence(activity=activity)
    
    async def on_guild_join(self, guild):
        """Called when the bot joins a new guild"""
        logger.info(f"Joined new guild: {guild.name} (ID: {guild.id})")
        
        # Send welcome message to system channel or first available channel
        channel = guild.system_channel or guild.text_channels[0]
        if channel:
            embed = self.create_welcome_embed()
            await channel.send(embed=embed)
    
    async def on_guild_remove(self, guild):
        """Called when the bot is removed from a guild"""
        logger.info(f"Left guild: {guild.name} (ID: {guild.id})")
    
    def create_welcome_embed(self) -> discord.Embed:
        """Create welcome embed for new servers"""
        embed = discord.Embed(
            title="🔐 SSL Monitor Pro",
            description="Thank you for adding SSL Monitor Pro to your server!",
            color=0x00ff00,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🚀 Getting Started",
            value="Use `!ssl help` to see all available commands",
            inline=False
        )
        
        embed.add_field(
            name="📋 Quick Commands",
            value=(
                "`!ssl add <domain>` - Add a domain to monitor\n"
                "`!ssl list` - List monitored domains\n"
                "`!ssl status <domain>` - Check SSL status\n"
                "`!ssl setup` - Configure notification settings"
            ),
            inline=False
        )
        
        embed.add_field(
            name="🔧 Configuration",
            value=(
                "`!ssl channel` - Set notification channel\n"
                "`!ssl role` - Set notification role\n"
                "`!ssl settings` - View current settings"
            ),
            inline=False
        )
        
        embed.set_footer(text="SSL Monitor Pro • Professional SSL Certificate Monitoring")
        
        return embed
    
    @tasks.loop(minutes=5)
    async def ssl_monitor_task(self):
        """Background task to monitor SSL certificates"""
        try:
            await self.check_ssl_certificates()
        except Exception as e:
            logger.error(f"Error in SSL monitor task: {e}")
    
    @tasks.loop(hours=24)
    async def cleanup_task(self):
        """Daily cleanup task"""
        try:
            await self.cleanup_old_data()
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
    
    async def check_ssl_certificates(self):
        """Check SSL certificates for all monitored domains"""
        try:
            domains = self.db_session.query(Domain).filter(Domain.is_active == True).all()
            
            for domain in domains:
                try:
                    # Check SSL certificate
                    ssl_info = await self.get_ssl_info(domain.name)
                    
                    if ssl_info:
                        # Update domain with new SSL info
                        domain.ssl_status = json.dumps(ssl_info)
                        domain.last_checked = datetime.utcnow()
                        
                        # Check if we need to send notifications
                        await self.check_notification_triggers(domain, ssl_info)
                    
                except Exception as e:
                    logger.error(f"Error checking domain {domain.name}: {e}")
            
            self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error in SSL certificate check: {e}")
    
    async def get_ssl_info(self, domain: str) -> Optional[Dict]:
        """Get SSL certificate information for a domain"""
        try:
            import ssl
            import socket
            from cryptography import x509
            from cryptography.hazmat.backends import default_backend
            
            # Connect to domain
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert_der = ssock.getpeercert_chain()[0]
                    cert = x509.load_der_x509_certificate(cert_der, default_backend())
                    
                    # Extract certificate information
                    not_after = cert.not_valid_after
                    not_before = cert.not_valid_before
                    issuer = cert.issuer.rfc4514_string()
                    subject = cert.subject.rfc4514_string()
                    
                    # Calculate days until expiry
                    days_until_expiry = (not_after - datetime.utcnow()).days
                    
                    return {
                        'is_valid': days_until_expiry > 0,
                        'expires_in': days_until_expiry,
                        'issuer': issuer,
                        'subject': subject,
                        'not_valid_after': not_after.isoformat(),
                        'not_valid_before': not_before.isoformat(),
                        'checked_at': datetime.utcnow().isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Error getting SSL info for {domain}: {e}")
            return None
    
    async def check_notification_triggers(self, domain: Domain, ssl_info: Dict):
        """Check if we need to send notifications for a domain"""
        try:
            expires_in = ssl_info.get('expires_in', 0)
            
            # Get notification settings for this domain
            notification_settings = self.db_session.query(NotificationSettings).filter(
                NotificationSettings.domain_id == domain.id
            ).first()
            
            if not notification_settings:
                return
            
            # Check notification triggers
            if expires_in <= 0:
                await self.send_ssl_expired_notification(domain, ssl_info)
            elif expires_in <= 7:
                await self.send_ssl_critical_notification(domain, ssl_info)
            elif expires_in <= 30:
                await self.send_ssl_warning_notification(domain, ssl_info)
            
        except Exception as e:
            logger.error(f"Error checking notification triggers for {domain.name}: {e}")
    
    async def send_ssl_expired_notification(self, domain: Domain, ssl_info: Dict):
        """Send SSL expired notification"""
        embed = self.create_ssl_alert_embed(
            title="🚨 SSL Certificate Expired",
            description=f"SSL certificate for **{domain.name}** has expired!",
            color=0xff0000,
            domain=domain,
            ssl_info=ssl_info
        )
        
        await self.send_notification(domain, embed, priority="critical")
    
    async def send_ssl_critical_notification(self, domain: Domain, ssl_info: Dict):
        """Send SSL critical notification"""
        expires_in = ssl_info.get('expires_in', 0)
        
        embed = self.create_ssl_alert_embed(
            title="⚠️ SSL Certificate Expiring Soon",
            description=f"SSL certificate for **{domain.name}** expires in **{expires_in} days**!",
            color=0xff8c00,
            domain=domain,
            ssl_info=ssl_info
        )
        
        await self.send_notification(domain, embed, priority="high")
    
    async def send_ssl_warning_notification(self, domain: Domain, ssl_info: Dict):
        """Send SSL warning notification"""
        expires_in = ssl_info.get('expires_in', 0)
        
        embed = self.create_ssl_alert_embed(
            title="⚠️ SSL Certificate Expiring",
            description=f"SSL certificate for **{domain.name}** expires in **{expires_in} days**",
            color=0xffa500,
            domain=domain,
            ssl_info=ssl_info
        )
        
        await self.send_notification(domain, embed, priority="medium")
    
    def create_ssl_alert_embed(self, title: str, description: str, color: int, 
                              domain: Domain, ssl_info: Dict) -> discord.Embed:
        """Create SSL alert embed"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="🌐 Domain",
            value=domain.name,
            inline=True
        )
        
        embed.add_field(
            name="⏰ Expires In",
            value=f"{ssl_info.get('expires_in', 0)} days",
            inline=True
        )
        
        embed.add_field(
            name="📅 Expiry Date",
            value=datetime.fromisoformat(ssl_info.get('not_valid_after', '')).strftime('%Y-%m-%d'),
            inline=True
        )
        
        embed.add_field(
            name="🏢 Issuer",
            value=ssl_info.get('issuer', 'Unknown'),
            inline=False
        )
        
        embed.add_field(
            name="🔗 Subject",
            value=ssl_info.get('subject', 'Unknown'),
            inline=False
        )
        
        embed.set_footer(text="SSL Monitor Pro • Click to view details")
        
        return embed
    
    async def send_notification(self, domain: Domain, embed: discord.Embed, priority: str = "medium"):
        """Send notification to configured Discord channel"""
        try:
            # Get notification settings
            notification_settings = self.db_session.query(NotificationSettings).filter(
                NotificationSettings.domain_id == domain.id
            ).first()
            
            if not notification_settings or not notification_settings.discord_enabled:
                return
            
            # Get Discord channel
            channel_id = notification_settings.discord_channel_id
            if not channel_id:
                return
            
            channel = self.get_channel(int(channel_id))
            if not channel:
                logger.error(f"Discord channel {channel_id} not found")
                return
            
            # Prepare notification message
            message_content = ""
            
            # Add role mention for critical alerts
            if priority == "critical" and notification_settings.discord_role_id:
                role = channel.guild.get_role(int(notification_settings.discord_role_id))
                if role:
                    message_content += f"{role.mention} "
            
            # Send notification
            await channel.send(content=message_content, embed=embed)
            
            logger.info(f"Sent {priority} notification for domain {domain.name}")
            
        except Exception as e:
            logger.error(f"Error sending notification for domain {domain.name}: {e}")
    
    async def cleanup_old_data(self):
        """Clean up old data and logs"""
        try:
            # Clean up old notification logs (older than 30 days)
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            # Add cleanup logic here if needed
            
            logger.info("Cleanup task completed")
            
        except Exception as e:
            logger.error(f"Error in cleanup task: {e}")
    
    async def close(self):
        """Clean shutdown of the bot"""
        logger.info("SSL Monitor Bot is shutting down...")
        
        # Cancel background tasks
        self.ssl_monitor_task.cancel()
        self.cleanup_task.cancel()
        
        # Close database session
        self.db_session.close()
        
        await super().close()

# Create bot instance
bot = SSLMonitorBot()

async def start_bot():
    """Start the Discord bot"""
    try:
        await bot.start(settings.DISCORD_BOT_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start Discord bot: {e}")

def run_bot():
    """Run the Discord bot"""
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")

if __name__ == "__main__":
    run_bot()
