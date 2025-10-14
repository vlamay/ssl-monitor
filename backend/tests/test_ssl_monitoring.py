"""
SSL Monitor Pro - Comprehensive Test Suite

This test suite covers all critical SSL monitoring functionality including:
- SSL certificate checking
- Domain management
- Notification triggers
- API endpoints
- Error handling
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app
from database import get_db
from models import Base, Domain, SSLCheck
from services.ssl_service import SSLChecker
from services.notification_service import NotificationService

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database for each test"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)

@pytest.fixture
def sample_domain_data():
    """Sample domain data for testing"""
    return {
        "name": "example.com",
        "alert_threshold_days": 30,
        "is_active": True
    }

@pytest.fixture
def sample_ssl_result():
    """Sample SSL check result"""
    return {
        "status": "healthy",
        "days_until_expiry": 89,
        "issuer": "Let's Encrypt Authority X3",
        "subject": "example.com",
        "not_valid_before": "2024-01-01T00:00:00",
        "not_valid_after": "2024-04-01T00:00:00",
        "is_valid": True,
        "expires_in": 89,
        "error": None
    }

class TestSSLMonitoring:
    """Test SSL monitoring core functionality"""
    
    @pytest.mark.asyncio
    async def test_ssl_check_valid_domain(self):
        """Test SSL check for valid domain"""
        checker = SSLChecker()
        
        # Mock SSL check for valid domain
        with patch.object(checker, 'check_domain') as mock_check:
            mock_check.return_value = {
                "status": "healthy",
                "days_until_expiry": 89,
                "issuer": "Let's Encrypt",
                "subject": "google.com",
                "is_valid": True,
                "expires_in": 89,
                "error": None
            }
            
            result = await checker.check_domain("google.com")
            
            assert result["status"] == "healthy"
            assert result["days_until_expiry"] > 0
            assert result["issuer"] is not None
            assert result["is_valid"] is True
    
    @pytest.mark.asyncio
    async def test_ssl_check_expired_domain(self):
        """Test SSL check for expired certificate"""
        checker = SSLChecker()
        
        with patch.object(checker, 'check_domain') as mock_check:
            mock_check.return_value = {
                "status": "critical",
                "days_until_expiry": -5,
                "issuer": "Expired CA",
                "subject": "expired.badssl.com",
                "is_valid": False,
                "expires_in": -5,
                "error": "Certificate has expired"
            }
            
            result = await checker.check_domain("expired.badssl.com")
            
            assert result["status"] == "critical"
            assert result["days_until_expiry"] < 0
            assert result["is_valid"] is False
    
    @pytest.mark.asyncio
    async def test_ssl_check_invalid_domain(self):
        """Test SSL check for non-existent domain"""
        checker = SSLChecker()
        
        with patch.object(checker, 'check_domain') as mock_check:
            mock_check.side_effect = Exception("Domain does not exist")
            
            with pytest.raises(Exception):
                await checker.check_domain("this-domain-does-not-exist-12345.com")
    
    def test_notification_trigger_30_days(self):
        """Test notification triggers at 30 days"""
        notification_service = NotificationService()
        
        # Mock notification methods
        with patch.object(notification_service, 'send_email') as mock_email, \
             patch.object(notification_service, 'send_telegram') as mock_telegram:
            
            # Test 30-day warning
            result = notification_service.check_and_notify(
                domain="example.com",
                days_until_expiry=30,
                threshold_days=30
            )
            
            assert result["notification_sent"] is True
            assert result["notification_type"] == "warning"
    
    def test_notification_trigger_7_days(self):
        """Test notification triggers at 7 days"""
        notification_service = NotificationService()
        
        with patch.object(notification_service, 'send_email') as mock_email, \
             patch.object(notification_service, 'send_telegram') as mock_telegram:
            
            # Test 7-day critical warning
            result = notification_service.check_and_notify(
                domain="example.com",
                days_until_expiry=7,
                threshold_days=30
            )
            
            assert result["notification_sent"] is True
            assert result["notification_type"] == "critical"
    
    def test_notification_trigger_expired(self):
        """Test notification triggers when expired"""
        notification_service = NotificationService()
        
        with patch.object(notification_service, 'send_email') as mock_email, \
             patch.object(notification_service, 'send_telegram') as mock_telegram:
            
            # Test expired certificate
            result = notification_service.check_and_notify(
                domain="example.com",
                days_until_expiry=-1,
                threshold_days=30
            )
            
            assert result["notification_sent"] is True
            assert result["notification_type"] == "expired"

class TestAPIEndpoints:
    """Test API endpoints"""
    
    def test_create_domain(self, client, sample_domain_data, db_session):
        """Test domain creation endpoint"""
        response = client.post("/domains/", json=sample_domain_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == sample_domain_data["name"]
        assert data["alert_threshold_days"] == sample_domain_data["alert_threshold_days"]
        assert "id" in data
        assert "created_at" in data
    
    def test_create_duplicate_domain(self, client, sample_domain_data, db_session):
        """Test creating duplicate domain"""
        # Create first domain
        client.post("/domains/", json=sample_domain_data)
        
        # Try to create duplicate
        response = client.post("/domains/", json=sample_domain_data)
        
        assert response.status_code == 409
        assert "already exists" in response.json()["detail"]
    
    def test_list_domains(self, client, sample_domain_data, db_session):
        """Test listing domains"""
        # Create test domains
        client.post("/domains/", json=sample_domain_data)
        client.post("/domains/", json={"name": "test.com", "alert_threshold_days": 14})
        
        response = client.get("/domains/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert any(d["name"] == "example.com" for d in data)
        assert any(d["name"] == "test.com" for d in data)
    
    def test_get_domain(self, client, sample_domain_data, db_session):
        """Test getting domain details"""
        # Create domain
        create_response = client.post("/domains/", json=sample_domain_data)
        domain_id = create_response.json()["id"]
        
        response = client.get(f"/domains/{domain_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == sample_domain_data["name"]
    
    def test_update_domain(self, client, sample_domain_data, db_session):
        """Test updating domain"""
        # Create domain
        create_response = client.post("/domains/", json=sample_domain_data)
        domain_id = create_response.json()["id"]
        
        # Update domain
        update_data = {"alert_threshold_days": 14, "is_active": False}
        response = client.patch(f"/domains/{domain_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["alert_threshold_days"] == 14
        assert data["is_active"] is False
    
    def test_delete_domain(self, client, sample_domain_data, db_session):
        """Test deleting domain"""
        # Create domain
        create_response = client.post("/domains/", json=sample_domain_data)
        domain_id = create_response.json()["id"]
        
        # Delete domain
        response = client.delete(f"/domains/{domain_id}")
        
        assert response.status_code == 204
        
        # Verify domain is deleted
        get_response = client.get(f"/domains/{domain_id}")
        assert get_response.status_code == 404
    
    @patch('services.ssl_service.SSLChecker.check_ssl_certificate')
    def test_ssl_check_endpoint(self, mock_ssl_check, client, sample_domain_data, sample_ssl_result, db_session):
        """Test SSL check endpoint"""
        # Create domain
        create_response = client.post("/domains/", json=sample_domain_data)
        domain_id = create_response.json()["id"]
        
        # Mock SSL check result
        mock_ssl_check.return_value = sample_ssl_result
        
        # Trigger SSL check
        response = client.post(f"/domains/{domain_id}/check")
        
        assert response.status_code == 200
        data = response.json()
        assert data["domain_name"] == sample_domain_data["name"]
        assert data["is_valid"] is True
        assert data["expires_in"] == 89
        assert data["status"] == "healthy"
    
    def test_ssl_status_endpoint_no_checks(self, client, sample_domain_data, db_session):
        """Test SSL status endpoint when no checks exist"""
        # Create domain
        create_response = client.post("/domains/", json=sample_domain_data)
        domain_id = create_response.json()["id"]
        
        # Get SSL status (no checks yet)
        response = client.get(f"/domains/{domain_id}/ssl-status")
        
        assert response.status_code == 404
        assert "No SSL checks found" in response.json()["detail"]
    
    @patch('services.ssl_service.SSLChecker.check_ssl_certificate')
    def test_ssl_status_endpoint_with_checks(self, mock_ssl_check, client, sample_domain_data, sample_ssl_result, db_session):
        """Test SSL status endpoint with existing checks"""
        # Create domain
        create_response = client.post("/domains/", json=sample_domain_data)
        domain_id = create_response.json()["id"]
        
        # Mock SSL check result
        mock_ssl_check.return_value = sample_ssl_result
        
        # Create SSL check
        client.post(f"/domains/{domain_id}/check")
        
        # Get SSL status
        response = client.get(f"/domains/{domain_id}/ssl-status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["domain_name"] == sample_domain_data["name"]
        assert data["is_valid"] is True
    
    def test_statistics_endpoint(self, client, sample_domain_data, db_session):
        """Test statistics endpoint"""
        # Create test domains
        client.post("/domains/", json=sample_domain_data)
        client.post("/domains/", json={"name": "test.com", "alert_threshold_days": 14})
        
        response = client.get("/statistics")
        
        assert response.status_code == 200
        data = response.json()
        assert data["total_domains"] == 2
        assert data["active_domains"] == 2
        assert "domains_with_errors" in data
        assert "domains_expiring_soon" in data
        assert "domains_expired" in data

class TestHealthChecks:
    """Test health check endpoints"""
    
    def test_health_check_endpoint(self, client):
        """Test main health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ["healthy", "degraded"]
        assert "timestamp" in data
        assert "checks" in data
    
    def test_readiness_check(self, client):
        """Test readiness check endpoint"""
        response = client.get("/ready")
        
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert "timestamp" in data
    
    def test_liveness_check(self, client):
        """Test liveness check endpoint"""
        response = client.get("/live")
        
        assert response.status_code == 200
        data = response.json()
        assert data["alive"] is True
        assert "timestamp" in data

class TestErrorHandling:
    """Test error handling scenarios"""
    
    def test_invalid_domain_id(self, client):
        """Test handling of invalid domain ID"""
        response = client.get("/domains/999999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_invalid_domain_data(self, client):
        """Test handling of invalid domain data"""
        invalid_data = {"name": "", "alert_threshold_days": -1}
        
        response = client.post("/domains/", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_ssl_check_invalid_domain(self, client, db_session):
        """Test SSL check with invalid domain ID"""
        response = client.post("/domains/999999/check")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

class TestPerformance:
    """Test performance characteristics"""
    
    def test_api_response_time(self, client):
        """Test API response times are acceptable"""
        import time
        
        start_time = time.time()
        response = client.get("/health")
        end_time = time.time()
        
        response_time = end_time - start_time
        assert response.status_code == 200
        assert response_time < 1.0  # Should respond within 1 second
    
    def test_concurrent_requests(self, client, sample_domain_data, db_session):
        """Test handling of concurrent requests"""
        import threading
        import time
        
        results = []
        
        def make_request():
            response = client.get("/health")
            results.append(response.status_code)
        
        # Create multiple threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert len(results) == 10
        assert all(status == 200 for status in results)

# Integration tests
class TestIntegration:
    """Integration tests for complete workflows"""
    
    @patch('services.ssl_service.SSLChecker.check_ssl_certificate')
    @patch('services.notification_service.NotificationService.send_email')
    def test_complete_monitoring_workflow(self, mock_email, mock_ssl_check, client, sample_domain_data, sample_ssl_result, db_session):
        """Test complete monitoring workflow"""
        # Mock SSL check result
        mock_ssl_check.return_value = sample_ssl_result
        
        # 1. Create domain
        create_response = client.post("/domains/", json=sample_domain_data)
        domain_id = create_response.json()["id"]
        
        # 2. Trigger SSL check
        check_response = client.post(f"/domains/{domain_id}/check")
        assert check_response.status_code == 200
        
        # 3. Get SSL status
        status_response = client.get(f"/domains/{domain_id}/ssl-status")
        assert status_response.status_code == 200
        
        # 4. Get check history
        history_response = client.get(f"/domains/{domain_id}/checks")
        assert history_response.status_code == 200
        assert len(history_response.json()) == 1
        
        # 5. Get statistics
        stats_response = client.get("/statistics")
        assert stats_response.status_code == 200
        
        # Verify all steps completed successfully
        assert create_response.status_code == 201
        assert check_response.status_code == 200
        assert status_response.status_code == 200
        assert history_response.status_code == 200
        assert stats_response.status_code == 200

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
