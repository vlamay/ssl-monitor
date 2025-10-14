"""
Security Configuration for SSL Monitor Pro
Implements comprehensive security measures
"""

from flask import Flask, request, jsonify
from flask_talisman import Talisman
from flask_cors import CORS
import os
import logging
from functools import wraps
import re
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

def init_security(app: Flask):
    """Initialize security middleware and configurations"""
    
    # Content Security Policy
    csp = {
        'default-src': "'self'",
        'style-src': [
            "'self'", 
            "'unsafe-inline'",  # Required for some UI frameworks
            "https://cdnjs.cloudflare.com",
            "https://fonts.googleapis.com"
        ],
        'script-src': [
            "'self'",
            "'unsafe-inline'",  # Required for inline scripts
            "https://cdnjs.cloudflare.com",
            "https://js.stripe.com",  # For Stripe payments
            "https://checkout.stripe.com"
        ],
        'img-src': [
            "'self'",
            "data:",
            "https:",
            "blob:"
        ],
        'connect-src': [
            "'self'",
            "https://api.telegram.org",
            "https://api.stripe.com",
            "https://js.stripe.com",
            "https://checkout.stripe.com",
            "https://api.uptimerobot.com"
        ],
        'font-src': [
            "'self'",
            "https://fonts.gstatic.com",
            "https://cdnjs.cloudflare.com"
        ],
        'object-src': "'none'",
        'base-uri': "'self'",
        'form-action': "'self'",
        'frame-ancestors': "'none'"
    }
    
    # Initialize Talisman for security headers
    Talisman(app, 
        force_https=True,
        strict_transport_security=True,
        strict_transport_security_max_age=31536000,  # 1 year
        content_security_policy=csp,
        referrer_policy='strict-origin-when-cross-origin',
        permissions_policy={
            'geolocation': 'none',
            'camera': 'none',
            'microphone': 'none',
            'payment': 'none'
        }
    )
    
    # CORS configuration
    allowed_origins = os.getenv('ALLOWED_ORIGINS', 'https://sslmonitor.pro').split(',')
    
    CORS(app, 
        origins=allowed_origins,
        methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
        allow_headers=['Content-Type', 'Authorization', 'X-API-Key'],
        supports_credentials=True,
        max_age=3600
    )
    
    # Additional security middleware
    @app.before_request
    def security_headers():
        """Add additional security headers"""
        # Prevent clickjacking
        response = request.environ.get('werkzeug.response')
        if response:
            response.headers['X-Frame-Options'] = 'DENY'
            response.headers['X-Content-Type-Options'] = 'nosniff'
            response.headers['X-XSS-Protection'] = '1; mode=block'
            response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
            
            # Remove server information
            if 'Server' in response.headers:
                del response.headers['Server']
    
    logger.info("Security middleware initialized")

def validate_domain(domain: str) -> bool:
    """Validate domain name format"""
    if not domain:
        return False
    
    # Remove protocol if present
    domain = domain.replace('https://', '').replace('http://', '').replace('www.', '')
    
    # Basic domain validation regex
    domain_regex = re.compile(
        r'^(?:[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?\.)*[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?$'
    )
    
    return bool(domain_regex.match(domain)) and len(domain) <= 253

def validate_email(email: str) -> bool:
    """Validate email format"""
    if not email:
        return False
    
    email_regex = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )
    
    return bool(email_regex.match(email)) and len(email) <= 254

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength"""
    if not password:
        return False, "Password is required"
    
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    
    # Check for required character types
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
    
    if not (has_lower and has_upper and has_digit):
        return False, "Password must contain uppercase, lowercase, and numbers"
    
    # Check for common weak patterns
    weak_patterns = [
        r'password',
        r'123456',
        r'qwerty',
        r'admin',
        r'user'
    ]
    
    for pattern in weak_patterns:
        if re.search(pattern, password, re.IGNORECASE):
            return False, "Password contains common weak patterns"
    
    return True, "Password is valid"

def sanitize_input(text: str, max_length: int = 1000) -> str:
    """Sanitize user input"""
    if not text:
        return ""
    
    # Truncate to max length
    text = text[:max_length]
    
    # Remove potentially dangerous characters
    dangerous_chars = ['<', '>', '"', "'", '&', '\x00']
    for char in dangerous_chars:
        text = text.replace(char, '')
    
    # Remove control characters
    text = ''.join(char for char in text if ord(char) >= 32)
    
    return text.strip()

def validate_url(url: str) -> bool:
    """Validate URL format"""
    if not url:
        return False
    
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False

def require_api_key(f):
    """Decorator to require API key for endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        
        if not api_key:
            return jsonify({
                "error": "API key required",
                "message": "Include X-API-Key header"
            }), 401
        
        # Validate API key (implement your validation logic)
        if not validate_api_key(api_key):
            return jsonify({
                "error": "Invalid API key",
                "message": "The provided API key is invalid"
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def validate_api_key(api_key: str) -> bool:
    """Validate API key format and authenticity"""
    if not api_key:
        return False
    
    # Basic format validation (implement your logic)
    if len(api_key) < 32:
        return False
    
    # Check against stored API keys (implement database lookup)
    # For now, return True for demonstration
    return True

def require_https(f):
    """Decorator to require HTTPS"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not request.is_secure and os.getenv('FLASK_ENV') == 'production':
            return jsonify({
                "error": "HTTPS required",
                "message": "This endpoint requires HTTPS"
            }), 400
        
        return f(*args, **kwargs)
    
    return decorated_function

def log_security_event(event_type: str, details: dict, severity: str = "INFO"):
    """Log security-related events"""
    log_data = {
        "timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "severity": severity,
        "ip_address": request.remote_addr,
        "user_agent": request.headers.get('User-Agent', ''),
        "details": details
    }
    
    if severity == "CRITICAL":
        logger.critical(f"Security event: {json.dumps(log_data)}")
    elif severity == "WARNING":
        logger.warning(f"Security event: {json.dumps(log_data)}")
    else:
        logger.info(f"Security event: {json.dumps(log_data)}")

def detect_suspicious_activity(request) -> bool:
    """Detect potentially suspicious activity"""
    suspicious_indicators = []
    
    # Check for suspicious User-Agent
    user_agent = request.headers.get('User-Agent', '').lower()
    suspicious_ua_patterns = [
        'sqlmap', 'nmap', 'nikto', 'masscan', 'zap',
        'burp', 'wget', 'curl', 'python-requests'
    ]
    
    for pattern in suspicious_ua_patterns:
        if pattern in user_agent:
            suspicious_indicators.append(f"Suspicious User-Agent: {pattern}")
    
    # Check for suspicious headers
    suspicious_headers = [
        'X-Forwarded-For', 'X-Real-IP', 'X-Originating-IP',
        'X-Remote-IP', 'X-Remote-Addr'
    ]
    
    for header in suspicious_headers:
        if header in request.headers:
            suspicious_indicators.append(f"Suspicious header: {header}")
    
    # Check for SQL injection patterns in query parameters
    sql_patterns = [
        r'union\s+select',
        r'drop\s+table',
        r'delete\s+from',
        r'insert\s+into',
        r'update\s+set',
        r'exec\s*\(',
        r'script\s*>'
    ]
    
    for key, value in request.args.items():
        for pattern in sql_patterns:
            if re.search(pattern, str(value), re.IGNORECASE):
                suspicious_indicators.append(f"SQL injection attempt in {key}")
    
    # Log suspicious activity
    if suspicious_indicators:
        log_security_event(
            "suspicious_activity",
            {
                "indicators": suspicious_indicators,
                "url": request.url,
                "method": request.method
            },
            "WARNING"
        )
        return True
    
    return False

def security_middleware(f):
    """Security middleware decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Detect suspicious activity
        if detect_suspicious_activity(request):
            return jsonify({
                "error": "Access denied",
                "message": "Request blocked due to security policy"
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

# Input validation schemas using decorators
def validate_input(schema_class):
    """Generic input validation decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            try:
                # Validate JSON input
                if request.is_json:
                    validated_data = schema_class().load(request.json)
                    request.validated_data = validated_data
                
                # Validate form data
                elif request.form:
                    validated_data = schema_class().load(request.form.to_dict())
                    request.validated_data = validated_data
                
                return f(*args, **kwargs)
                
            except ValidationError as e:
                log_security_event(
                    "validation_error",
                    {"errors": e.messages, "endpoint": request.endpoint},
                    "WARNING"
                )
                
                return jsonify({
                    "error": "Validation failed",
                    "details": e.messages
                }), 400
        
        return decorated_function
    return decorator

# Security configuration for different environments
SECURITY_CONFIG = {
    'development': {
        'force_https': False,
        'csp_strict': False,
        'rate_limiting': False
    },
    'staging': {
        'force_https': True,
        'csp_strict': True,
        'rate_limiting': True
    },
    'production': {
        'force_https': True,
        'csp_strict': True,
        'rate_limiting': True,
        'logging': True
    }
}

def get_security_config():
    """Get security configuration for current environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return SECURITY_CONFIG.get(env, SECURITY_CONFIG['development'])

# Initialize security logging
def init_security_logging():
    """Initialize security-specific logging"""
    security_logger = logging.getLogger('security')
    security_logger.setLevel(logging.INFO)
    
    # Create file handler for security logs
    if not security_logger.handlers:
        handler = logging.FileHandler('logs/security.log')
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        security_logger.addHandler(handler)
    
    return security_logger

# Export commonly used functions
__all__ = [
    'init_security',
    'validate_domain',
    'validate_email',
    'validate_password',
    'sanitize_input',
    'require_api_key',
    'require_https',
    'security_middleware',
    'validate_input',
    'get_security_config'
]
