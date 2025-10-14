"""
SSL certificate checking tasks
"""
import ssl
import socket
from datetime import datetime, timezone
from typing import Dict, Any, Optional
from celery import current_task
from app.tasks.celery_app import celery_app
from app.core.database import async_session_maker
from app.models.monitor import Monitor, SSLCertStatus
from app.models.check_result import MonitorCheckResult
from app.tasks.notification_tasks import trigger_notifications
import logging

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3)
def check_ssl_certificate(self, monitor_id: int) -> Dict[str, Any]:
    """
    Check SSL certificate for a specific monitor
    
    Args:
        monitor_id: ID of the monitor to check
        
    Returns:
        Dict with check results
    """
    try:
        logger.info(f"Starting SSL check for monitor {monitor_id}")
        
        # Get monitor from database
        from sqlalchemy import select
        async with async_session_maker() as session:
            result = await session.execute(
                select(Monitor).where(Monitor.id == monitor_id)
            )
            monitor = result.scalar_one_or_none()
            
            if not monitor:
                logger.error(f"Monitor {monitor_id} not found")
                return {"error": "Monitor not found"}
            
            # Check SSL certificate
            check_result = await _check_ssl_certificate(monitor)
            
            # Save check result to database
            check_result_db = MonitorCheckResult(
                monitor_id=monitor_id,
                check_type="ssl_cert",
                success=check_result["success"],
                issuer=check_result.get("issuer"),
                subject=check_result.get("subject"),
                serial_number=check_result.get("serial_number"),
                fingerprint=check_result.get("fingerprint"),
                valid_from=check_result.get("valid_from"),
                valid_until=check_result.get("valid_until"),
                response_time_ms=check_result.get("response_time_ms"),
                connection_time_ms=check_result.get("connection_time_ms"),
                handshake_time_ms=check_result.get("handshake_time_ms"),
                error_code=check_result.get("error_code"),
                error_message=check_result.get("error_message"),
                certificate_chain_length=check_result.get("certificate_chain_length"),
                cipher_suite=check_result.get("cipher_suite"),
                protocol_version=check_result.get("protocol_version"),
            )
            
            session.add(check_result_db)
            
            # Update monitor with latest check info
            monitor.last_checked_at = datetime.now(timezone.utc)
            
            if check_result["success"]:
                monitor.last_successful_check = datetime.now(timezone.utc)
                monitor.consecutive_errors = 0
                monitor.last_error = None
                
                # Update SSL status
                days_until_expiry = check_result.get("days_until_expiry", 0)
                if days_until_expiry < 0:
                    monitor.ssl_status = SSLCertStatus.EXPIRED
                elif days_until_expiry <= monitor.alert_before_days:
                    monitor.ssl_status = SSLCertStatus.EXPIRING_SOON
                else:
                    monitor.ssl_status = SSLCertStatus.VALID
                    
                # Update certificate info
                monitor.issuer = check_result.get("issuer")
                monitor.subject = check_result.get("subject")
                monitor.serial_number = check_result.get("serial_number")
                monitor.fingerprint = check_result.get("fingerprint")
                monitor.valid_from = check_result.get("valid_from")
                monitor.valid_until = check_result.get("valid_until")
                monitor.response_time_ms = check_result.get("response_time_ms")
                
            else:
                monitor.consecutive_errors += 1
                monitor.last_error = check_result.get("error_message")
                
                if monitor.consecutive_errors >= monitor.max_consecutive_errors:
                    monitor.status = "error"
                    monitor.ssl_status = SSLCertStatus.INVALID
            
            await session.commit()
            
            # Trigger notifications if needed
            if check_result["success"]:
                trigger_notifications.delay(monitor_id, "ssl_check_success", check_result)
            else:
                trigger_notifications.delay(monitor_id, "ssl_check_error", check_result)
            
            logger.info(f"SSL check completed for monitor {monitor_id}")
            return check_result
            
    except Exception as exc:
        logger.error(f"SSL check failed for monitor {monitor_id}: {exc}")
        
        # Retry the task
        if self.request.retries < self.max_retries:
            logger.info(f"Retrying SSL check for monitor {monitor_id} (attempt {self.request.retries + 1})")
            raise self.retry(countdown=60 * (2 ** self.request.retries))
        
        return {"error": str(exc)}


async def _check_ssl_certificate(monitor: Monitor) -> Dict[str, Any]:
    """
    Perform SSL certificate check
    
    Args:
        monitor: Monitor instance
        
    Returns:
        Dict with check results
    """
    import time
    start_time = time.time()
    
    try:
        # Create SSL context
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        
        # Connect to server
        connection_start = time.time()
        with socket.create_connection((monitor.domain, monitor.port), timeout=10) as sock:
            connection_time = (time.time() - connection_start) * 1000
            
            # Perform SSL handshake
            handshake_start = time.time()
            with context.wrap_socket(sock, server_hostname=monitor.domain) as ssock:
                handshake_time = (time.time() - handshake_start) * 1000
                
                # Get certificate
                cert = ssock.getpeercert()
                
                # Get cipher info
                cipher = ssock.cipher()
                
                # Parse certificate dates
                from datetime import datetime
                valid_from = datetime.strptime(cert["notBefore"], "%b %d %H:%M:%S %Y %Z")
                valid_until = datetime.strptime(cert["notAfter"], "%b %d %H:%M:%S %Y %Z")
                
                # Calculate days until expiry
                now = datetime.now(timezone.utc)
                days_until_expiry = (valid_until - now).days
                
                response_time = (time.time() - start_time) * 1000
                
                return {
                    "success": True,
                    "issuer": cert.get("issuer", {}).get("organizationName", "Unknown"),
                    "subject": cert.get("subject", {}).get("commonName", monitor.domain),
                    "serial_number": cert.get("serialNumber"),
                    "fingerprint": cert.get("fingerprint", "").replace(":", "").upper(),
                    "valid_from": valid_from,
                    "valid_until": valid_until,
                    "days_until_expiry": days_until_expiry,
                    "response_time_ms": response_time,
                    "connection_time_ms": connection_time,
                    "handshake_time_ms": handshake_time,
                    "certificate_chain_length": len(cert.get("issuer", {})),
                    "cipher_suite": cipher[0] if cipher else None,
                    "protocol_version": cipher[2] if cipher else None,
                }
                
    except socket.timeout:
        return {
            "success": False,
            "error_code": "TIMEOUT",
            "error_message": f"Connection timeout to {monitor.domain}:{monitor.port}",
            "response_time_ms": (time.time() - start_time) * 1000,
        }
    except ssl.SSLError as e:
        return {
            "success": False,
            "error_code": "SSL_ERROR",
            "error_message": f"SSL error: {str(e)}",
            "response_time_ms": (time.time() - start_time) * 1000,
        }
    except socket.error as e:
        return {
            "success": False,
            "error_code": "CONNECTION_ERROR",
            "error_message": f"Connection error: {str(e)}",
            "response_time_ms": (time.time() - start_time) * 1000,
        }
    except Exception as e:
        return {
            "success": False,
            "error_code": "UNKNOWN_ERROR",
            "error_message": f"Unknown error: {str(e)}",
            "response_time_ms": (time.time() - start_time) * 1000,
        }


@celery_app.task
def check_multiple_ssl_certificates(monitor_ids: list[int]) -> Dict[str, Any]:
    """
    Check SSL certificates for multiple monitors
    
    Args:
        monitor_ids: List of monitor IDs to check
        
    Returns:
        Dict with results summary
    """
    results = []
    
    for monitor_id in monitor_ids:
        try:
            result = check_ssl_certificate.delay(monitor_id)
            results.append({
                "monitor_id": monitor_id,
                "task_id": result.id,
                "status": "queued"
            })
        except Exception as e:
            results.append({
                "monitor_id": monitor_id,
                "error": str(e),
                "status": "failed"
            })
    
    return {
        "total_monitors": len(monitor_ids),
        "queued": len([r for r in results if r.get("status") == "queued"]),
        "failed": len([r for r in results if r.get("status") == "failed"]),
        "results": results
    }
