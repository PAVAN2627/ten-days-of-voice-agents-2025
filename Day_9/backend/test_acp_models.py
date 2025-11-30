"""
Tests for Type-Safe ACP Models
Validates Pydantic model validation and type safety
"""

import pytest
from pydantic import ValidationError
from datetime import datetime

from acp_models import (
    Product, LineItem, Buyer, Order, CartItem,
    OrderStatus, ProductFilter, OrderCreateRequest
)


class TestProduct:
    """Test Product model validation"""
    
    def test_valid_product(self):
        """Valid product should pass"""
        product = Product(
            id="test-001",
            name="Test Product",
            price=100.0,
            currency="INR",
            category="test",
            description="A test product"
        )
        assert product.id == "test-001"
        assert product.price == 100.0
    
    def test_negative_price_fails(self):
        """Negative price should fail"""
        with pytest.raises(ValidationError):
            Product(
                id="test-001",
                name="Test Product",
                price=-100.0,
                currency="INR",
                category="test"
            )
    
    def test_zero_price_fails(self):
        """Zero price should fail"""
        with pytest.raises(ValidationError):
            Product(
                id="test-001",
                name="Test Product",
                price=0,
                currency="INR",
                category="test"
            )
    
    def test_missing_required_fields(self):
        """Missing required fields should fail"""
        with pytest.raises(ValidationError):
            Product(name="Test Product")


class TestLineItem:
    """Test LineItem model validation"""
    
    def test_valid_line_item(self):
        """Valid line item should pass"""
        item = LineItem(
            product_id="test-001",
            name="Test Product",
            quantity=2,
            unit_amount=100.0,
            currency="INR",
            line_total=200.0
        )
        assert item.quantity == 2
        assert item.line_total == 200.0
    
    def test_line_total_validation(self):
        """Line total must match quantity * unit_amount"""
        with pytest.raises(ValidationError):
            LineItem(
                product_id="test-001",
                name="Test Product",
                quantity=2,
                unit_amount=100.0,
                currency="INR",
                line_total=150.0  # Wrong total
            )
    
    def test_zero_quantity_fails(self):
        """Zero quantity should fail"""
        with pytest.raises(ValidationError):
            LineItem(
                product_id="test-001",
                name="Test Product",
                quantity=0,
                unit_amount=100.0,
                currency="INR",
                line_total=0
            )
    
    def test_negative_quantity_fails(self):
        """Negative quantity should fail"""
        with pytest.raises(ValidationError):
            LineItem(
                product_id="test-001",
                name="Test Product",
                quantity=-1,
                unit_amount=100.0,
                currency="INR",
                line_total=-100.0
            )


class TestBuyer:
    """Test Buyer model validation"""
    
    def test_valid_buyer(self):
        """Valid buyer should pass"""
        buyer = Buyer(
            name="John Doe",
            email="john@example.com",
            phone="+91-9876543210",
            address="123 Main St"
        )
        assert buyer.name == "John Doe"
        assert buyer.email == "john@example.com"
    
    def test_invalid_email_fails(self):
        """Invalid email should fail"""
        with pytest.raises(ValidationError):
            Buyer(
                name="John Doe",
                email="not-an-email",
                phone="+91-9876543210"
            )
    
    def test_empty_name_fails(self):
        """Empty name should fail"""
        with pytest.raises(ValidationError):
            Buyer(
                name="",
                email="john@example.com"
            )


class TestOrder:
    """Test Order model validation"""
    
    def test_valid_order(self):
        """Valid order should pass"""
        buyer = Buyer(
            name="John Doe",
            email="john@example.com"
        )
        
        line_items = [
            LineItem(
                product_id="test-001",
                name="Test Product",
                quantity=2,
                unit_amount=100.0,
                currency="INR",
                line_total=200.0
            )
        ]
        
        order = Order(
            id="ORD_TEST_001",
            buyer=buyer,
            line_items=line_items,
            total_amount=200.0,
            currency="INR",
            status=OrderStatus.PENDING
        )
        
        assert order.id == "ORD_TEST_001"
        assert order.total_amount == 200.0
        assert order.status == OrderStatus.PENDING
    
    def test_total_amount_validation(self):
        """Total amount must match sum of line items"""
        buyer = Buyer(name="John Doe", email="john@example.com")
        
        line_items = [
            LineItem(
                product_id="test-001",
                name="Test Product",
                quantity=2,
                unit_amount=100.0,
                currency="INR",
                line_total=200.0
            )
        ]
        
        with pytest.raises(ValidationError):
            Order(
                id="ORD_TEST_001",
                buyer=buyer,
                line_items=line_items,
                total_amount=150.0,  # Wrong total
                currency="INR"
            )
    
    def test_empty_line_items_fails(self):
        """Empty line items should fail"""
        buyer = Buyer(name="John Doe", email="john@example.com")
        
        with pytest.raises(ValidationError):
            Order(
                id="ORD_TEST_001",
                buyer=buyer,
                line_items=[],  # Empty
                total_amount=0,
                currency="INR"
            )


class TestCartItem:
    """Test CartItem model validation"""
    
    def test_valid_cart_item(self):
        """Valid cart item should pass"""
        item = CartItem(
            product_id="test-001",
            quantity=2
        )
        assert item.product_id == "test-001"
        assert item.quantity == 2
    
    def test_zero_quantity_fails(self):
        """Zero quantity should fail"""
        with pytest.raises(ValidationError):
            CartItem(
                product_id="test-001",
                quantity=0
            )


class TestOrderCreateRequest:
    """Test OrderCreateRequest model validation"""
    
    def test_valid_request(self):
        """Valid request should pass"""
        buyer = Buyer(name="John Doe", email="john@example.com")
        
        request = OrderCreateRequest(
            line_items=[
                CartItem(product_id="test-001", quantity=2)
            ],
            buyer_info=buyer
        )
        
        assert len(request.line_items) == 1
        assert request.buyer_info.name == "John Doe"
    
    def test_empty_line_items_fails(self):
        """Empty line items should fail"""
        with pytest.raises(ValidationError):
            OrderCreateRequest(
                line_items=[],
                buyer_info=None
            )


class TestProductFilter:
    """Test ProductFilter model validation"""
    
    def test_valid_filter(self):
        """Valid filter should pass"""
        filter_obj = ProductFilter(
            category="mug",
            max_price=1000.0,
            search="coffee"
        )
        assert filter_obj.category == "mug"
        assert filter_obj.max_price == 1000.0
    
    def test_negative_max_price_fails(self):
        """Negative max price should fail"""
        with pytest.raises(ValidationError):
            ProductFilter(max_price=-100.0)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
