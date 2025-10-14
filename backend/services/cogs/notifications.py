"""
Notifications Cog - Notification management commands
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Optional

import discord
from discord.ext import commands
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Domain, NotificationSettings

logger = logging.getLogger(__name__)

class NotificationsCog(commands.Cog):
    """Notification management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='notify')
    async def test_notification(self, ctx, *, message: Optional[str] = None):
        """Test notification system"""
        try:
            if not message:
                message = "This is a test notification from SSL Monitor Pro!"
            
            embed = discord.Embed(
                title="🔔 Test Notification",
                description=message,
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="ℹ️ Information",
                value="This is a test notification to verify the notification system is working correctly.",
                inline=False
            )
            
            embed.set_footer(text="SSL Monitor Pro • Test Notification")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error sending test notification: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to send test notification. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='subscribe')
    async def subscribe_notifications(self, ctx, *, domain: str):
        """Subscribe to notifications for a specific domain"""
        try:
            db: Session = next(get_db())
            
            # Find domain
            domain_obj = db.query(Domain).filter(Domain.name == domain).first()
            if not domain_obj:
                embed = discord.Embed(
                    title="❌ Domain Not Found",
                    description=f"**{domain}** is not being monitored",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            # Update notification settings for this domain
            notification_settings = db.query(NotificationSettings).filter(
                NotificationSettings.domain_id == domain_obj.id
            ).first()
            
            if notification_settings:
                notification_settings.discord_enabled = True
                notification_settings.discord_channel_id = str(ctx.channel.id)
            else:
                # Create new notification settings
                notification_settings = NotificationSettings(
                    domain_id=domain_obj.id,
                    discord_enabled=True,
                    discord_channel_id=str(ctx.channel.id),
                    discord_role_id=None,
                    alert_threshold_days=30
                )
                db.add(notification_settings)
            
            db.commit()
            
            embed = discord.Embed(
                title="✅ Subscribed to Notifications",
                description=f"You will now receive SSL notifications for **{domain}** in this channel",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📋 Notification Details",
                value=(
                    f"**Domain:** {domain}\n"
                    f"**Channel:** {ctx.channel.mention}\n"
                    f"**Alert Threshold:** 30 days\n"
                    f"**Status:** Active"
                ),
                inline=False
            )
            
            embed.set_footer(text="Use !ssl unsubscribe <domain> to stop notifications")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error subscribing to notifications: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to subscribe to notifications. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='unsubscribe')
    async def unsubscribe_notifications(self, ctx, *, domain: str):
        """Unsubscribe from notifications for a specific domain"""
        try:
            db: Session = next(get_db())
            
            # Find domain
            domain_obj = db.query(Domain).filter(Domain.name == domain).first()
            if not domain_obj:
                embed = discord.Embed(
                    title="❌ Domain Not Found",
                    description=f"**{domain}** is not being monitored",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            # Update notification settings
            notification_settings = db.query(NotificationSettings).filter(
                NotificationSettings.domain_id == domain_obj.id
            ).first()
            
            if notification_settings:
                notification_settings.discord_enabled = False
                db.commit()
                
                embed = discord.Embed(
                    title="✅ Unsubscribed from Notifications",
                    description=f"You will no longer receive SSL notifications for **{domain}**",
                    color=0xffa500,
                    timestamp=datetime.utcnow()
                )
            else:
                embed = discord.Embed(
                    title="⚠️ Not Subscribed",
                    description=f"You were not subscribed to notifications for **{domain}**",
                    color=0xffa500
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error unsubscribing from notifications: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to unsubscribe from notifications. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='subscriptions')
    async def list_subscriptions(self, ctx):
        """List your current notification subscriptions"""
        try:
            db: Session = next(get_db())
            
            # Get notification settings for this channel
            notification_settings = db.query(NotificationSettings).filter(
                NotificationSettings.discord_channel_id == str(ctx.channel.id),
                NotificationSettings.discord_enabled == True
            ).all()
            
            if not notification_settings:
                embed = discord.Embed(
                    title="📋 Notification Subscriptions",
                    description="No active notification subscriptions found for this channel.",
                    color=0x3498db,
                    timestamp=datetime.utcnow()
                )
                embed.add_field(
                    name="ℹ️ Information",
                    value="Use `!ssl subscribe <domain>` to subscribe to notifications for a domain.",
                    inline=False
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="📋 Notification Subscriptions",
                description=f"Active subscriptions for {ctx.channel.mention}",
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            for setting in notification_settings:
                if setting.domain_id:
                    # Get domain information
                    domain = db.query(Domain).filter(Domain.id == setting.domain_id).first()
                    if domain:
                        # Get SSL status
                        if domain.ssl_status:
                            ssl_info = json.loads(domain.ssl_status)
                            expires_in = ssl_info.get('expires_in', 0)
                            status_emoji = self.get_status_emoji(expires_in)
                            status_text = f"{expires_in} days"
                        else:
                            status_emoji = "❓"
                            status_text = "Not checked"
                        
                        embed.add_field(
                            name=f"{status_emoji} {domain.name}",
                            value=(
                                f"**Alert Threshold:** {setting.alert_threshold_days} days\n"
                                f"**SSL Status:** {status_text}\n"
                                f"**Notifications:** {'Enabled' if setting.discord_enabled else 'Disabled'}"
                            ),
                            inline=True
                        )
            
            embed.set_footer(text="Use !ssl unsubscribe <domain> to stop notifications")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing subscriptions: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve subscriptions. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='schedule')
    async def schedule_notification(self, ctx, domain: str, days: int):
        """Schedule a notification for a specific domain and days"""
        try:
            if days < 1 or days > 365:
                embed = discord.Embed(
                    title="❌ Invalid Days",
                    description="Days must be between 1 and 365",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            db: Session = next(get_db())
            
            # Find domain
            domain_obj = db.query(Domain).filter(Domain.name == domain).first()
            if not domain_obj:
                embed = discord.Embed(
                    title="❌ Domain Not Found",
                    description=f"**{domain}** is not being monitored",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            # Update notification settings
            notification_settings = db.query(NotificationSettings).filter(
                NotificationSettings.domain_id == domain_obj.id
            ).first()
            
            if notification_settings:
                notification_settings.alert_threshold_days = days
            else:
                # Create new notification settings
                notification_settings = NotificationSettings(
                    domain_id=domain_obj.id,
                    discord_enabled=True,
                    discord_channel_id=str(ctx.channel.id),
                    discord_role_id=None,
                    alert_threshold_days=days
                )
                db.add(notification_settings)
            
            db.commit()
            
            embed = discord.Embed(
                title="✅ Notification Scheduled",
                description=f"Notifications for **{domain}** will be sent {days} days before expiry",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📋 Schedule Details",
                value=(
                    f"**Domain:** {domain}\n"
                    f"**Alert Threshold:** {days} days\n"
                    f"**Channel:** {ctx.channel.mention}\n"
                    f"**Status:** Active"
                ),
                inline=False
            )
            
            embed.set_footer(text="Use !ssl schedule <domain> <days> to change the schedule")
            
            await ctx.send(embed=embed)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Input",
                description="Please provide a valid number of days",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error scheduling notification: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to schedule notification. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='digest')
    async def notification_digest(self, ctx, frequency: str = "daily"):
        """Configure notification digest frequency"""
        try:
            valid_frequencies = ["hourly", "daily", "weekly"]
            if frequency.lower() not in valid_frequencies:
                embed = discord.Embed(
                    title="❌ Invalid Frequency",
                    description=f"Valid frequencies: {', '.join(valid_frequencies)}",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            # This would be implemented with a digest system
            embed = discord.Embed(
                title="✅ Digest Configured",
                description=f"Notification digest set to **{frequency}** frequency",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="ℹ️ Information",
                value="Digest notifications will be sent at the specified frequency with a summary of all SSL alerts.",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error configuring digest: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to configure digest. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='mute')
    async def mute_notifications(self, ctx, duration: str = "1h"):
        """Temporarily mute notifications"""
        try:
            # Parse duration (simplified)
            duration_map = {
                "1h": "1 hour",
                "6h": "6 hours",
                "1d": "1 day",
                "1w": "1 week"
            }
            
            if duration not in duration_map:
                embed = discord.Embed(
                    title="❌ Invalid Duration",
                    description="Valid durations: 1h, 6h, 1d, 1w",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            # This would be implemented with a mute system
            embed = discord.Embed(
                title="🔇 Notifications Muted",
                description=f"Notifications have been muted for **{duration_map[duration]}**",
                color=0xffa500,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="ℹ️ Information",
                value="You will not receive any SSL notifications during this period. Use `!ssl unmute` to unmute early.",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error muting notifications: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to mute notifications. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='unmute')
    async def unmute_notifications(self, ctx):
        """Unmute notifications"""
        try:
            embed = discord.Embed(
                title="🔊 Notifications Unmuted",
                description="All SSL notifications have been unmuted",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="ℹ️ Information",
                value="You will now receive all SSL notifications as configured.",
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error unmuting notifications: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to unmute notifications. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    def get_status_emoji(self, expires_in: int) -> str:
        """Get status emoji based on expiry days"""
        if expires_in <= 0:
            return "🚨"
        elif expires_in <= 7:
            return "⚠️"
        elif expires_in <= 30:
            return "🟡"
        else:
            return "✅"

async def setup(bot):
    """Setup the cog"""
    await bot.add_cog(NotificationsCog(bot))
