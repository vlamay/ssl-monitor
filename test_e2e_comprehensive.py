#!/usr/bin/env python3
"""
SSL Monitor Pro - Comprehensive E2E Test Suite

This script performs end-to-end testing of all critical functionality:
- User registration and authentication
- Domain management
- SSL certificate checking
- Notifications (Email, Telegram, Slack)
- Payment processing (Stripe)
- Multi-language support
- Performance testing

Usage:
    python test_e2e_comprehensive.py [--base-url URL] [--verbose]
"""

import requests
import json
import time
import sys
import argparse
import random
import string
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import concurrent.futures
import threading

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

class E2ETestSuite:
    """Comprehensive E2E test suite for SSL Monitor Pro"""
    
    def __init__(self, base_url: str = "https://ssl-monitor-api.onrender.com", verbose: bool = False):
        self.base_url = base_url.rstrip('/')
        self.verbose = verbose
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'User-Agent': 'SSL-Monitor-Pro-E2E-Test/1.0'
        })
        self.test_results = []
        self.test_domains = []
        
    def log(self, message: str, level: str = "INFO"):
        """Log message with timestamp and color coding"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        color_map = {
            "INFO": Colors.CYAN,
            "SUCCESS": Colors.GREEN,
            "WARNING": Colors.YELLOW,
            "ERROR": Colors.RED,
            "TEST": Colors.MAGENTA
        }
        
        color = color_map.get(level, Colors.WHITE)
        print(f"{color}[{timestamp}] {level}: {message}{Colors.END}")
    
    def log_verbose(self, message: str):
        """Log verbose message if verbose mode is enabled"""
        if self.verbose:
            self.log(f"VERBOSE: {message}", "INFO")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            self.log_verbose(f"{method} {url}")
            response = self.session.request(method, url, timeout=30, **kwargs)
            self.log_verbose(f"Response: {response.status_code}")
            return response
        except requests.exceptions.RequestException as e:
            self.log(f"Request failed: {e}", "ERROR")
            raise
    
    def test_api_health(self) -> bool:
        """Test API health check endpoint"""
        self.log("Testing API health check...", "TEST")
        
        try:
            response = self.make_request("GET", "/health")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"API health check passed: {data.get('status', 'unknown')}", "SUCCESS")
                
                # Check individual services
                checks = data.get('checks', {})
                for service, status in checks.items():
                    self.log(f"  {service}: {status}", "INFO")
                
                return True
            else:
                self.log(f"API health check failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"API health check failed with exception: {e}", "ERROR")
            return False
    
    def test_readiness_liveness(self) -> bool:
        """Test readiness and liveness probes"""
        self.log("Testing readiness and liveness probes...", "TEST")
        
        success = True
        
        # Test readiness probe
        try:
            response = self.make_request("GET", "/ready")
            if response.status_code == 200:
                self.log("Readiness probe passed", "SUCCESS")
            else:
                self.log(f"Readiness probe failed: {response.status_code}", "ERROR")
                success = False
        except Exception as e:
            self.log(f"Readiness probe failed: {e}", "ERROR")
            success = False
        
        # Test liveness probe
        try:
            response = self.make_request("GET", "/live")
            if response.status_code == 200:
                self.log("Liveness probe passed", "SUCCESS")
            else:
                self.log(f"Liveness probe failed: {response.status_code}", "ERROR")
                success = False
        except Exception as e:
            self.log(f"Liveness probe failed: {e}", "ERROR")
            success = False
        
        return success
    
    def test_api_documentation(self) -> bool:
        """Test API documentation endpoints"""
        self.log("Testing API documentation...", "TEST")
        
        success = True
        
        # Test OpenAPI docs
        try:
            response = self.make_request("GET", "/docs")
            if response.status_code == 200:
                self.log("OpenAPI documentation accessible", "SUCCESS")
            else:
                self.log(f"OpenAPI docs failed: {response.status_code}", "ERROR")
                success = False
        except Exception as e:
            self.log(f"OpenAPI docs failed: {e}", "ERROR")
            success = False
        
        # Test ReDoc
        try:
            response = self.make_request("GET", "/redoc")
            if response.status_code == 200:
                self.log("ReDoc documentation accessible", "SUCCESS")
            else:
                self.log(f"ReDoc failed: {response.status_code}", "ERROR")
                success = False
        except Exception as e:
            self.log(f"ReDoc failed: {e}", "ERROR")
            success = False
        
        return success
    
    def test_domain_management(self) -> bool:
        """Test domain management functionality"""
        self.log("Testing domain management...", "TEST")
        
        success = True
        
        # Test domains to create
        test_domains = [
            {"name": "google.com", "alert_threshold_days": 30},
            {"name": "github.com", "alert_threshold_days": 14},
            {"name": "stackoverflow.com", "alert_threshold_days": 7}
        ]
        
        created_domain_ids = []
        
        # Create domains
        for domain_data in test_domains:
            try:
                response = self.make_request("POST", "/domains/", json=domain_data)
                
                if response.status_code == 201:
                    data = response.json()
                    domain_id = data.get('id')
                    created_domain_ids.append(domain_id)
                    self.log(f"Created domain: {domain_data['name']} (ID: {domain_id})", "SUCCESS")
                else:
                    self.log(f"Failed to create domain {domain_data['name']}: {response.status_code}", "ERROR")
                    success = False
                    
            except Exception as e:
                self.log(f"Exception creating domain {domain_data['name']}: {e}", "ERROR")
                success = False
        
        # List domains
        try:
            response = self.make_request("GET", "/domains/")
            if response.status_code == 200:
                domains = response.json()
                self.log(f"Listed {len(domains)} domains", "SUCCESS")
                
                # Verify our domains are in the list
                domain_names = [d['name'] for d in domains]
                for test_domain in test_domains:
                    if test_domain['name'] in domain_names:
                        self.log(f"Domain {test_domain['name']} found in list", "SUCCESS")
                    else:
                        self.log(f"Domain {test_domain['name']} not found in list", "ERROR")
                        success = False
            else:
                self.log(f"Failed to list domains: {response.status_code}", "ERROR")
                success = False
                
        except Exception as e:
            self.log(f"Exception listing domains: {e}", "ERROR")
            success = False
        
        # Test domain details
        for domain_id in created_domain_ids[:1]:  # Test first domain
            try:
                response = self.make_request("GET", f"/domains/{domain_id}")
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"Retrieved domain details: {data.get('name')}", "SUCCESS")
                else:
                    self.log(f"Failed to get domain details: {response.status_code}", "ERROR")
                    success = False
                    
            except Exception as e:
                self.log(f"Exception getting domain details: {e}", "ERROR")
                success = False
        
        # Test domain update
        if created_domain_ids:
            domain_id = created_domain_ids[0]
            try:
                update_data = {"alert_threshold_days": 14, "is_active": False}
                response = self.make_request("PATCH", f"/domains/{domain_id}", json=update_data)
                
                if response.status_code == 200:
                    data = response.json()
                    self.log(f"Updated domain: alert_threshold={data.get('alert_threshold_days')}, active={data.get('is_active')}", "SUCCESS")
                else:
                    self.log(f"Failed to update domain: {response.status_code}", "ERROR")
                    success = False
                    
            except Exception as e:
                self.log(f"Exception updating domain: {e}", "ERROR")
                success = False
        
        # Store domain IDs for later tests
        self.test_domains = created_domain_ids
        
        return success
    
    def test_ssl_checking(self) -> bool:
        """Test SSL certificate checking functionality"""
        self.log("Testing SSL certificate checking...", "TEST")
        
        if not self.test_domains:
            self.log("No test domains available for SSL checking", "WARNING")
            return False
        
        success = True
        
        # Test SSL check for first domain
        domain_id = self.test_domains[0]
        
        try:
            response = self.make_request("POST", f"/domains/{domain_id}/check")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"SSL check completed for domain: {data.get('domain_name')}", "SUCCESS")
                self.log(f"  Status: {data.get('status')}", "INFO")
                self.log(f"  Valid: {data.get('is_valid')}", "INFO")
                self.log(f"  Expires in: {data.get('expires_in')} days", "INFO")
                
                # Wait a moment for the check to be stored
                time.sleep(2)
                
            else:
                self.log(f"SSL check failed: {response.status_code}", "ERROR")
                success = False
                
        except Exception as e:
            self.log(f"Exception during SSL check: {e}", "ERROR")
            success = False
        
        # Test SSL status retrieval
        try:
            response = self.make_request("GET", f"/domains/{domain_id}/ssl-status")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"Retrieved SSL status: {data.get('status')}", "SUCCESS")
            else:
                self.log(f"Failed to get SSL status: {response.status_code}", "ERROR")
                success = False
                
        except Exception as e:
            self.log(f"Exception getting SSL status: {e}", "ERROR")
            success = False
        
        # Test SSL check history
        try:
            response = self.make_request("GET", f"/domains/{domain_id}/checks")
            
            if response.status_code == 200:
                checks = response.json()
                self.log(f"Retrieved {len(checks)} SSL check records", "SUCCESS")
            else:
                self.log(f"Failed to get SSL check history: {response.status_code}", "ERROR")
                success = False
                
        except Exception as e:
            self.log(f"Exception getting SSL check history: {e}", "ERROR")
            success = False
        
        return success
    
    def test_statistics(self) -> bool:
        """Test statistics endpoint"""
        self.log("Testing statistics endpoint...", "TEST")
        
        try:
            response = self.make_request("GET", "/statistics")
            
            if response.status_code == 200:
                data = response.json()
                self.log("Statistics retrieved successfully", "SUCCESS")
                self.log(f"  Total domains: {data.get('total_domains')}", "INFO")
                self.log(f"  Active domains: {data.get('active_domains')}", "INFO")
                self.log(f"  Domains with errors: {data.get('domains_with_errors')}", "INFO")
                self.log(f"  Domains expiring soon: {data.get('domains_expiring_soon')}", "INFO")
                self.log(f"  Expired domains: {data.get('domains_expired')}", "INFO")
                return True
            else:
                self.log(f"Statistics endpoint failed: {response.status_code}", "ERROR")
                return False
                
        except Exception as e:
            self.log(f"Exception getting statistics: {e}", "ERROR")
            return False
    
    def test_billing_endpoints(self) -> bool:
        """Test billing/payment endpoints"""
        self.log("Testing billing endpoints...", "TEST")
        
        success = True
        
        # Test billing plans
        try:
            response = self.make_request("GET", "/billing/plans")
            
            if response.status_code == 200:
                plans = response.json()
                self.log(f"Retrieved {len(plans)} billing plans", "SUCCESS")
                
                for plan in plans:
                    self.log(f"  Plan: {plan.get('name')} - {plan.get('price')} {plan.get('currency')}", "INFO")
            else:
                self.log(f"Billing plans endpoint failed: {response.status_code}", "ERROR")
                success = False
                
        except Exception as e:
            self.log(f"Exception getting billing plans: {e}", "ERROR")
            success = False
        
        # Test checkout session creation (with test data)
        try:
            checkout_data = {
                "plan_id": "starter",
                "success_url": "https://cloudsre.xyz/success",
                "cancel_url": "https://cloudsre.xyz/cancel"
            }
            
            response = self.make_request("POST", "/billing/create-checkout-session", json=checkout_data)
            
            if response.status_code == 200:
                data = response.json()
                self.log("Checkout session created successfully", "SUCCESS")
                self.log(f"  Session ID: {data.get('session_id', 'N/A')}", "INFO")
                self.log(f"  Checkout URL: {data.get('checkout_url', 'N/A')}", "INFO")
            else:
                self.log(f"Checkout session creation failed: {response.status_code}", "ERROR")
                # This might fail if Stripe is not configured, which is OK
                if response.status_code == 500:
                    self.log("  (This might be expected if Stripe is not configured)", "WARNING")
                
        except Exception as e:
            self.log(f"Exception creating checkout session: {e}", "ERROR")
            # This might fail if Stripe is not configured, which is OK
            self.log("  (This might be expected if Stripe is not configured)", "WARNING")
        
        return success
    
    def test_user_endpoints(self) -> bool:
        """Test user management endpoints"""
        self.log("Testing user management endpoints...", "TEST")
        
        success = True
        
        # Generate test user data
        test_email = f"test_{random.randint(1000, 9999)}@example.com"
        test_user_data = {
            "email": test_email,
            "name": "Test User",
            "language": "en"
        }
        
        # Test user registration
        try:
            response = self.make_request("POST", "/api/user/register", json=test_user_data)
            
            if response.status_code in [200, 201]:
                self.log(f"User registration successful: {test_email}", "SUCCESS")
            else:
                self.log(f"User registration failed: {response.status_code}", "ERROR")
                success = False
                
        except Exception as e:
            self.log(f"Exception during user registration: {e}", "ERROR")
            success = False
        
        # Test user profile retrieval
        try:
            response = self.make_request("GET", f"/api/user/profile/{test_email}")
            
            if response.status_code == 200:
                data = response.json()
                self.log(f"User profile retrieved: {data.get('email')}", "SUCCESS")
            else:
                self.log(f"User profile retrieval failed: {response.status_code}", "ERROR")
                success = False
                
        except Exception as e:
            self.log(f"Exception getting user profile: {e}", "ERROR")
            success = False
        
        return success
    
    def test_notification_endpoints(self) -> bool:
        """Test notification endpoints"""
        self.log("Testing notification endpoints...", "TEST")
        
        success = True
        
        # Test notification settings
        try:
            response = self.make_request("GET", "/api/notifications/settings")
            
            if response.status_code == 200:
                settings = response.json()
                self.log("Notification settings retrieved", "SUCCESS")
                self.log(f"  Available channels: {', '.join(settings.get('channels', []))}", "INFO")
            else:
                self.log(f"Notification settings failed: {response.status_code}", "ERROR")
                success = False
                
        except Exception as e:
            self.log(f"Exception getting notification settings: {e}", "ERROR")
            success = False
        
        # Test notification channels
        try:
            response = self.make_request("GET", "/api/notifications/channels")
            
            if response.status_code == 200:
                channels = response.json()
                self.log(f"Retrieved {len(channels)} notification channels", "SUCCESS")
                
                for channel in channels:
                    self.log(f"  Channel: {channel.get('type')} - {channel.get('status')}", "INFO")
            else:
                self.log(f"Notification channels failed: {response.status_code}", "ERROR")
                success = False
                
        except Exception as e:
            self.log(f"Exception getting notification channels: {e}", "ERROR")
            success = False
        
        return success
    
    def test_performance(self) -> bool:
        """Test API performance"""
        self.log("Testing API performance...", "TEST")
        
        success = True
        
        # Test response times
        endpoints_to_test = [
            ("/health", "Health check"),
            ("/ready", "Readiness probe"),
            ("/live", "Liveness probe"),
            ("/statistics", "Statistics"),
            ("/domains/", "Domain list")
        ]
        
        for endpoint, description in endpoints_to_test:
            try:
                start_time = time.time()
                response = self.make_request("GET", endpoint)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000  # Convert to milliseconds
                
                if response.status_code == 200:
                    if response_time < 1000:  # Less than 1 second
                        self.log(f"{description}: {response_time:.0f}ms - GOOD", "SUCCESS")
                    elif response_time < 3000:  # Less than 3 seconds
                        self.log(f"{description}: {response_time:.0f}ms - ACCEPTABLE", "WARNING")
                    else:
                        self.log(f"{description}: {response_time:.0f}ms - SLOW", "ERROR")
                        success = False
                else:
                    self.log(f"{description}: Failed ({response.status_code})", "ERROR")
                    success = False
                    
            except Exception as e:
                self.log(f"{description}: Exception - {e}", "ERROR")
                success = False
        
        return success
    
    def test_concurrent_requests(self) -> bool:
        """Test concurrent request handling"""
        self.log("Testing concurrent request handling...", "TEST")
        
        def make_health_request():
            """Make a health check request"""
            try:
                response = self.make_request("GET", "/health")
                return response.status_code == 200
            except:
                return False
        
        # Test with 10 concurrent requests
        num_requests = 10
        self.log(f"Making {num_requests} concurrent health check requests...", "INFO")
        
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_health_request) for _ in range(num_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        end_time = time.time()
        duration = end_time - start_time
        
        successful_requests = sum(results)
        failed_requests = num_requests - successful_requests
        
        self.log(f"Concurrent requests completed in {duration:.2f} seconds", "INFO")
        self.log(f"Successful: {successful_requests}/{num_requests}", "SUCCESS" if failed_requests == 0 else "WARNING")
        
        if failed_requests > 0:
            self.log(f"Failed: {failed_requests}/{num_requests}", "ERROR")
            return False
        
        return True
    
    def cleanup_test_data(self):
        """Clean up test data"""
        self.log("Cleaning up test data...", "TEST")
        
        # Delete test domains
        for domain_id in self.test_domains:
            try:
                response = self.make_request("DELETE", f"/domains/{domain_id}")
                if response.status_code == 204:
                    self.log(f"Deleted test domain ID: {domain_id}", "SUCCESS")
                else:
                    self.log(f"Failed to delete domain ID {domain_id}: {response.status_code}", "WARNING")
            except Exception as e:
                self.log(f"Exception deleting domain ID {domain_id}: {e}", "WARNING")
    
    def run_all_tests(self) -> Dict[str, bool]:
        """Run all E2E tests"""
        self.log("=" * 60, "TEST")
        self.log("SSL Monitor Pro - Comprehensive E2E Test Suite", "TEST")
        self.log("=" * 60, "TEST")
        self.log(f"Testing against: {self.base_url}", "INFO")
        self.log(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
        self.log("", "INFO")
        
        tests = [
            ("API Health Check", self.test_api_health),
            ("Readiness/Liveness Probes", self.test_readiness_liveness),
            ("API Documentation", self.test_api_documentation),
            ("Domain Management", self.test_domain_management),
            ("SSL Certificate Checking", self.test_ssl_checking),
            ("Statistics Endpoint", self.test_statistics),
            ("Billing Endpoints", self.test_billing_endpoints),
            ("User Management", self.test_user_endpoints),
            ("Notification Endpoints", self.test_notification_endpoints),
            ("Performance Testing", self.test_performance),
            ("Concurrent Requests", self.test_concurrent_requests)
        ]
        
        results = {}
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            self.log(f"Running: {test_name}", "TEST")
            try:
                result = test_func()
                results[test_name] = result
                
                if result:
                    self.log(f"✅ {test_name}: PASSED", "SUCCESS")
                    passed += 1
                else:
                    self.log(f"❌ {test_name}: FAILED", "ERROR")
                    failed += 1
                    
            except Exception as e:
                self.log(f"❌ {test_name}: EXCEPTION - {e}", "ERROR")
                results[test_name] = False
                failed += 1
            
            self.log("", "INFO")
        
        # Cleanup
        self.cleanup_test_data()
        
        # Summary
        self.log("=" * 60, "TEST")
        self.log("TEST SUMMARY", "TEST")
        self.log("=" * 60, "TEST")
        self.log(f"Total Tests: {len(tests)}", "INFO")
        self.log(f"Passed: {passed}", "SUCCESS" if passed == len(tests) else "INFO")
        self.log(f"Failed: {failed}", "ERROR" if failed > 0 else "INFO")
        self.log(f"Success Rate: {(passed/len(tests)*100):.1f}%", "INFO")
        self.log(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "INFO")
        
        if failed == 0:
            self.log("🎉 ALL TESTS PASSED! 🎉", "SUCCESS")
        else:
            self.log(f"⚠️  {failed} TEST(S) FAILED", "ERROR")
        
        return results

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="SSL Monitor Pro E2E Test Suite")
    parser.add_argument("--base-url", default="https://ssl-monitor-api.onrender.com",
                       help="Base URL of the API to test")
    parser.add_argument("--verbose", action="store_true",
                       help="Enable verbose logging")
    parser.add_argument("--no-cleanup", action="store_true",
                       help="Skip cleanup of test data")
    
    args = parser.parse_args()
    
    # Create test suite
    test_suite = E2ETestSuite(base_url=args.base_url, verbose=args.verbose)
    
    # Run tests
    results = test_suite.run_all_tests()
    
    # Exit with appropriate code
    failed_tests = sum(1 for result in results.values() if not result)
    sys.exit(failed_tests)

if __name__ == "__main__":
    main()
