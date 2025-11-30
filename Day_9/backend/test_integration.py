"""
E-Commerce Agent - Integration Testing Suite
Tests all backend endpoints and frontend components
"""

import requests
import json
from typing import Dict, List, Any
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "p1m0281@gmail.com"
TEST_USER = {
    "name": "Test User",
    "email": TEST_EMAIL,
    "phone": "9876543210",
    "address": "123 Test Street, Test City"
}

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'

class EcommerceTestSuite:
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.tests = []
        
    def print_header(self, text):
        print(f"\n{Colors.BLUE}{'='*50}{Colors.END}")
        print(f"{Colors.BLUE}{text}{Colors.END}")
        print(f"{Colors.BLUE}{'='*50}{Colors.END}\n")
    
    def print_test(self, name, passed, message=""):
        status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
        print(f"{status} | {name}")
        if message:
            print(f"       {Colors.YELLOW}{message}{Colors.END}")
    
    def test_health_check(self):
        """Test API health endpoint"""
        self.print_header("1. HEALTH CHECK")
        
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            passed = response.status_code == 200
            self.print_test("Health Check", passed, f"Status: {response.status_code}")
            self.passed += 1 if passed else 0
            self.failed += 1 if not passed else 0
            return passed
        except Exception as e:
            self.print_test("Health Check", False, str(e))
            self.failed += 1
            return False
    
    def test_catalog_endpoints(self):
        """Test all catalog endpoints"""
        self.print_header("2. CATALOG ENDPOINTS")
        
        tests = [
            {
                "name": "GET /acp/catalog",
                "method": "GET",
                "url": f"{BASE_URL}/acp/catalog",
                "expected_keys": ["success", "count", "products"]
            },
            {
                "name": "GET /acp/categories",
                "method": "GET",
                "url": f"{BASE_URL}/acp/categories",
                "expected_keys": ["success", "categories"]
            },
            {
                "name": "GET /acp/catalog?category=mug",
                "method": "GET",
                "url": f"{BASE_URL}/acp/catalog?category=mug",
                "expected_keys": ["success", "products"]
            },
            {
                "name": "GET /acp/products/search?q=coffee",
                "method": "GET",
                "url": f"{BASE_URL}/acp/products/search?q=coffee",
                "expected_keys": ["success", "products"]
            }
        ]
        
        for test in tests:
            try:
                response = requests.get(test["url"], timeout=5)
                passed = response.status_code == 200
                
                if passed:
                    data = response.json()
                    passed = all(key in data for key in test["expected_keys"])
                
                self.print_test(test["name"], passed, f"Status: {response.status_code}")
                self.passed += 1 if passed else 0
                self.failed += 1 if not passed else 0
            except Exception as e:
                self.print_test(test["name"], False, str(e))
                self.failed += 1
    
    def test_order_creation(self):
        """Test order creation endpoint"""
        self.print_header("3. ORDER CREATION")
        
        order_payload = {
            "line_items": [
                {
                    "product_id": "mug-001",
                    "name": "Coffee Mug",
                    "quantity": 2,
                    "unit_amount": 800,
                    "currency": "INR"
                }
            ],
            "buyer_info": TEST_USER
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/acp/orders",
                json=order_payload,
                timeout=5
            )
            passed = response.status_code == 200
            
            if passed:
                data = response.json()
                passed = "order" in data and "id" in data["order"]
                self.order_id = data["order"]["id"] if passed else None
            
            self.print_test("POST /acp/orders", passed, f"Status: {response.status_code}")
            self.passed += 1 if passed else 0
            self.failed += 1 if not passed else 0
            return passed
        except Exception as e:
            self.print_test("POST /acp/orders", False, str(e))
            self.failed += 1
            return False
    
    def test_order_retrieval(self):
        """Test order retrieval endpoints"""
        self.print_header("4. ORDER RETRIEVAL")
        
        if not hasattr(self, 'order_id') or not self.order_id:
            print(f"{Colors.YELLOW}⚠ Skipping order retrieval tests (no order created){Colors.END}")
            return
        
        tests = [
            {
                "name": f"GET /acp/orders/{self.order_id}",
                "url": f"{BASE_URL}/acp/orders/{self.order_id}",
                "expected_keys": ["success", "order"]
            },
            {
                "name": f"GET /acp/users/{TEST_EMAIL}/orders",
                "url": f"{BASE_URL}/acp/users/{TEST_EMAIL}/orders",
                "expected_keys": ["success", "orders"]
            }
        ]
        
        for test in tests:
            try:
                response = requests.get(test["url"], timeout=5)
                passed = response.status_code == 200
                
                if passed:
                    data = response.json()
                    passed = all(key in data for key in test["expected_keys"])
                
                self.print_test(test["name"], passed, f"Status: {response.status_code}")
                self.passed += 1 if passed else 0
                self.failed += 1 if not passed else 0
            except Exception as e:
                self.print_test(test["name"], False, str(e))
                self.failed += 1
    
    def test_spending_endpoints(self):
        """Test spending analytics endpoints"""
        self.print_header("5. SPENDING ANALYTICS")
        
        tests = [
            {
                "name": f"GET /acp/users/{TEST_EMAIL}/spending",
                "url": f"{BASE_URL}/acp/users/{TEST_EMAIL}/spending",
                "expected_keys": ["success", "total_spent"]
            }
        ]
        
        for test in tests:
            try:
                response = requests.get(test["url"], timeout=5)
                passed = response.status_code == 200
                
                if passed:
                    data = response.json()
                    passed = all(key in data for key in test["expected_keys"])
                
                self.print_test(test["name"], passed, f"Status: {response.status_code}")
                self.passed += 1 if passed else 0
                self.failed += 1 if not passed else 0
            except Exception as e:
                self.print_test(test["name"], False, str(e))
                self.failed += 1
    
    def test_cart_endpoints(self):
        """Test cart persistence endpoints"""
        self.print_header("6. CART PERSISTENCE")
        
        cart_items = [
            {
                "product_id": "tshirt-001",
                "name": "Cotton T-Shirt",
                "quantity": 1,
                "unit_amount": 1200,
                "currency": "INR",
                "line_total": 1200
            }
        ]
        
        # Test save cart
        try:
            response = requests.post(
                f"{BASE_URL}/acp/users/{TEST_EMAIL}/cart",
                json={"items": cart_items},
                timeout=5
            )
            passed = response.status_code == 200
            self.print_test(f"POST /acp/users/{TEST_EMAIL}/cart", passed, f"Status: {response.status_code}")
            self.passed += 1 if passed else 0
            self.failed += 1 if not passed else 0
        except Exception as e:
            self.print_test(f"POST /acp/users/{TEST_EMAIL}/cart", False, str(e))
            self.failed += 1
        
        # Test get cart
        try:
            response = requests.get(
                f"{BASE_URL}/acp/users/{TEST_EMAIL}/cart",
                timeout=5
            )
            passed = response.status_code == 200
            self.print_test(f"GET /acp/users/{TEST_EMAIL}/cart", passed, f"Status: {response.status_code}")
            self.passed += 1 if passed else 0
            self.failed += 1 if not passed else 0
        except Exception as e:
            self.print_test(f"GET /acp/users/{TEST_EMAIL}/cart", False, str(e))
            self.failed += 1
        
        # Test delete cart
        try:
            response = requests.delete(
                f"{BASE_URL}/acp/users/{TEST_EMAIL}/cart",
                timeout=5
            )
            passed = response.status_code == 200
            self.print_test(f"DELETE /acp/users/{TEST_EMAIL}/cart", passed, f"Status: {response.status_code}")
            self.passed += 1 if passed else 0
            self.failed += 1 if not passed else 0
        except Exception as e:
            self.print_test(f"DELETE /acp/users/{TEST_EMAIL}/cart", False, str(e))
            self.failed += 1
    
    def test_order_status_update(self):
        """Test order status update"""
        self.print_header("7. ORDER STATUS UPDATE")
        
        if not hasattr(self, 'order_id') or not self.order_id:
            print(f"{Colors.YELLOW}⚠ Skipping status update tests (no order created){Colors.END}")
            return
        
        try:
            response = requests.post(
                f"{BASE_URL}/acp/orders/{self.order_id}/status",
                json={"status": "processing"},
                timeout=5
            )
            passed = response.status_code == 200
            self.print_test(f"POST /acp/orders/{self.order_id}/status", passed, f"Status: {response.status_code}")
            self.passed += 1 if passed else 0
            self.failed += 1 if not passed else 0
        except Exception as e:
            self.print_test(f"POST /acp/orders/{self.order_id}/status", False, str(e))
            self.failed += 1
    
    def print_summary(self):
        """Print test summary"""
        self.print_header("TEST SUMMARY")
        
        total = self.passed + self.failed
        percentage = (self.passed / total * 100) if total > 0 else 0
        
        print(f"{Colors.GREEN}✓ Passed: {self.passed}{Colors.END}")
        print(f"{Colors.RED}✗ Failed: {self.failed}{Colors.END}")
        print(f"{'━'*50}")
        print(f"Total: {total} tests")
        print(f"Success Rate: {percentage:.1f}%")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}🎉 ALL TESTS PASSED!{Colors.END}")
        else:
            print(f"\n{Colors.YELLOW}⚠ Some tests failed. Check errors above.{Colors.END}")
    
    def run_all(self):
        """Run all tests"""
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        print(f"{Colors.BLUE}E-Commerce Agent - Integration Test Suite{Colors.END}")
        print(f"{Colors.BLUE}{'='*50}{Colors.END}")
        print(f"\nBase URL: {BASE_URL}")
        print(f"Test Email: {TEST_EMAIL}")
        print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        # Run all test groups
        if self.test_health_check():
            self.test_catalog_endpoints()
            self.test_order_creation()
            self.test_order_retrieval()
            self.test_spending_endpoints()
            self.test_cart_endpoints()
            self.test_order_status_update()
        else:
            print(f"\n{Colors.RED}❌ API is not responding. Cannot continue tests.{Colors.END}")
            print(f"Please ensure backend is running: python -m uvicorn api:app --host 0.0.0.0 --port 8000")
        
        self.print_summary()

if __name__ == "__main__":
    suite = EcommerceTestSuite()
    suite.run_all()
