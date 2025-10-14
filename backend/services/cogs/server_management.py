"""
Server Management Cog - Server configuration and management commands
"""

import logging
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Domain, NotificationSettings

logger = logging.getLogger(__name__)

class ServerManagementCog(commands.Cog):
    """Server management commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='setup')
    @commands.has_permissions(manage_channels=True)
    async def setup_server(self, ctx):
        """Setup SSL monitoring for this server"""
        try:
            db: Session = next(get_db())
            
            embed = discord.Embed(
                title="⚙️ Server Setup",
                description="Setting up SSL monitoring for this server...",
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            # Check if server is already configured
            existing_settings = db.query(NotificationSettings).filter(
                NotificationSettings.discord_channel_id == str(ctx.channel.id)
            ).first()
            
            if existing_settings:
                embed.add_field(
                    name="ℹ️ Already Configured",
                    value="This server is already configured for SSL monitoring.",
                    inline=False
                )
                await ctx.send(embed=embed)
                return
            
            # Create default notification settings for this channel
            default_settings = NotificationSettings(
                domain_id=None,  # Global server settings
                discord_enabled=True,
                discord_channel_id=str(ctx.channel.id),
                discord_role_id=None,
                alert_threshold_days=30
            )
            
            db.add(default_settings)
            db.commit()
            
            embed.add_field(
                name="✅ Setup Complete",
                value="SSL monitoring has been configured for this server.",
                inline=False
            )
            
            embed.add_field(
                name="📋 Default Settings",
                value=(
                    f"**Notification Channel:** {ctx.channel.mention}\n"
                    f"**Alert Threshold:** 30 days\n"
                    f"**Notifications:** Enabled\n"
                    f"**Role Mentions:** None"
                ),
                inline=False
            )
            
            embed.add_field(
                name="🚀 Next Steps",
                value=(
                    "1. Use `!ssl add <domain>` to add domains to monitor\n"
                    "2. Use `!ssl channel` to change notification channel\n"
                    "3. Use `!ssl role` to set notification role\n"
                    "4. Use `!ssl settings` to view current settings"
                ),
                inline=False
            )
            
            embed.set_footer(text="Use !ssl help for more commands")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error setting up server: {e}")
            embed = discord.Embed(
                title="❌ Setup Failed",
                description="Failed to setup SSL monitoring. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='channel')
    @commands.has_permissions(manage_channels=True)
    async def set_channel(self, ctx, channel: Optional[discord.TextChannel] = None):
        """Set the notification channel for SSL alerts"""
        try:
            if not channel:
                channel = ctx.channel
            
            db: Session = next(get_db())
            
            # Update notification settings for this server
            settings = db.query(NotificationSettings).filter(
                NotificationSettings.discord_channel_id == str(ctx.channel.id)
            ).all()
            
            if not settings:
                # Create new settings if none exist
                new_settings = NotificationSettings(
                    domain_id=None,
                    discord_enabled=True,
                    discord_channel_id=str(channel.id),
                    discord_role_id=None,
                    alert_threshold_days=30
                )
                db.add(new_settings)
            else:
                # Update existing settings
                for setting in settings:
                    setting.discord_channel_id = str(channel.id)
            
            db.commit()
            
            embed = discord.Embed(
                title="✅ Notification Channel Set",
                description=f"SSL alerts will now be sent to {channel.mention}",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📋 Channel Information",
                value=(
                    f"**Channel:** {channel.mention}\n"
                    f"**Channel ID:** {channel.id}\n"
                    f"**Server:** {channel.guild.name}"
                ),
                inline=False
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error setting notification channel: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to set notification channel. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='role')
    @commands.has_permissions(manage_roles=True)
    async def set_role(self, ctx, role: Optional[discord.Role] = None):
        """Set the role to mention for critical SSL alerts"""
        try:
            db: Session = next(get_db())
            
            # Update notification settings for this server
            settings = db.query(NotificationSettings).filter(
                NotificationSettings.discord_channel_id == str(ctx.channel.id)
            ).all()
            
            role_id = str(role.id) if role else None
            
            if not settings:
                # Create new settings if none exist
                new_settings = NotificationSettings(
                    domain_id=None,
                    discord_enabled=True,
                    discord_channel_id=str(ctx.channel.id),
                    discord_role_id=role_id,
                    alert_threshold_days=30
                )
                db.add(new_settings)
            else:
                # Update existing settings
                for setting in settings:
                    setting.discord_role_id = role_id
            
            db.commit()
            
            if role:
                embed = discord.Embed(
                    title="✅ Notification Role Set",
                    description=f"Critical SSL alerts will now mention {role.mention}",
                    color=0x00ff00,
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="📋 Role Information",
                    value=(
                        f"**Role:** {role.mention}\n"
                        f"**Role ID:** {role.id}\n"
                        f"**Mentioned For:** Critical alerts only"
                    ),
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title="✅ Notification Role Removed",
                    description="No role will be mentioned for SSL alerts",
                    color=0xffa500,
                    timestamp=datetime.utcnow()
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error setting notification role: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to set notification role. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='settings')
    async def view_settings(self, ctx):
        """View current server settings"""
        try:
            db: Session = next(get_db())
            
            # Get server settings
            settings = db.query(NotificationSettings).filter(
                NotificationSettings.discord_channel_id == str(ctx.channel.id)
            ).first()
            
            # Get domains for this server
            domains = db.query(Domain).filter(Domain.is_active == True).all()
            
            embed = discord.Embed(
                title="⚙️ Server Settings",
                description=f"SSL monitoring configuration for {ctx.guild.name}",
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            if settings:
                channel = self.bot.get_channel(int(settings.discord_channel_id)) if settings.discord_channel_id else None
                role = ctx.guild.get_role(int(settings.discord_role_id)) if settings.discord_role_id else None
                
                embed.add_field(
                    name="📋 Notification Settings",
                    value=(
                        f"**Channel:** {channel.mention if channel else 'Not set'}\n"
                        f"**Role:** {role.mention if role else 'None'}\n"
                        f"**Enabled:** {'Yes' if settings.discord_enabled else 'No'}\n"
                        f"**Alert Threshold:** {settings.alert_threshold_days} days"
                    ),
                    inline=False
                )
            else:
                embed.add_field(
                    name="⚠️ Not Configured",
                    value="This server is not configured for SSL monitoring.\nUse `!ssl setup` to configure.",
                    inline=False
                )
            
            embed.add_field(
                name="📊 Statistics",
                value=(
                    f"**Monitored Domains:** {len(domains)}\n"
                    f"**Active Domains:** {len([d for d in domains if d.is_active])}\n"
                    f"**Server Members:** {ctx.guild.member_count}"
                ),
                inline=False
            )
            
            if domains:
                domain_list = "\n".join([f"• {domain.name}" for domain in domains[:10]])
                if len(domains) > 10:
                    domain_list += f"\n• ... and {len(domains) - 10} more"
                
                embed.add_field(
                    name="🌐 Monitored Domains",
                    value=domain_list,
                    inline=False
                )
            
            embed.set_footer(text="Use !ssl setup to configure monitoring")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error viewing settings: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve settings. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='disable')
    @commands.has_permissions(manage_channels=True)
    async def disable_notifications(self, ctx):
        """Disable SSL notifications for this server"""
        try:
            db: Session = next(get_db())
            
            # Update notification settings
            settings = db.query(NotificationSettings).filter(
                NotificationSettings.discord_channel_id == str(ctx.channel.id)
            ).all()
            
            if settings:
                for setting in settings:
                    setting.discord_enabled = False
                db.commit()
                
                embed = discord.Embed(
                    title="✅ Notifications Disabled",
                    description="SSL notifications have been disabled for this server",
                    color=0xffa500,
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="ℹ️ Information",
                    value="Domains will still be monitored, but no notifications will be sent.",
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title="⚠️ Not Configured",
                    value="This server is not configured for SSL monitoring.",
                    color=0xffa500
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error disabling notifications: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to disable notifications. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='enable')
    @commands.has_permissions(manage_channels=True)
    async def enable_notifications(self, ctx):
        """Enable SSL notifications for this server"""
        try:
            db: Session = next(get_db())
            
            # Update notification settings
            settings = db.query(NotificationSettings).filter(
                NotificationSettings.discord_channel_id == str(ctx.channel.id)
            ).all()
            
            if settings:
                for setting in settings:
                    setting.discord_enabled = True
                db.commit()
                
                embed = discord.Embed(
                    title="✅ Notifications Enabled",
                    description="SSL notifications have been enabled for this server",
                    color=0x00ff00,
                    timestamp=datetime.utcnow()
                )
            else:
                embed = discord.Embed(
                    title="⚠️ Not Configured",
                    value="This server is not configured for SSL monitoring.\nUse `!ssl setup` to configure.",
                    color=0xffa500
                )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error enabling notifications: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to enable notifications. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='threshold')
    @commands.has_permissions(manage_channels=True)
    async def set_threshold(self, ctx, days: int):
        """Set the alert threshold in days"""
        try:
            if days < 1 or days > 365:
                embed = discord.Embed(
                    title="❌ Invalid Threshold",
                    description="Alert threshold must be between 1 and 365 days",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            db: Session = next(get_db())
            
            # Update notification settings
            settings = db.query(NotificationSettings).filter(
                NotificationSettings.discord_channel_id == str(ctx.channel.id)
            ).all()
            
            if settings:
                for setting in settings:
                    setting.alert_threshold_days = days
                db.commit()
                
                embed = discord.Embed(
                    title="✅ Alert Threshold Updated",
                    description=f"Alert threshold set to {days} days",
                    color=0x00ff00,
                    timestamp=datetime.utcnow()
                )
                
                embed.add_field(
                    name="ℹ️ Information",
                    value=f"SSL certificates will trigger alerts {days} days before expiry.",
                    inline=False
                )
            else:
                embed = discord.Embed(
                    title="⚠️ Not Configured",
                    value="This server is not configured for SSL monitoring.\nUse `!ssl setup` to configure.",
                    color=0xffa500
                )
            
            await ctx.send(embed=embed)
            
        except ValueError:
            embed = discord.Embed(
                title="❌ Invalid Input",
                description="Please provide a valid number of days",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        except Exception as e:
            logger.error(f"Error setting threshold: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to set alert threshold. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='info')
    async def bot_info(self, ctx):
        """Show bot information"""
        embed = discord.Embed(
            title="🔐 SSL Monitor Pro",
            description="Professional SSL certificate monitoring bot",
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📊 Statistics",
            value=(
                f"**Servers:** {len(self.bot.guilds)}\n"
                f"**Users:** {len(self.bot.users)}\n"
                f"**Uptime:** {self.get_uptime()}\n"
                f"**Latency:** {round(self.bot.latency * 1000)}ms"
            ),
            inline=True
        )
        
        embed.add_field(
            name="🔧 Features",
            value=(
                "• Real-time SSL monitoring\n"
                "• Customizable alerts\n"
                "• Rich notifications\n"
                "• Role mentions\n"
                "• Detailed analytics"
            ),
            inline=True
        )
        
        embed.add_field(
            name="📋 Commands",
            value=(
                "• `!ssl add <domain>` - Add domain\n"
                "• `!ssl list` - List domains\n"
                "• `!ssl status <domain>` - Check status\n"
                "• `!ssl setup` - Configure server\n"
                "• `!ssl help` - Show all commands"
            ),
            inline=False
        )
        
        embed.set_footer(text="SSL Monitor Pro • Professional SSL Certificate Monitoring")
        
        await ctx.send(embed=embed)
    
    def get_uptime(self) -> str:
        """Get bot uptime"""
        uptime = datetime.utcnow() - self.bot.start_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        if days > 0:
            return f"{days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m {seconds}s"

async def setup(bot):
    """Setup the cog"""
    await bot.add_cog(ServerManagementCog(bot))
