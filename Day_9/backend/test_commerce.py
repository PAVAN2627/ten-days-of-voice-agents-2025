#!/usr/bin/env python3
"""
Test script for Day 9 E-commerce Agent commerce functions
"""

import sys
from pathlib import Path

# Add current directory to path
sys.path.append(str(Path(__file__).parent))

from commerce import (
    list_products,
    create_order,
    get_order,
    get_recent_orders,
    get_categories,
    search_products,
    get_product_by_id
)

def test_catalog_browsing():
    """Test product catalog browsing"""
    print("=== Testing Catalog Browsing ===")
    
    # Get all products
    all_products = list_products()
    print(f"Total products: {len(all_products)}")
    
    # Show first 3 products
    print("\nFirst 3 products:")
    for i, product in enumerate(all_products[:3], 1):
        print(f"{i}. {product['name']} - Rs.{product['price']} ({product['category']})")
    
    # Test category filtering
    print("\n--- Category Filtering ---")
    mugs = list_products({'category': 'mug'})
    print(f"Mugs found: {len(mugs)}")
    for mug in mugs:
        print(f"- {mug['name']} - Rs.{mug['price']}")
    
    clothing = list_products({'category': 'clothing'})
    print(f"\nClothing items: {len(clothing)}")
    for item in clothing:
        print(f"- {item['name']} - Rs.{item['price']} ({item.get('color', 'N/A')})")
    
    # Test price filtering
    print("\n--- Price Filtering ---")
    affordable = list_products({'max_price': 1000})
    print(f"Items under Rs.1000: {len(affordable)}")
    for item in affordable:
        print(f"- {item['name']} - Rs.{item['price']}")
    
    # Test search
    print("\n--- Search Testing ---")
    search_results = search_products("coffee")
    print(f"Search 'coffee': {len(search_results)} results")
    for item in search_results:
        print(f"- {item['name']} - Rs.{item['price']}")
    
    # Test categories
    print("\n--- Available Categories ---")
    categories = get_categories()
    print(f"Categories: {', '.join(categories)}")


def test_order_creation():
    """Test order creation and management"""
    print("\n=== Testing Order Creation ===")
    
    # Create a test order
    line_items = [
        {'product_id': 'mug-001', 'quantity': 2},
        {'product_id': 'tshirt-001', 'quantity': 1},
        {'product_id': 'book-001', 'quantity': 1}
    ]
    
    print("Creating order with:")
    for item in line_items:
        product = get_product_by_id(item['product_id'])
        if product:
            print(f"- {product['name']} x{item['quantity']} = Rs.{product['price'] * item['quantity']}")
    
    order = create_order(line_items)
    print(f"\nOrder created: {order['id']}")
    print(f"Total: Rs.{order['total_amount']}")
    print(f"Status: {order['status']}")
    print(f"Items in order: {len(order['line_items'])}")
    
    # Test order retrieval
    print("\n--- Order Retrieval ---")
    retrieved_order = get_order(order['id'])
    if retrieved_order:
        print(f"Retrieved order: {retrieved_order['id']}")
        print(f"Total: Rs.{retrieved_order['total_amount']}")
        print("Line items:")
        for item in retrieved_order['line_items']:
            print(f"  - {item['name']} x{item['quantity']} = Rs.{item['line_total']}")
    
    # Test recent orders
    print("\n--- Recent Orders ---")
    recent = get_recent_orders(3)
    print(f"Recent orders: {len(recent)}")
    for order in recent:
        print(f"- {order['id']} (Rs.{order['total_amount']}) - {order['status']}")
    
    return order['id']


def test_voice_scenarios():
    """Test scenarios that would happen in voice interactions"""
    print("\n=== Testing Voice Scenarios ===")
    
    # Scenario 1: "Show me all coffee mugs"
    print("Scenario 1: 'Show me all coffee mugs'")
    mugs = list_products({'category': 'mug'})
    print(f"Found {len(mugs)} mugs:")
    for i, mug in enumerate(mugs, 1):
        print(f"{i}. {mug['name']} - Rs.{mug['price']}")
    
    # Scenario 2: "Do you have any t-shirts under 1500?"
    print("\nScenario 2: 'Do you have any t-shirts under Rs.1500?'")
    affordable_tshirts = list_products({'category': 'clothing', 'max_price': 1500})
    tshirts = [item for item in affordable_tshirts if 'shirt' in item['name'].lower()]
    print(f"Found {len(tshirts)} t-shirts under Rs.1500:")
    for shirt in tshirts:
        print(f"- {shirt['name']} - Rs.{shirt['price']}")
    
    # Scenario 3: "I'm looking for a black hoodie"
    print("\nScenario 3: 'I'm looking for a black hoodie'")
    black_hoodies = list_products({'category': 'clothing', 'color': 'black'})
    hoodies = [item for item in black_hoodies if 'hoodie' in item['name'].lower()]
    print(f"Found {len(hoodies)} black hoodies:")
    for hoodie in hoodies:
        print(f"- {hoodie['name']} - Rs.{hoodie['price']}")
    
    # Scenario 4: Order the second hoodie
    print("\nScenario 4: 'I'll buy the second hoodie you mentioned, in size M'")
    if len(hoodies) > 1:
        selected_hoodie = hoodies[1]  # Second hoodie (index 1)
        print(f"Selected: {selected_hoodie['name']} - Rs.{selected_hoodie['price']}")
        
        # Create order
        order = create_order([{'product_id': selected_hoodie['id'], 'quantity': 1}])
        print(f"Order placed: {order['id']} for Rs.{order['total_amount']}")
        
        return order['id']
    else:
        print("Not enough hoodies to select second one")
        return None


def main():
    """Run all tests"""
    print("Day 9 E-commerce Agent - Commerce Functions Test")
    print("=" * 60)
    
    try:
        # Test catalog browsing
        test_catalog_browsing()
        
        # Test order creation
        order_id = test_order_creation()
        
        # Test voice scenarios
        voice_order_id = test_voice_scenarios()
        
        print("\n" + "=" * 60)
        print("All tests completed successfully!")
        print(f"Orders created: {order_id}")
        if voice_order_id:
            print(f"Voice scenario order: {voice_order_id}")
        
    except Exception as e:
        print(f"\nTest failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()