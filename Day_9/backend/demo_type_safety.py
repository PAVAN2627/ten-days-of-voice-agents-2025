"""
Demo: Type-Safe ACP vs Non-Type-Safe Implementation
Shows the benefits of using Pydantic models
"""

from pydantic import ValidationError
from acp_models import (
    Product, LineItem, Buyer, Order, CartItem,
    OrderCreateRequest, OrderStatus
)
from acp_commerce import create_order, list_products, get_product_by_id
from acp_models import ProductFilter


def demo_product_validation():
    """Demo: Product validation catches errors early"""
    print("=" * 60)
    print("DEMO 1: Product Validation")
    print("=" * 60)
    
    # ✅ Valid product
    print("\n✅ Creating valid product...")
    try:
        product = Product(
            id="demo-001",
            name="Demo Product",
            price=100.0,
            currency="INR",
            category="demo",
            description="A demo product"
        )
        print(f"Success! Created: {product.name} at ₹{product.price}")
    except ValidationError as e:
        print(f"Failed: {e}")
    
    # ❌ Invalid product - negative price
    print("\n❌ Trying to create product with negative price...")
    try:
        product = Product(
            id="demo-002",
            name="Invalid Product",
            price=-100.0,  # Invalid!
            currency="INR",
            category="demo"
        )
        print(f"Created: {product.name}")
    except ValidationError as e:
        print(f"Caught error: Price must be positive!")
        print(f"Details: {e.errors()[0]['msg']}")
    
    # ❌ Invalid product - zero price
    print("\n❌ Trying to create product with zero price...")
    try:
        product = Product(
            id="demo-003",
            name="Free Product",
            price=0,  # Invalid!
            currency="INR",
            category="demo"
        )
        print(f"Created: {product.name}")
    except ValidationError as e:
        print(f"Caught error: Price must be greater than 0!")


def demo_line_item_validation():
    """Demo: LineItem validation ensures correct calculations"""
    print("\n" + "=" * 60)
    print("DEMO 2: LineItem Calculation Validation")
    print("=" * 60)
    
    # ✅ Valid line item
    print("\n✅ Creating valid line item...")
    try:
        item = LineItem(
            product_id="demo-001",
            name="Demo Product",
            quantity=2,
            unit_amount=100.0,
            currency="INR",
            line_total=200.0  # Correct: 2 * 100
        )
        print(f"Success! {item.quantity}x {item.name} = ₹{item.line_total}")
    except ValidationError as e:
        print(f"Failed: {e}")
    
    # ❌ Invalid line item - wrong calculation
    print("\n❌ Trying to create line item with wrong total...")
    try:
        item = LineItem(
            product_id="demo-001",
            name="Demo Product",
            quantity=2,
            unit_amount=100.0,
            currency="INR",
            line_total=150.0  # Wrong! Should be 200
        )
        print(f"Created: {item.line_total}")
    except ValidationError as e:
        print(f"Caught error: Line total doesn't match quantity × unit_amount!")
        print(f"Expected: 2 × ₹100 = ₹200, Got: ₹150")


def demo_buyer_validation():
    """Demo: Buyer validation ensures valid email"""
    print("\n" + "=" * 60)
    print("DEMO 3: Buyer Email Validation")
    print("=" * 60)
    
    # ✅ Valid buyer
    print("\n✅ Creating valid buyer...")
    try:
        buyer = Buyer(
            name="John Doe",
            email="john@example.com",
            phone="+91-9876543210"
        )
        print(f"Success! Created buyer: {buyer.name} ({buyer.email})")
    except ValidationError as e:
        print(f"Failed: {e}")
    
    # ❌ Invalid buyer - bad email
    print("\n❌ Trying to create buyer with invalid email...")
    try:
        buyer = Buyer(
            name="Jane Doe",
            email="not-an-email",  # Invalid!
            phone="+91-9876543210"
        )
        print(f"Created: {buyer.name}")
    except ValidationError as e:
        print(f"Caught error: Invalid email format!")
        print(f"Details: {e.errors()[0]['msg']}")


def demo_order_validation():
    """Demo: Order validation ensures correct totals"""
    print("\n" + "=" * 60)
    print("DEMO 4: Order Total Validation")
    print("=" * 60)
    
    buyer = Buyer(
        name="Test User",
        email="test@example.com"
    )
    
    line_items = [
        LineItem(
            product_id="demo-001",
            name="Product 1",
            quantity=2,
            unit_amount=100.0,
            currency="INR",
            line_total=200.0
        ),
        LineItem(
            product_id="demo-002",
            name="Product 2",
            quantity=1,
            unit_amount=150.0,
            currency="INR",
            line_total=150.0
        )
    ]
    
    # ✅ Valid order
    print("\n✅ Creating valid order...")
    try:
        order = Order(
            id="ORD_DEMO_001",
            buyer=buyer,
            line_items=line_items,
            total_amount=350.0,  # Correct: 200 + 150
            currency="INR",
            status=OrderStatus.PENDING
        )
        print(f"Success! Order {order.id} total: ₹{order.total_amount}")
    except ValidationError as e:
        print(f"Failed: {e}")
    
    # ❌ Invalid order - wrong total
    print("\n❌ Trying to create order with wrong total...")
    try:
        order = Order(
            id="ORD_DEMO_002",
            buyer=buyer,
            line_items=line_items,
            total_amount=300.0,  # Wrong! Should be 350
            currency="INR",
            status=OrderStatus.PENDING
        )
        print(f"Created order: ₹{order.total_amount}")
    except ValidationError as e:
        print(f"Caught error: Total doesn't match sum of line items!")
        print(f"Expected: ₹200 + ₹150 = ₹350, Got: ₹300")


def demo_order_creation():
    """Demo: Real order creation with validation"""
    print("\n" + "=" * 60)
    print("DEMO 5: Real Order Creation")
    print("=" * 60)
    
    # Get real products
    products = list_products()
    if len(products) < 2:
        print("Not enough products in catalog")
        return
    
    product1 = products[0]
    product2 = products[1]
    
    print(f"\nProducts available:")
    print(f"  1. {product1.name} - ₹{product1.price}")
    print(f"  2. {product2.name} - ₹{product2.price}")
    
    # ✅ Valid order creation
    print("\n✅ Creating order with 2 items...")
    try:
        buyer = Buyer(
            name="Demo User",
            email="demo@example.com",
            phone="+91-1234567890",
            address="123 Demo Street"
        )
        
        request = OrderCreateRequest(
            line_items=[
                CartItem(product_id=product1.id, quantity=2),
                CartItem(product_id=product2.id, quantity=1)
            ],
            buyer_info=buyer
        )
        
        order = create_order(request)
        
        print(f"Success! Order created: {order.id}")
        print(f"  Buyer: {order.buyer.name}")
        print(f"  Items: {len(order.line_items)}")
        print(f"  Total: ₹{order.total_amount}")
        print(f"  Status: {order.status.value}")
        
    except ValidationError as e:
        print(f"Validation failed: {e}")
    except ValueError as e:
        print(f"Business logic error: {e}")
    
    # ❌ Invalid order - nonexistent product
    print("\n❌ Trying to create order with invalid product...")
    try:
        request = OrderCreateRequest(
            line_items=[
                CartItem(product_id="nonexistent-product", quantity=1)
            ],
            buyer_info=buyer
        )
        
        order = create_order(request)
        print(f"Created order: {order.id}")
        
    except ValueError as e:
        print(f"Caught error: {e}")
    
    # ❌ Invalid order - zero quantity
    print("\n❌ Trying to create order with zero quantity...")
    try:
        request = OrderCreateRequest(
            line_items=[
                CartItem(product_id=product1.id, quantity=0)  # Invalid!
            ],
            buyer_info=buyer
        )
        
        order = create_order(request)
        print(f"Created order: {order.id}")
        
    except ValidationError as e:
        print(f"Caught error: Quantity must be greater than 0!")


def demo_product_filtering():
    """Demo: Type-safe product filtering"""
    print("\n" + "=" * 60)
    print("DEMO 6: Type-Safe Product Filtering")
    print("=" * 60)
    
    # Get all products
    all_products = list_products()
    print(f"\nTotal products: {len(all_products)}")
    
    # Filter by category
    print("\n✅ Filtering by category='mug'...")
    filters = ProductFilter(category="mug")
    mugs = list_products(filters)
    print(f"Found {len(mugs)} mugs:")
    for mug in mugs[:3]:
        print(f"  - {mug.name} (₹{mug.price})")
    
    # Filter by price
    print("\n✅ Filtering by max_price=1000...")
    filters = ProductFilter(max_price=1000.0)
    affordable = list_products(filters)
    print(f"Found {len(affordable)} products under ₹1000:")
    for product in affordable[:3]:
        print(f"  - {product.name} (₹{product.price})")
    
    # Search
    print("\n✅ Searching for 'coffee'...")
    filters = ProductFilter(search="coffee")
    results = list_products(filters)
    print(f"Found {len(results)} products matching 'coffee':")
    for product in results[:3]:
        print(f"  - {product.name} (₹{product.price})")


def demo_enum_safety():
    """Demo: Enum type safety for order status"""
    print("\n" + "=" * 60)
    print("DEMO 7: Order Status Enum Safety")
    print("=" * 60)
    
    print("\n✅ Valid order statuses:")
    for status in OrderStatus:
        print(f"  - {status.value}")
    
    print("\n✅ Using enum in code:")
    status = OrderStatus.PENDING
    print(f"  Status: {status.value}")
    
    print("\n❌ Trying to use invalid status...")
    try:
        status = OrderStatus("INVALID_STATUS")
        print(f"  Status: {status}")
    except ValueError as e:
        print(f"  Caught error: 'INVALID_STATUS' is not a valid OrderStatus")


def main():
    """Run all demos"""
    print("\n" + "=" * 60)
    print("TYPE-SAFE ACP IMPLEMENTATION DEMO")
    print("=" * 60)
    print("\nThis demo shows how Pydantic models catch errors early")
    print("and ensure data integrity throughout the system.")
    
    demo_product_validation()
    demo_line_item_validation()
    demo_buyer_validation()
    demo_order_validation()
    demo_order_creation()
    demo_product_filtering()
    demo_enum_safety()
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETE")
    print("=" * 60)
    print("\nKey Benefits:")
    print("  ✅ Errors caught at model creation, not runtime")
    print("  ✅ Automatic validation of calculations")
    print("  ✅ Type safety with IDE autocomplete")
    print("  ✅ Self-documenting code")
    print("  ✅ Better error messages")
    print("\nTry running the tests: pytest test_acp_*.py -v")


if __name__ == "__main__":
    main()
