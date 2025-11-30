"""
ACP-Inspired Commerce Layer
Handles product catalog and order management
"""

import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# File paths
CATALOG_PATH = Path(__file__).parent / "catalog.json"
ORDERS_PATH = Path(__file__).parent / "orders.json"

# Load catalog
with open(CATALOG_PATH) as f:
    CATALOG_DATA = json.load(f)

PRODUCTS = CATALOG_DATA["products"]

# In-memory orders storage (will be persisted to JSON)
ORDERS = {}

# Load existing orders if file exists
if ORDERS_PATH.exists():
    with open(ORDERS_PATH) as f:
        ORDERS = json.load(f)


def save_orders():
    """Save orders to JSON file"""
    with open(ORDERS_PATH, 'w') as f:
        json.dump(ORDERS, f, indent=2)


def list_products(filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Get products from catalog with optional filtering
    
    Args:
        filters: Optional dict with keys like 'category', 'max_price', 'color', etc.
    
    Returns:
        List of product dictionaries
    """
    products = PRODUCTS.copy()
    
    if not filters:
        return products
    
    filtered_products = []
    
    for product in products:
        include = True
        
        # Filter by category
        if 'category' in filters:
            if product.get('category', '').lower() != filters['category'].lower():
                include = False
        
        # Filter by max price
        if 'max_price' in filters:
            if product.get('price', 0) > filters['max_price']:
                include = False
        
        # Filter by color
        if 'color' in filters:
            if product.get('color', '').lower() != filters['color'].lower():
                include = False
        
        # Filter by size
        if 'size' in filters:
            if product.get('size', '').upper() != filters['size'].upper():
                include = False
        
        # Search in name/description
        if 'search' in filters:
            search_term = filters['search'].lower()
            if (search_term not in product.get('name', '').lower() and 
                search_term not in product.get('description', '').lower()):
                include = False
        
        if include:
            filtered_products.append(product)
    
    return filtered_products


def get_product_by_id(product_id: str) -> Optional[Dict[str, Any]]:
    """Get a single product by ID"""
    for product in PRODUCTS:
        if product['id'] == product_id:
            return product
    return None


def create_order(line_items: List[Dict[str, Any]], buyer_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Create a new order with comprehensive validation
    
    Args:
        line_items: List of dicts with 'product_id' and 'quantity'
        buyer_info: Optional dict with buyer details {name, email, phone, address}
    
    Returns:
        Order dictionary with ACP-inspired structure
    
    Raises:
        ValueError: For invalid inputs
    """
    # Validation 1: Cart not empty
    if not line_items:
        raise ValueError("Cart cannot be empty. Add items before placing an order.")
    
    # Validation 2: Check all items before processing
    for i, item in enumerate(line_items):
        # Check product_id exists
        if 'product_id' not in item:
            raise ValueError(f"Item {i+1}: missing 'product_id'")
        
        # Check quantity exists and is valid
        if 'quantity' not in item:
            raise ValueError(f"Item {i+1}: missing 'quantity'")
        
        quantity = item.get('quantity', 1)
        
        # Validate quantity
        if not isinstance(quantity, int):
            raise ValueError(f"Item {i+1}: quantity must be an integer, got {type(quantity).__name__}")
        
        if quantity <= 0:
            raise ValueError(f"Item {i+1}: quantity must be > 0, got {quantity}")
        
        # Check product exists
        product_id = item['product_id']
        product = get_product_by_id(product_id)
        if not product:
            raise ValueError(f"Item {i+1}: product '{product_id}' not found")
    
    # All validation passed, create order
    order_id = f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{str(uuid.uuid4())[:8]}"
    
    # Process line items
    processed_items = []
    total_amount = 0
    
    for item in line_items:
        product = get_product_by_id(item['product_id'])
        quantity = item.get('quantity', 1)
        unit_amount = product['price']
        line_total = unit_amount * quantity
        
        line_item = {
            "product_id": product['id'],
            "name": product['name'],
            "quantity": quantity,
            "unit_amount": unit_amount,
            "currency": product['currency'],
            "line_total": line_total
        }
        
        # Include size if provided
        if 'size' in item and item['size']:
            line_item['size'] = item['size']
        
        processed_items.append(line_item)
        
        total_amount += line_total
    
    # Prepare buyer info (with defaults for demo)
    buyer = {
        "name": buyer_info.get('name', 'Guest Customer') if buyer_info else 'Guest Customer',
        "email": buyer_info.get('email', 'guest@example.com') if buyer_info else 'guest@example.com',
        "phone": buyer_info.get('phone', 'N/A') if buyer_info else 'N/A',
        "address": buyer_info.get('address', 'N/A') if buyer_info else 'N/A'
    }
    
    # Create order object (ACP-inspired structure)
    order = {
        "id": order_id,
        "buyer": buyer,
        "line_items": processed_items,
        "total_amount": total_amount,
        "currency": "INR",
        "status": "PENDING",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    # Store order
    ORDERS[order_id] = order
    save_orders()
    
    return order


def get_order(order_id: str) -> Optional[Dict[str, Any]]:
    """Get order by ID"""
    return ORDERS.get(order_id)


def get_recent_orders(limit: int = 5) -> List[Dict[str, Any]]:
    """Get recent orders, most recent first"""
    orders_list = list(ORDERS.values())
    # Sort by created_at descending
    orders_list.sort(key=lambda x: x['created_at'], reverse=True)
    return orders_list[:limit]


def update_order_status(order_id: str, status: str) -> bool:
    """Update order status"""
    if order_id in ORDERS:
        ORDERS[order_id]['status'] = status
        ORDERS[order_id]['updated_at'] = datetime.now().isoformat()
        save_orders()
        return True
    return False


def get_categories() -> List[str]:
    """Get all unique product categories"""
    categories = set()
    for product in PRODUCTS:
        if 'category' in product:
            categories.add(product['category'])
    return sorted(list(categories))


def search_products(query: str) -> List[Dict[str, Any]]:
    """Search products by name or description"""
    return list_products({'search': query})


def get_orders_by_user(email: str) -> List[Dict[str, Any]]:
    """Get all orders for a specific user by email"""
    user_orders = []
    for order in ORDERS.values():
        if order.get('buyer', {}).get('email', '').lower() == email.lower():
            user_orders.append(order)
    # Sort by created_at descending
    user_orders.sort(key=lambda x: x['created_at'], reverse=True)
    return user_orders


def get_orders_by_date_range(start_date: str, end_date: str) -> List[Dict[str, Any]]:
    """Get orders within a date range (format: YYYY-MM-DD)"""
    filtered_orders = []
    try:
        from datetime import datetime as dt
        start = dt.strptime(start_date, '%Y-%m-%d')
        end = dt.strptime(end_date, '%Y-%m-%d')
        
        for order in ORDERS.values():
            order_date = dt.fromisoformat(order['created_at'].split('T')[0])
            if start <= order_date <= end:
                filtered_orders.append(order)
        
        filtered_orders.sort(key=lambda x: x['created_at'], reverse=True)
    except Exception as e:
        print(f"Date filtering error: {e}")
    
    return filtered_orders


def get_orders_by_status(status: str) -> List[Dict[str, Any]]:
    """Get all orders with a specific status"""
    filtered_orders = [order for order in ORDERS.values() if order.get('status', '').upper() == status.upper()]
    filtered_orders.sort(key=lambda x: x['created_at'], reverse=True)
    return filtered_orders


def calculate_user_spending(email: str) -> float:
    """Calculate total spending for a user"""
    user_orders = get_orders_by_user(email)
    total = sum(order['total_amount'] for order in user_orders)
    return total


def get_spending_by_category(email: str) -> Dict[str, float]:
    """Get spending breakdown by category for a user"""
    user_orders = get_orders_by_user(email)
    category_spending = {}
    
    for order in user_orders:
        for item in order.get('line_items', []):
            product = get_product_by_id(item['product_id'])
            if product:
                category = product.get('category', 'Other')
                if category not in category_spending:
                    category_spending[category] = 0
                category_spending[category] += item['line_total']
    
    return category_spending


def update_order_status(order_id: str, new_status: str) -> bool:
    """Update order status with validation"""
    valid_statuses = ['PENDING', 'CONFIRMED', 'SHIPPED', 'DELIVERED', 'CANCELLED']
    
    if new_status.upper() not in valid_statuses:
        return False
    
    if order_id in ORDERS:
        ORDERS[order_id]['status'] = new_status.upper()
        ORDERS[order_id]['updated_at'] = datetime.now().isoformat()
        save_orders()
        return True
    return False


def get_cart(email: str) -> List[Dict[str, Any]]:
    """Get saved cart for a user"""
    cart_file = Path(__file__).parent / "carts.json"
    
    if not cart_file.exists():
        return []
    
    try:
        with open(cart_file) as f:
            carts = json.load(f)
        return carts.get(email, [])
    except:
        return []


def save_cart(email: str, cart: List[Dict[str, Any]]) -> None:
    """Save cart for a user"""
    cart_file = Path(__file__).parent / "carts.json"
    
    try:
        if cart_file.exists():
            with open(cart_file) as f:
                carts = json.load(f)
        else:
            carts = {}
        
        carts[email] = cart
        
        with open(cart_file, 'w') as f:
            json.dump(carts, f, indent=2)
    except Exception as e:
        print(f"Error saving cart: {e}")


def clear_cart(email: str) -> None:
    """Clear saved cart for a user"""
    save_cart(email, [])


# Example usage and testing
if __name__ == "__main__":
    # Test catalog browsing
    print("All products:")
    products = list_products()
    for p in products[:3]:
        print(f"- {p['name']} (₹{p['price']})")
    
    print(f"\nTotal products: {len(products)}")
    
    # Test filtering
    print("\nMugs only:")
    mugs = list_products({'category': 'mug'})
    for mug in mugs:
        print(f"- {mug['name']} (₹{mug['price']})")
    
    # Test order creation
    print("\nCreating test order...")
    test_order = create_order([
        {'product_id': 'mug-001', 'quantity': 2},
        {'product_id': 'tshirt-001', 'quantity': 1}
    ])
    print(f"Order created: {test_order['id']}")
    print(f"Total: ₹{test_order['total_amount']}")
    
    # Test order retrieval
    retrieved = get_order(test_order['id'])
    print(f"Retrieved order total: ₹{retrieved['total_amount']}")