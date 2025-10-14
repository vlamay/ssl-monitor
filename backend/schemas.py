from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Domain Schemas
class DomainBase(BaseModel):
    name: str = Field(..., description="Domain name (e.g., example.com)")
    alert_threshold_days: int = Field(default=30, description="Alert when SSL expires in N days")

class DomainCreate(DomainBase):
    pass

class DomainUpdate(BaseModel):
    is_active: Optional[bool] = None
    alert_threshold_days: Optional[int] = None

class Domain(DomainBase):
    id: int
    created_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True

# SSL Check Schemas
class SSLCheckBase(BaseModel):
    expires_in: Optional[int] = None
    is_valid: bool
    error_message: Optional[str] = None
    issuer: Optional[str] = None
    subject: Optional[str] = None
    not_valid_before: Optional[datetime] = None
    not_valid_after: Optional[datetime] = None

class SSLCheck(SSLCheckBase):
    id: int
    domain_id: int
    checked_at: datetime
    
    class Config:
        from_attributes = True

class SSLStatus(BaseModel):
    domain_name: str
    is_valid: bool
    expires_in: Optional[int] = None
    not_valid_after: Optional[datetime] = None
    last_checked: Optional[datetime] = None
    error_message: Optional[str] = None
    status: str  # "healthy", "warning", "critical", "error"

class DomainWithChecks(Domain):
    ssl_checks: List[SSLCheck] = []
    latest_check: Optional[SSLCheck] = None
    
    class Config:
        from_attributes = True

# Statistics Schema
class Statistics(BaseModel):
    total_domains: int
    active_domains: int
    domains_with_errors: int
    domains_expiring_soon: int  # within threshold
    domains_expired: int

