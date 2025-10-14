"""
SSL Monitor Cog - Core SSL monitoring commands
"""

import json
import logging
from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Domain, User, NotificationSettings

logger = logging.getLogger(__name__)

class SSLMonitorCog(commands.Cog):
    """SSL monitoring commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='add', aliases=['monitor'])
    async def add_domain(self, ctx, *, domain: str):
        """Add a domain to monitor"""
        try:
            # Validate domain format
            if not self.is_valid_domain(domain):
                embed = discord.Embed(
                    title="❌ Invalid Domain",
                    description="Please provide a valid domain name (e.g., example.com)",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            db: Session = next(get_db())
            
            # Check if domain already exists
            existing_domain = db.query(Domain).filter(Domain.name == domain).first()
            if existing_domain:
                embed = discord.Embed(
                    title="⚠️ Domain Already Exists",
                    description=f"**{domain}** is already being monitored",
                    color=0xffa500
                )
                await ctx.send(embed=embed)
                return
            
            # Create new domain
            new_domain = Domain(
                name=domain,
                is_active=True,
                alert_threshold_days=30,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(new_domain)
            db.commit()
            db.refresh(new_domain)
            
            # Create notification settings
            notification_settings = NotificationSettings(
                domain_id=new_domain.id,
                discord_enabled=True,
                discord_channel_id=str(ctx.channel.id),
                discord_role_id=None,
                alert_threshold_days=30
            )
            
            db.add(notification_settings)
            db.commit()
            
            embed = discord.Embed(
                title="✅ Domain Added",
                description=f"**{domain}** has been added to monitoring",
                color=0x00ff00,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📋 Details",
                value=(
                    f"**Domain:** {domain}\n"
                    f"**Alert Threshold:** 30 days\n"
                    f"**Channel:** {ctx.channel.mention}\n"
                    f"**Status:** Active"
                ),
                inline=False
            )
            
            embed.set_footer(text="Use !ssl status <domain> to check SSL status")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error adding domain {domain}: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to add domain. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='remove', aliases=['unmonitor'])
    async def remove_domain(self, ctx, *, domain: str):
        """Remove a domain from monitoring"""
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
            
            # Delete domain and its notification settings
            db.query(NotificationSettings).filter(
                NotificationSettings.domain_id == domain_obj.id
            ).delete()
            
            db.delete(domain_obj)
            db.commit()
            
            embed = discord.Embed(
                title="✅ Domain Removed",
                description=f"**{domain}** has been removed from monitoring",
                color=0x00ff00
            )
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error removing domain {domain}: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to remove domain. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='list', aliases=['domains'])
    async def list_domains(self, ctx):
        """List all monitored domains"""
        try:
            db: Session = next(get_db())
            
            domains = db.query(Domain).filter(Domain.is_active == True).all()
            
            if not domains:
                embed = discord.Embed(
                    title="📋 Monitored Domains",
                    description="No domains are currently being monitored.\nUse `!ssl add <domain>` to add a domain.",
                    color=0x3498db
                )
                await ctx.send(embed=embed)
                return
            
            embed = discord.Embed(
                title="📋 Monitored Domains",
                description=f"Currently monitoring **{len(domains)}** domain(s)",
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            # Add domains to embed (max 25 fields)
            for i, domain in enumerate(domains[:25]):
                ssl_status = json.loads(domain.ssl_status) if domain.ssl_status else None
                
                if ssl_status:
                    expires_in = ssl_status.get('expires_in', 0)
                    status_emoji = self.get_status_emoji(expires_in)
                    status_text = f"{expires_in} days"
                else:
                    status_emoji = "❓"
                    status_text = "Not checked"
                
                embed.add_field(
                    name=f"{status_emoji} {domain.name}",
                    value=f"Expires in: {status_text}",
                    inline=True
                )
            
            if len(domains) > 25:
                embed.add_field(
                    name="...",
                    value=f"and {len(domains) - 25} more domains",
                    inline=False
                )
            
            embed.set_footer(text="Use !ssl status <domain> for detailed information")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error listing domains: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to list domains. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='status')
    async def domain_status(self, ctx, *, domain: str):
        """Get detailed SSL status for a domain"""
        try:
            db: Session = next(get_db())
            
            domain_obj = db.query(Domain).filter(Domain.name == domain).first()
            if not domain_obj:
                embed = discord.Embed(
                    title="❌ Domain Not Found",
                    description=f"**{domain}** is not being monitored",
                    color=0xff0000
                )
                await ctx.send(embed=embed)
                return
            
            ssl_status = json.loads(domain_obj.ssl_status) if domain_obj.ssl_status else None
            
            if not ssl_status:
                embed = discord.Embed(
                    title="❓ SSL Status Unknown",
                    description=f"No SSL information available for **{domain}**",
                    color=0xffa500
                )
                embed.add_field(
                    name="ℹ️ Information",
                    value="SSL status will be checked automatically every 5 minutes",
                    inline=False
                )
                await ctx.send(embed=embed)
                return
            
            expires_in = ssl_status.get('expires_in', 0)
            status_emoji = self.get_status_emoji(expires_in)
            status_color = self.get_status_color(expires_in)
            
            embed = discord.Embed(
                title=f"{status_emoji} SSL Certificate Status",
                description=f"**{domain}**",
                color=status_color,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📅 Expiry Date",
                value=datetime.fromisoformat(ssl_status.get('not_valid_after', '')).strftime('%Y-%m-%d %H:%M:%S UTC'),
                inline=True
            )
            
            embed.add_field(
                name="⏰ Days Until Expiry",
                value=f"{expires_in} days",
                inline=True
            )
            
            embed.add_field(
                name="🏢 Issuer",
                value=ssl_status.get('issuer', 'Unknown'),
                inline=False
            )
            
            embed.add_field(
                name="🔗 Subject",
                value=ssl_status.get('subject', 'Unknown'),
                inline=False
            )
            
            embed.add_field(
                name="🔄 Last Checked",
                value=datetime.fromisoformat(ssl_status.get('checked_at', '')).strftime('%Y-%m-%d %H:%M:%S UTC'),
                inline=True
            )
            
            embed.add_field(
                name="⚙️ Alert Threshold",
                value=f"{domain_obj.alert_threshold_days} days",
                inline=True
            )
            
            embed.set_footer(text="SSL Monitor Pro")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error getting status for domain {domain}: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to get domain status. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='check')
    async def check_ssl(self, ctx, *, domain: str):
        """Manually check SSL status for a domain"""
        try:
            # Show checking message
            checking_embed = discord.Embed(
                title="🔍 Checking SSL Certificate",
                description=f"Checking SSL status for **{domain}**...",
                color=0x3498db
            )
            message = await ctx.send(embed=checking_embed)
            
            # Perform SSL check
            ssl_info = await self.bot.get_ssl_info(domain)
            
            if not ssl_info:
                embed = discord.Embed(
                    title="❌ SSL Check Failed",
                    description=f"Could not retrieve SSL information for **{domain}**",
                    color=0xff0000
                )
                embed.add_field(
                    name="Possible Reasons",
                    value=(
                        "• Domain does not exist\n"
                        "• SSL certificate is invalid\n"
                        "• Domain is not accessible\n"
                        "• Network connectivity issues"
                    ),
                    inline=False
                )
                await message.edit(embed=embed)
                return
            
            expires_in = ssl_info.get('expires_in', 0)
            status_emoji = self.get_status_emoji(expires_in)
            status_color = self.get_status_color(expires_in)
            
            embed = discord.Embed(
                title=f"{status_emoji} SSL Certificate Check",
                description=f"**{domain}**",
                color=status_color,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📅 Expiry Date",
                value=datetime.fromisoformat(ssl_info.get('not_valid_after', '')).strftime('%Y-%m-%d %H:%M:%S UTC'),
                inline=True
            )
            
            embed.add_field(
                name="⏰ Days Until Expiry",
                value=f"{expires_in} days",
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
            
            embed.add_field(
                name="✅ Certificate Valid",
                value="Yes" if ssl_info.get('is_valid', False) else "No",
                inline=True
            )
            
            embed.add_field(
                name="🔒 Encryption",
                value="Strong" if expires_in > 30 else "Check Required",
                inline=True
            )
            
            embed.set_footer(text="SSL Monitor Pro • Manual Check")
            
            await message.edit(embed=embed)
            
        except Exception as e:
            logger.error(f"Error checking SSL for domain {domain}: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to check SSL status. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
    
    @commands.command(name='help')
    async def help_command(self, ctx):
        """Show help information"""
        embed = discord.Embed(
            title="🔐 SSL Monitor Pro - Help",
            description="Professional SSL certificate monitoring bot",
            color=0x3498db,
            timestamp=datetime.utcnow()
        )
        
        embed.add_field(
            name="📋 Domain Management",
            value=(
                "`!ssl add <domain>` - Add domain to monitoring\n"
                "`!ssl remove <domain>` - Remove domain from monitoring\n"
                "`!ssl list` - List all monitored domains\n"
                "`!ssl status <domain>` - Get detailed SSL status\n"
                "`!ssl check <domain>` - Manually check SSL status"
            ),
            inline=False
        )
        
        embed.add_field(
            name="⚙️ Configuration",
            value=(
                "`!ssl setup` - Configure notification settings\n"
                "`!ssl channel` - Set notification channel\n"
                "`!ssl role` - Set notification role\n"
                "`!ssl settings` - View current settings"
            ),
            inline=False
        )
        
        embed.add_field(
            name="📊 Analytics",
            value=(
                "`!ssl stats` - View server statistics\n"
                "`!ssl alerts` - View recent alerts\n"
                "`!ssl health` - Overall SSL health summary"
            ),
            inline=False
        )
        
        embed.add_field(
            name="ℹ️ Information",
            value=(
                "• SSL certificates are checked every 5 minutes\n"
                "• Alerts are sent based on your configured thresholds\n"
                "• Use `!ssl setup` to configure notification preferences"
            ),
            inline=False
        )
        
        embed.set_footer(text="SSL Monitor Pro • Professional SSL Certificate Monitoring")
        
        await ctx.send(embed=embed)
    
    def is_valid_domain(self, domain: str) -> bool:
        """Validate domain format"""
        import re
        domain_regex = re.compile(
            r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
        )
        return bool(domain_regex.match(domain))
    
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
    
    def get_status_color(self, expires_in: int) -> int:
        """Get status color based on expiry days"""
        if expires_in <= 0:
            return 0xff0000  # Red
        elif expires_in <= 7:
            return 0xff8c00  # Orange
        elif expires_in <= 30:
            return 0xffa500  # Yellow
        else:
            return 0x00ff00  # Green

async def setup(bot):
    """Setup the cog"""
    await bot.add_cog(SSLMonitorCog(bot))
