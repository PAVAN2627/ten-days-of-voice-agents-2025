"""
Tests for Type-Safe ACP Commerce Layer
Integration tests for commerce operations
"""

import pytest
from pydantic import ValidationError

from acp_models import (
    Product, Buyer, CartItem, OrderCreateRequest, ProductFilter, OrderStatus
)
from acp_commerce import (
    list_products, get_product_by_id, create_order,
    get_order, search_products, get_categories
)


class TestProductCatalog:
    """Test product catalog operations"""
    
    def test_list_all_products(self):
        """Should list all products"""
        products = list_products()
        assert len(products) > 0
        assert all(isinstance(p, Product) for p in products)
    
    def test_filter_by_category(self):
        """Should filter products by category"""
        filter_obj = ProductFilter(category="mug")
        products = list_products(filter_obj)
        assert all(p.category.lower() == "mug" for p in products)
    
    def test_filter_by_max_price(self):
        """Should filter products by max price"""
        filter_obj = ProductFilter(max_price=1000.0)
        products = list_products(filter_obj)
        assert all(p.price <= 1000.0 for p in products)
    
    def test_search_products(self):
        """Should search products by name"""
        products = search_products("mug")
        assert len(products) > 0
        assert all("mug" in p.name.lower() or "mug" in p.description.lower() 
                  for p in products)
    
    def test_get_product_by_id(self):
        """Should get product by ID"""
        products = list_products()
        if products:
            product_id = products[0].id
            product = get_product_by_id(product_id)
            assert product is not None
            assert product.id == product_id
    
    def test_get_nonexistent_product(self):
        """Should return None for nonexistent product"""
        product = get_product_by_id("nonexistent-id")
        assert product is None
    
    def test_get_categories(self):
        """Should get all categories"""
        categories = get_categories()
        assert len(categories) > 0
        assert all(isinstance(c, str) for c in categories)


class TestOrderCreation:
    """Test order creation with validation"""
    
    def test_create_valid_order(self):
        """Should create order with valid data"""
        # Get a real product
        products = list_products()
        assert len(products) > 0
        
        product = products[0]
        
        buyer = Buyer(
            name="Test User",
            email="test@example.com",
            phone="+91-1234567890",
            address="Test Address"
        )
        
        request = OrderCreateRequest(
            line_items=[
                CartItem(product_id=product.id, quantity=2)
            ],
            buyer_info=buyer
        )
        
        order = create_order(request)
        
        assert order.id.startswith("ORD_")
        assert order.buyer.email == "test@example.com"
        assert len(order.line_items) == 1
        assert order.line_items[0].quantity == 2
        assert order.total_amount == product.price * 2
        assert order.status == OrderStatus.PENDING
    
    def test_create_order_without_buyer(self):
        """Should create order with default guest buyer"""
        products = list_products()
        assert len(products) > 0
        
        product = products[0]
        
        request = OrderCreateRequest(
            line_items=[
                CartItem(product_id=product.id, quantity=1)
            ],
            buyer_info=None
        )
        
        order = create_order(request)
        
        assert order.buyer.name == "Guest Customer"
        assert order.buyer.email == "guest@example.com"
    
    def test_create_order_invalid_product(self):
        """Should fail with invalid product ID"""
        buyer = Buyer(
            name="Test User",
            email="test@example.com"
        )
        
        request = OrderCreateRequest(
            line_items=[
                CartItem(product_id="invalid-product-id", quantity=1)
            ],
            buyer_info=buyer
        )
        
        with pytest.raises(ValueError, match="not found"):
            create_order(request)
    
    def test_create_order_empty_cart(self):
        """Should fail with empty cart"""
        buyer = Buyer(
            name="Test User",
            email="test@example.com"
        )
        
        with pytest.raises(ValidationError):
            OrderCreateRequest(
                line_items=[],  # Empty cart
                buyer_info=buyer
            )
    
    def test_create_order_zero_quantity(self):
        """Should fail with zero quantity"""
        products = list_products()
        product = products[0]
        
        buyer = Buyer(
            name="Test User",
            email="test@example.com"
        )
        
        with pytest.raises(ValidationError):
            OrderCreateRequest(
                line_items=[
                    CartItem(product_id=product.id, quantity=0)
                ],
                buyer_info=buyer
            )
    
    def test_create_order_multiple_items(self):
        """Should create order with multiple items"""
        products = list_products()
        assert len(products) >= 2
        
        buyer = Buyer(
            name="Test User",
            email="test@example.com"
        )
        
        request = OrderCreateRequest(
            line_items=[
                CartItem(product_id=products[0].id, quantity=2),
                CartItem(product_id=products[1].id, quantity=1)
            ],
            buyer_info=buyer
        )
        
        order = create_order(request)
        
        assert len(order.line_items) == 2
        expected_total = (products[0].price * 2) + (products[1].price * 1)
        assert abs(order.total_amount - expected_total) < 0.01


class TestOrderRetrieval:
    """Test order retrieval operations"""
    
    def test_get_order_by_id(self):
        """Should retrieve order by ID"""
        # Create an order first
        products = list_products()
        product = products[0]
        
        buyer = Buyer(name="Test User", email="test@example.com")
        request = OrderCreateRequest(
            line_items=[CartItem(product_id=product.id, quantity=1)],
            buyer_info=buyer
        )
        
        created_order = create_order(request)
        
        # Retrieve it
        retrieved_order = get_order(created_order.id)
        
        assert retrieved_order is not None
        assert retrieved_order.id == created_order.id
        assert retrieved_order.total_amount == created_order.total_amount
    
    def test_get_nonexistent_order(self):
        """Should return None for nonexistent order"""
        order = get_order("nonexistent-order-id")
        assert order is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
