from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from database import Base

class Domain(Base):
    __tablename__ = "domains"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    alert_threshold_days = Column(Integer, default=30)
    
    # Relationship to SSL checks
    ssl_checks = relationship("SSLCheck", back_populates="domain", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Domain(id={self.id}, name='{self.name}')>"

class SSLCheck(Base):
    __tablename__ = "ssl_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    domain_id = Column(Integer, ForeignKey("domains.id"), nullable=False)
    checked_at = Column(DateTime, default=datetime.utcnow)
    expires_in = Column(Integer)  # days until expiration
    is_valid = Column(Boolean)
    error_message = Column(Text, nullable=True)
    issuer = Column(String, nullable=True)
    subject = Column(String, nullable=True)
    not_valid_before = Column(DateTime, nullable=True)
    not_valid_after = Column(DateTime, nullable=True)
    
    # Relationship to domain
    domain = relationship("Domain", back_populates="ssl_checks")
    
    def __repr__(self):
        return f"<SSLCheck(id={self.id}, domain_id={self.domain_id}, expires_in={self.expires_in})>"

