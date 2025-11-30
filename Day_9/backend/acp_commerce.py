"""
Type-Safe ACP Commerce Layer
Uses Pydantic models for validation and type safety
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from pydantic import ValidationError

from acp_models import (
    Product, LineItem, Buyer, Order, CartItem,
    OrderStatus, ProductFilter, OrderCreateRequest
)

# File paths
CATALOG_PATH = Path(__file__).parent / "catalog.json"
ORDERS_PATH = Path(__file__).parent / "orders.json"
CARTS_PATH = Path(__file__).parent / "carts.json"

# Load and validate catalog
def load_catalog() -> List[Product]:
    """Load catalog with type validation"""
    with open(CATALOG_PATH) as f:
        data = json.load(f)
    
    products = []
    for product_data in data.get("products", []):
        try:
            product = Product(**product_data)
            products.append(product)
        except ValidationError as e:
            print(f"Invalid product data: {product_data.get('id', 'unknown')}")
            print(f"Validation error: {e}")
    
    return products


# Load catalog
PRODUCTS = load_catalog()

# Load orders
def load_orders() -> dict[str, Order]:
    """Load orders with type validation"""
    if not ORDERS_PATH.exists():
        return {}
    
    with open(ORDERS_PATH) as f:
        data = json.load(f)
    
    orders = {}
    for order_id, order_data in data.items():
        try:
            # Convert datetime strings back to datetime objects
            if 'created_at' in order_data:
                order_data['created_at'] = datetime.fromisoformat(order_data['created_at'])
            if 'updated_at' in order_data:
                order_data['updated_at'] = datetime.fromisoformat(order_data['updated_at'])
            
            order = Order(**order_data)
            orders[order_id] = order
        except ValidationError as e:
            print(f"Invalid order data: {order_id}")
            print(f"Validation error: {e}")
    
    return orders


ORDERS = load_orders()


def save_orders():
    """Save orders to JSON file"""
    # Convert Order objects to dicts with ISO format dates
    orders_dict = {}
    for order_id, order in ORDERS.items():
        order_dict = order.model_dump()
        order_dict['created_at'] = order.created_at.isoformat()
        order_dict['updated_at'] = order.updated_at.isoformat()
        orders_dict[order_id] = order_dict
    
    with open(ORDERS_PATH, 'w') as f:
        json.dump(orders_dict, f, indent=2)


def list_products(filters: Optional[ProductFilter] = None) -> List[Product]:
    """
    Get products from catalog with optional filtering
    
    Args:
        filters: Optional ProductFilter model
    
    Returns:
        List of Product models
    """
    if not filters:
        return PRODUCTS.copy()
    
    filtered_products = []
    
    for product in PRODUCTS:
        include = True
        
        # Filter by category
        if filters.category:
            if product.category.lower() != filters.category.lower():
                include = False
        
        # Filter by price range
        if filters.max_price is not None:
            if product.price > filters.max_price:
                include = False
        
        if filters.min_price is not None:
            if product.price < filters.min_price:
                include = False
        
        # Filter by color
        if filters.color:
            if not product.color or product.color.lower() != filters.color.lower():
                include = False
        
        # Filter by size
        if filters.size:
            if not product.size or product.size.upper() != filters.size.upper():
                include = False
        
        # Filter by stock
        if filters.in_stock is not None:
            if filters.in_stock and product.stock <= 0:
                include = False
        
        # Search in name/description
        if filters.search:
            search_term = filters.search.lower()
            if (search_term not in product.name.lower() and 
                search_term not in product.description.lower()):
                include = False
        
        if include:
            filtered_products.append(product)
    
    return filtered_products


def get_product_by_id(product_id: str) -> Optional[Product]:
    """Get a single product by ID"""
    for product in PRODUCTS:
        if product.id == product_id:
            return product
    return None


def create_order(request: OrderCreateRequest) -> Order:
    """
    Create a new order with comprehensive validation
    
    Args:
        request: OrderCreateRequest with line_items and buyer_info
    
    Returns:
        Order model
    
    Raises:
        ValueError: For invalid inputs
        ValidationError: For Pydantic validation errors
    """
    # Validation 1: Cart not empty (handled by Pydantic min_length=1)
    
    # Validation 2: Check all products exist and build line items
    line_items = []
    total_amount = 0.0
    
    for cart_item in request.line_items:
        product = get_product_by_id(cart_item.product_id)
        if not product:
            raise ValueError(f"Product '{cart_item.product_id}' not found")
        
        # Check stock
        if product.stock < cart_item.quantity:
            raise ValueError(
                f"Insufficient stock for '{product.name}'. "
                f"Available: {product.stock}, Requested: {cart_item.quantity}"
            )
        
        # Create line item
        line_total = product.price * cart_item.quantity
        line_item = LineItem(
            product_id=product.id,
            name=product.name,
            quantity=cart_item.quantity,
            unit_amount=product.price,
            currency=product.currency,
            line_total=line_total
        )
        
        line_items.append(line_item)
        total_amount += line_total
    
    # Prepare buyer info
    if request.buyer_info:
        buyer = request.buyer_info
    else:
        # Default guest buyer
        buyer = Buyer(
            name="Guest Customer",
            email="guest@example.com",
            phone="N/A",
            address="N/A"
        )
    
    # Generate order ID
    order_id = f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    # Create order (Pydantic will validate)
    order = Order(
        id=order_id,
        buyer=buyer,
        line_items=line_items,
        total_amount=total_amount,
        currency="INR",
        status=OrderStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )
    
    # Store order
    ORDERS[order_id] = order
    save_orders()
    
    return order


def get_order(order_id: str) -> Optional[Order]:
    """Get order by ID"""
    return ORDERS.get(order_id)


def get_recent_orders(limit: int = 5) -> List[Order]:
    """Get recent orders, most recent first"""
    orders_list = list(ORDERS.values())
    orders_list.sort(key=lambda x: x.created_at, reverse=True)
    return orders_list[:limit]


def update_order_status(order_id: str, status: OrderStatus) -> bool:
    """Update order status"""
    if order_id in ORDERS:
        ORDERS[order_id].status = status
        ORDERS[order_id].updated_at = datetime.now()
        save_orders()
        return True
    return False


def get_categories() -> List[str]:
    """Get all unique product categories"""
    categories = set()
    for product in PRODUCTS:
        categories.add(product.category)
    return sorted(list(categories))


def search_products(query: str) -> List[Product]:
    """Search products by name or description"""
    filter_obj = ProductFilter(search=query)
    return list_products(filter_obj)


def get_orders_by_user(email: str) -> List[Order]:
    """Get all orders for a specific user by email"""
    user_orders = []
    for order in ORDERS.values():
        if order.buyer.email.lower() == email.lower():
            user_orders.append(order)
    user_orders.sort(key=lambda x: x.created_at, reverse=True)
    return user_orders


def get_orders_by_status(status: OrderStatus) -> List[Order]:
    """Get all orders with a specific status"""
    filtered_orders = [order for order in ORDERS.values() if order.status == status]
    filtered_orders.sort(key=lambda x: x.created_at, reverse=True)
    return filtered_orders


def calculate_user_spending(email: str) -> float:
    """Calculate total spending for a user"""
    user_orders = get_orders_by_user(email)
    total = sum(order.total_amount for order in user_orders)
    return total


def get_spending_by_category(email: str) -> dict[str, float]:
    """Get spending breakdown by category for a user"""
    user_orders = get_orders_by_user(email)
    category_spending = {}
    
    for order in user_orders:
        for item in order.line_items:
            product = get_product_by_id(item.product_id)
            if product:
                category = product.category
                if category not in category_spending:
                    category_spending[category] = 0.0
                category_spending[category] += item.line_total
    
    return category_spending


def get_cart(email: str) -> List[CartItem]:
    """Get saved cart for a user"""
    if not CARTS_PATH.exists():
        return []
    
    try:
        with open(CARTS_PATH) as f:
            carts = json.load(f)
        
        cart_data = carts.get(email, [])
        cart_items = []
        
        for item_data in cart_data:
            try:
                cart_item = CartItem(**item_data)
                cart_items.append(cart_item)
            except ValidationError:
                continue
        
        return cart_items
    except:
        return []


def save_cart(email: str, cart: List[CartItem]) -> None:
    """Save cart for a user"""
    try:
        if CARTS_PATH.exists():
            with open(CARTS_PATH) as f:
                carts = json.load(f)
        else:
            carts = {}
        
        # Convert CartItem objects to dicts
        cart_data = [item.model_dump() for item in cart]
        carts[email] = cart_data
        
        with open(CARTS_PATH, 'w') as f:
            json.dump(carts, f, indent=2)
    except Exception as e:
        print(f"Error saving cart: {e}")


def clear_cart(email: str) -> None:
    """Clear saved cart for a user"""
    save_cart(email, [])
