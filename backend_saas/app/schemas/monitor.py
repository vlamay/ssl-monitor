"""
Monitor schemas
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, Field
from app.models.monitor import MonitorStatus, SSLCertStatus


class MonitorBase(BaseModel):
    """Base monitor schema"""
    domain: str = Field(..., min_length=1, max_length=255)
    port: int = Field(default=443, ge=1, le=65535)
    check_interval: int = Field(default=3600, ge=300, le=86400)  # 5 min to 24 hours
    alert_before_days: int = Field(default=30, ge=1, le=365)


class MonitorCreate(MonitorBase):
    """Monitor creation schema"""
    enabled_notifications: Optional[List[str]] = None


class MonitorUpdate(BaseModel):
    """Monitor update schema"""
    port: Optional[int] = Field(None, ge=1, le=65535)
    check_interval: Optional[int] = Field(None, ge=300, le=86400)
    alert_before_days: Optional[int] = Field(None, ge=1, le=365)
    enabled_notifications: Optional[List[str]] = None


class MonitorInDB(MonitorBase):
    """Monitor in database schema"""
    id: int
    user_id: int
    status: MonitorStatus
    ssl_status: SSLCertStatus
    issuer: Optional[str]
    subject: Optional[str]
    serial_number: Optional[str]
    fingerprint: Optional[str]
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    last_checked_at: Optional[datetime]
    last_successful_check: Optional[datetime]
    last_error: Optional[str]
    consecutive_errors: int
    response_time_ms: Optional[float]
    uptime_percentage: float
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class Monitor(MonitorInDB):
    """Monitor response schema"""
    days_until_expiry: Optional[int]
    is_expiring_soon: bool
    is_expired: bool
    should_check: bool


class MonitorCheckResultBase(BaseModel):
    """Base check result schema"""
    check_type: str = "ssl_cert"
    success: bool


class MonitorCheckResultCreate(MonitorCheckResultBase):
    """Check result creation schema"""
    monitor_id: int
    issuer: Optional[str] = None
    subject: Optional[str] = None
    serial_number: Optional[str] = None
    fingerprint: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    response_time_ms: Optional[float] = None
    connection_time_ms: Optional[float] = None
    handshake_time_ms: Optional[float] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    certificate_chain_length: Optional[int] = None
    cipher_suite: Optional[str] = None
    protocol_version: Optional[str] = None


class MonitorCheckResult(MonitorCheckResultBase):
    """Check result response schema"""
    id: int
    monitor_id: int
    issuer: Optional[str]
    subject: Optional[str]
    serial_number: Optional[str]
    fingerprint: Optional[str]
    valid_from: Optional[datetime]
    valid_until: Optional[datetime]
    response_time_ms: Optional[float]
    connection_time_ms: Optional[float]
    handshake_time_ms: Optional[float]
    error_code: Optional[str]
    error_message: Optional[str]
    certificate_chain_length: Optional[int]
    cipher_suite: Optional[str]
    protocol_version: Optional[str]
    checked_at: datetime
    days_until_expiry: Optional[int]
    
    class Config:
        from_attributes = True


class MonitorStats(BaseModel):
    """Monitor statistics schema"""
    total_monitors: int
    active_monitors: int
    expired_certificates: int
    expiring_soon: int
    average_response_time: Optional[float]
    overall_uptime: float
