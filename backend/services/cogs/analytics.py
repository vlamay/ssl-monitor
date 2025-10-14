"""
Analytics Cog - Analytics and statistics commands
"""

import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict

import discord
from discord.ext import commands
from sqlalchemy.orm import Session

from ...database import get_db
from ...models import Domain, NotificationSettings

logger = logging.getLogger(__name__)

class AnalyticsCog(commands.Cog):
    """Analytics and statistics commands"""
    
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name='stats')
    async def server_stats(self, ctx):
        """Show server statistics"""
        try:
            db: Session = next(get_db())
            
            # Get all domains
            domains = db.query(Domain).filter(Domain.is_active == True).all()
            
            if not domains:
                embed = discord.Embed(
                    title="📊 Server Statistics",
                    description="No domains are currently being monitored.",
                    color=0x3498db
                )
                await ctx.send(embed=embed)
                return
            
            # Calculate statistics
            total_domains = len(domains)
            healthy_count = 0
            warning_count = 0
            critical_count = 0
            expired_count = 0
            
            for domain in domains:
                if domain.ssl_status:
                    ssl_info = json.loads(domain.ssl_status)
                    expires_in = ssl_info.get('expires_in', 0)
                    
                    if expires_in <= 0:
                        expired_count += 1
                    elif expires_in <= 7:
                        critical_count += 1
                    elif expires_in <= 30:
                        warning_count += 1
                    else:
                        healthy_count += 1
            
            embed = discord.Embed(
                title="📊 SSL Monitoring Statistics",
                description=f"Statistics for **{ctx.guild.name}**",
                color=0x3498db,
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📋 Overview",
                value=(
                    f"**Total Domains:** {total_domains}\n"
                    f"**Active Monitoring:** {total_domains}\n"
                    f"**Last Updated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}"
                ),
                inline=True
            )
            
            embed.add_field(
                name="🔒 SSL Status",
                value=(
                    f"**✅ Healthy:** {healthy_count}\n"
                    f"**🟡 Warning:** {warning_count}\n"
                    f"**⚠️ Critical:** {critical_count}\n"
                    f"**🚨 Expired:** {expired_count}"
                ),
                inline=True
            )
            
            # Calculate health percentage
            if total_domains > 0:
                health_percentage = ((healthy_count + warning_count) / total_domains) * 100
                embed.add_field(
                    name="📈 Health Score",
                    value=f"**{health_percentage:.1f}%**\n{'🟢 Excellent' if health_percentage >= 90 else '🟡 Good' if health_percentage >= 70 else '🔴 Needs Attention'}",
                    inline=True
                )
            
            # Add recent activity
            recent_domains = sorted(domains, key=lambda d: d.updated_at, reverse=True)[:5]
            if recent_domains:
                recent_list = []
                for domain in recent_domains:
                    if domain.ssl_status:
                        ssl_info = json.loads(domain.ssl_status)
                        expires_in = ssl_info.get('expires_in', 0)
                        status_emoji = self.get_status_emoji(expires_in)
                        recent_list.append(f"{status_emoji} {domain.name}")
                    else:
                        recent_list.append(f"❓ {domain.name}")
                
                embed.add_field(
                    name="🕒 Recent Activity",
                    value="\n".join(recent_list),
                    inline=False
                )
            
            embed.set_footer(text="Use !ssl list for detailed domain information")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing server stats: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve statistics. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='health')
    async def health_summary(self, ctx):
        """Show overall SSL health summary"""
        try:
            db: Session = next(get_db())
            
            domains = db.query(Domain).filter(Domain.is_active == True).all()
            
            if not domains:
                embed = discord.Embed(
                    title="🏥 SSL Health Summary",
                    description="No domains are currently being monitored.",
                    color=0x3498db
                )
                await ctx.send(embed=embed)
                return
            
            # Analyze SSL health
            health_data = self.analyze_ssl_health(domains)
            
            embed = discord.Embed(
                title="🏥 SSL Health Summary",
                description=f"Overall SSL health for **{ctx.guild.name}**",
                color=self.get_health_color(health_data['overall_score']),
                timestamp=datetime.utcnow()
            )
            
            embed.add_field(
                name="📊 Health Score",
                value=f"**{health_data['overall_score']:.1f}%**\n{health_data['health_status']}",
                inline=True
            )
            
            embed.add_field(
                name="🔍 Analysis",
                value=(
                    f"**Domains Analyzed:** {health_data['total_domains']}\n"
                    f"**Healthy:** {health_data['healthy_count']}\n"
                    f"**At Risk:** {health_data['at_risk_count']}\n"
                    f"**Critical:** {health_data['critical_count']}"
                ),
                inline=True
            )
            
            # Add recommendations
            if health_data['recommendations']:
                embed.add_field(
                    name="💡 Recommendations",
                    value="\n".join([f"• {rec}" for rec in health_data['recommendations'][:3]]),
                    inline=False
                )
            
            # Add trend information
            if health_data['trend']:
                embed.add_field(
                    name="📈 Trend",
                    value=health_data['trend'],
                    inline=False
                )
            
            embed.set_footer(text="SSL Monitor Pro • Health Analysis")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing health summary: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve health summary. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='alerts')
    async def recent_alerts(self, ctx, limit: int = 10):
        """Show recent SSL alerts"""
        try:
            if limit < 1 or limit > 25:
                limit = 10
            
            db: Session = next(get_db())
            
            # Get domains that need attention
            domains = db.query(Domain).filter(Domain.is_active == True).all()
            
            alerts = []
            for domain in domains:
                if domain.ssl_status:
                    ssl_info = json.loads(domain.ssl_status)
                    expires_in = ssl_info.get('expires_in', 0)
                    
                    if expires_in <= 30:  # Show domains expiring within 30 days
                        alert_type = self.get_alert_type(expires_in)
                        alerts.append({
                            'domain': domain.name,
                            'expires_in': expires_in,
                            'type': alert_type,
                            'last_checked': ssl_info.get('checked_at', domain.updated_at.isoformat())
                        })
            
            # Sort by urgency (expired first, then by days)
            alerts.sort(key=lambda x: (x['expires_in'], x['domain']))
            alerts = alerts[:limit]
            
            if not alerts:
                embed = discord.Embed(
                    title="🔔 Recent Alerts",
                    description="No SSL alerts at this time. All certificates are healthy! 🎉",
                    color=0x00ff00,
                    timestamp=datetime.utcnow()
                )
            else:
                embed = discord.Embed(
                    title="🔔 Recent SSL Alerts",
                    description=f"Showing {len(alerts)} recent SSL alerts",
                    color=0xffa500,
                    timestamp=datetime.utcnow()
                )
                
                for alert in alerts:
                    status_emoji = self.get_status_emoji(alert['expires_in'])
                    embed.add_field(
                        name=f"{status_emoji} {alert['domain']}",
                        value=f"**Status:** {alert['type']}\n**Expires in:** {alert['expires_in']} days",
                        inline=True
                    )
            
            embed.set_footer(text="Use !ssl status <domain> for detailed information")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing recent alerts: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve alerts. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    @commands.command(name='expiring')
    async def expiring_certificates(self, ctx, days: int = 30):
        """Show certificates expiring within specified days"""
        try:
            if days < 1 or days > 365:
                days = 30
            
            db: Session = next(get_db())
            
            domains = db.query(Domain).filter(Domain.is_active == True).all()
            
            expiring_domains = []
            for domain in domains:
                if domain.ssl_status:
                    ssl_info = json.loads(domain.ssl_status)
                    expires_in = ssl_info.get('expires_in', 0)
                    
                    if 0 <= expires_in <= days:
                        expiring_domains.append({
                            'domain': domain.name,
                            'expires_in': expires_in,
                            'expiry_date': ssl_info.get('not_valid_after', 'Unknown'),
                            'issuer': ssl_info.get('issuer', 'Unknown')
                        })
            
            # Sort by days until expiry
            expiring_domains.sort(key=lambda x: x['expires_in'])
            
            if not expiring_domains:
                embed = discord.Embed(
                    title=f"📅 Certificates Expiring (Next {days} Days)",
                    description=f"No certificates are expiring within the next {days} days. 🎉",
                    color=0x00ff00,
                    timestamp=datetime.utcnow()
                )
            else:
                embed = discord.Embed(
                    title=f"📅 Certificates Expiring (Next {days} Days)",
                    description=f"Found {len(expiring_domains)} certificate(s) expiring soon",
                    color=0xffa500,
                    timestamp=datetime.utcnow()
                )
                
                for cert in expiring_domains[:10]:  # Show max 10
                    status_emoji = self.get_status_emoji(cert['expires_in'])
                    embed.add_field(
                        name=f"{status_emoji} {cert['domain']}",
                        value=(
                            f"**Expires in:** {cert['expires_in']} days\n"
                            f"**Issuer:** {cert['issuer'][:50]}..."
                        ),
                        inline=True
                    )
                
                if len(expiring_domains) > 10:
                    embed.add_field(
                        name="...",
                        value=f"and {len(expiring_domains) - 10} more certificates",
                        inline=False
                    )
            
            embed.set_footer(text="Use !ssl status <domain> for detailed information")
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            logger.error(f"Error showing expiring certificates: {e}")
            embed = discord.Embed(
                title="❌ Error",
                description="Failed to retrieve expiring certificates. Please try again later.",
                color=0xff0000
            )
            await ctx.send(embed=embed)
        finally:
            db.close()
    
    def analyze_ssl_health(self, domains: List[Domain]) -> Dict:
        """Analyze SSL health across all domains"""
        total_domains = len(domains)
        healthy_count = 0
        warning_count = 0
        critical_count = 0
        expired_count = 0
        
        recommendations = []
        
        for domain in domains:
            if domain.ssl_status:
                ssl_info = json.loads(domain.ssl_status)
                expires_in = ssl_info.get('expires_in', 0)
                
                if expires_in <= 0:
                    expired_count += 1
                    recommendations.append(f"Renew certificate for {domain.name}")
                elif expires_in <= 7:
                    critical_count += 1
                    recommendations.append(f"Urgent: Renew certificate for {domain.name}")
                elif expires_in <= 30:
                    warning_count += 1
                    recommendations.append(f"Plan renewal for {domain.name}")
                else:
                    healthy_count += 1
        
        # Calculate overall health score
        if total_domains > 0:
            overall_score = ((healthy_count + warning_count) / total_domains) * 100
        else:
            overall_score = 0
        
        # Determine health status
        if overall_score >= 90:
            health_status = "🟢 Excellent"
        elif overall_score >= 70:
            health_status = "🟡 Good"
        elif overall_score >= 50:
            health_status = "🟠 Fair"
        else:
            health_status = "🔴 Poor"
        
        # Determine trend (simplified)
        trend = "📈 Improving" if healthy_count > (total_domains / 2) else "📉 Needs Attention"
        
        return {
            'total_domains': total_domains,
            'healthy_count': healthy_count,
            'warning_count': warning_count,
            'critical_count': critical_count,
            'expired_count': expired_count,
            'at_risk_count': warning_count + critical_count,
            'overall_score': overall_score,
            'health_status': health_status,
            'recommendations': recommendations,
            'trend': trend
        }
    
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
    
    def get_alert_type(self, expires_in: int) -> str:
        """Get alert type based on expiry days"""
        if expires_in <= 0:
            return "Expired"
        elif expires_in <= 7:
            return "Critical"
        elif expires_in <= 30:
            return "Warning"
        else:
            return "Healthy"
    
    def get_health_color(self, score: float) -> int:
        """Get embed color based on health score"""
        if score >= 90:
            return 0x00ff00  # Green
        elif score >= 70:
            return 0xffa500  # Orange
        elif score >= 50:
            return 0xff8c00  # Dark Orange
        else:
            return 0xff0000  # Red

async def setup(bot):
    """Setup the cog"""
    await bot.add_cog(AnalyticsCog(bot))
