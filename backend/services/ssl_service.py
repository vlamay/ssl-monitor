import ssl
import socket
from datetime import datetime
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from typing import Dict, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_ssl_certificate(domain: str, port: int = 443, timeout: int = 10) -> Dict:
    """
    Check SSL certificate for a domain
    
    Args:
        domain: Domain name to check (e.g., 'example.com')
        port: Port to connect to (default: 443)
        timeout: Connection timeout in seconds (default: 10)
    
    Returns:
        Dictionary with SSL certificate information
    """
    logger.info(f"Checking SSL certificate for {domain}")
    
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to the domain
        with socket.create_connection((domain, port), timeout=timeout) as sock:
            with context.wrap_socket(sock, server_hostname=domain) as ssock:
                # Get certificate in binary form
                cert_bin = ssock.getpeercert(binary_form=True)
                
                # Parse certificate
                cert = x509.load_der_x509_certificate(cert_bin, default_backend())
                
                # Extract certificate information
                issuer = cert.issuer.rfc4514_string()
                subject = cert.subject.rfc4514_string()
                not_valid_before = cert.not_valid_before_utc if hasattr(cert, 'not_valid_before_utc') else cert.not_valid_before
                not_valid_after = cert.not_valid_after_utc if hasattr(cert, 'not_valid_after_utc') else cert.not_valid_after
                
                # Calculate days until expiration
                now = datetime.now(not_valid_after.tzinfo) if not_valid_after.tzinfo else datetime.utcnow()
                expires_in = (not_valid_after - now).days
                
                # Check if certificate is currently valid
                is_valid = now < not_valid_after and now > not_valid_before
                
                result = {
                    "domain": domain,
                    "is_valid": is_valid,
                    "expires_in": expires_in,
                    "issuer": issuer,
                    "subject": subject,
                    "not_valid_before": not_valid_before,
                    "not_valid_after": not_valid_after,
                    "error": None
                }
                
                logger.info(f"SSL check for {domain}: valid={is_valid}, expires_in={expires_in} days")
                return result
                
    except ssl.SSLError as e:
        logger.error(f"SSL error for {domain}: {str(e)}")
        return {
            "domain": domain,
            "is_valid": False,
            "expires_in": 0,
            "issuer": None,
            "subject": None,
            "not_valid_before": None,
            "not_valid_after": None,
            "error": f"SSL Error: {str(e)}"
        }
    except socket.gaierror as e:
        logger.error(f"DNS resolution failed for {domain}: {str(e)}")
        return {
            "domain": domain,
            "is_valid": False,
            "expires_in": 0,
            "issuer": None,
            "subject": None,
            "not_valid_before": None,
            "not_valid_after": None,
            "error": f"DNS Error: {str(e)}"
        }
    except socket.timeout:
        logger.error(f"Connection timeout for {domain}")
        return {
            "domain": domain,
            "is_valid": False,
            "expires_in": 0,
            "issuer": None,
            "subject": None,
            "not_valid_before": None,
            "not_valid_after": None,
            "error": "Connection timeout"
        }
    except Exception as e:
        logger.error(f"Unexpected error for {domain}: {str(e)}")
        return {
            "domain": domain,
            "is_valid": False,
            "expires_in": 0,
            "issuer": None,
            "subject": None,
            "not_valid_before": None,
            "not_valid_after": None,
            "error": f"Error: {str(e)}"
        }

def check_multiple_domains(domains: list) -> Dict[str, Dict]:
    """
    Check SSL certificates for multiple domains
    
    Args:
        domains: List of domain names
    
    Returns:
        Dictionary mapping domain names to their SSL check results
    """
    results = {}
    for domain in domains:
        results[domain] = check_ssl_certificate(domain)
    return results

