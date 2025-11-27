"""
Test script for DailyMart pricing features
"""

class MockAgent:
    def __init__(self):
        self.cart = []
        self.DELIVERY_CHARGE = 50
        self.FREE_DELIVERY_THRESHOLD = 1000
        self.DISCOUNT_THRESHOLD = 5000
        self.DISCOUNT_PERCENTAGE = 10
    
    def calculate_cart_subtotal(self):
        return sum(item["quantity"] * item["price"] for item in self.cart)
    
    def calculate_delivery_charge(self, subtotal: float) -> float:
        if subtotal >= self.FREE_DELIVERY_THRESHOLD:
            return 0
        return self.DELIVERY_CHARGE
    
    def calculate_discount(self, subtotal: float) -> float:
        if subtotal >= self.DISCOUNT_THRESHOLD:
            return subtotal * (self.DISCOUNT_PERCENTAGE / 100)
        return 0
    
    def calculate_order_total(self):
        subtotal = self.calculate_cart_subtotal()
        delivery = self.calculate_delivery_charge(subtotal)
        discount = self.calculate_discount(subtotal)
        total = subtotal + delivery - discount
        
        return {
            "subtotal": subtotal,
            "delivery_charge": delivery,
            "discount": discount,
            "total": total
        }

def test_pricing():
    print("=" * 60)
    print("DailyMart Pricing Test Suite")
    print("=" * 60)
    
    # Test 1: Small order (₹500)
    print("\n📦 Test 1: Small Order (₹500)")
    agent = MockAgent()
    agent.cart = [
        {"name": "Milk", "quantity": 5, "price": 60},
        {"name": "Bread", "quantity": 2, "price": 100}
    ]
    pricing = agent.calculate_order_total()
    print(f"Subtotal: ₹{pricing['subtotal']}")
    print(f"Delivery: ₹{pricing['delivery_charge']}")
    print(f"Discount: ₹{pricing['discount']}")
    print(f"Total: ₹{pricing['total']}")
    assert pricing['subtotal'] == 500
    assert pricing['delivery_charge'] == 50
    assert pricing['discount'] == 0
    assert pricing['total'] == 550
    print("✅ PASSED")
    
    # Test 2: Free delivery threshold (₹1000)
    print("\n📦 Test 2: Free Delivery Threshold (₹1000)")
    agent = MockAgent()
    agent.cart = [
        {"name": "Rice", "quantity": 5, "price": 150},
        {"name": "Oil", "quantity": 1, "price": 250}
    ]
    pricing = agent.calculate_order_total()
    print(f"Subtotal: ₹{pricing['subtotal']}")
    print(f"Delivery: ₹{pricing['delivery_charge']} (FREE!)")
    print(f"Discount: ₹{pricing['discount']}")
    print(f"Total: ₹{pricing['total']}")
    assert pricing['subtotal'] == 1000
    assert pricing['delivery_charge'] == 0
    assert pricing['discount'] == 0
    assert pricing['total'] == 1000
    print("✅ PASSED")
    
    # Test 3: Just below free delivery (₹999)
    print("\n📦 Test 3: Just Below Free Delivery (₹999)")
    agent = MockAgent()
    agent.cart = [
        {"name": "Items", "quantity": 1, "price": 999}
    ]
    pricing = agent.calculate_order_total()
    print(f"Subtotal: ₹{pricing['subtotal']}")
    print(f"Delivery: ₹{pricing['delivery_charge']} (₹1 away from free!)")
    print(f"Discount: ₹{pricing['discount']}")
    print(f"Total: ₹{pricing['total']}")
    assert pricing['subtotal'] == 999
    assert pricing['delivery_charge'] == 50
    assert pricing['discount'] == 0
    assert pricing['total'] == 1049
    print("✅ PASSED")
    
    # Test 4: Discount threshold (₹5000)
    print("\n📦 Test 4: Discount Threshold (₹5000)")
    agent = MockAgent()
    agent.cart = [
        {"name": "Bulk Items", "quantity": 1, "price": 5000}
    ]
    pricing = agent.calculate_order_total()
    print(f"Subtotal: ₹{pricing['subtotal']}")
    print(f"Delivery: ₹{pricing['delivery_charge']} (FREE!)")
    print(f"Discount: ₹{pricing['discount']} (10% off)")
    print(f"Total: ₹{pricing['total']}")
    assert pricing['subtotal'] == 5000
    assert pricing['delivery_charge'] == 0
    assert pricing['discount'] == 500
    assert pricing['total'] == 4500
    print("✅ PASSED")
    
    # Test 5: Large order with all benefits (₹6000)
    print("\n📦 Test 5: Large Order with All Benefits (₹6000)")
    agent = MockAgent()
    agent.cart = [
        {"name": "Premium Items", "quantity": 1, "price": 6000}
    ]
    pricing = agent.calculate_order_total()
    print(f"Subtotal: ₹{pricing['subtotal']}")
    print(f"Delivery: ₹{pricing['delivery_charge']} (FREE!)")
    print(f"Discount: ₹{pricing['discount']} (10% off)")
    print(f"Total: ₹{pricing['total']}")
    assert pricing['subtotal'] == 6000
    assert pricing['delivery_charge'] == 0
    assert pricing['discount'] == 600
    assert pricing['total'] == 5400
    print("✅ PASSED")
    
    # Test 6: Just below discount (₹4999)
    print("\n📦 Test 6: Just Below Discount (₹4999)")
    agent = MockAgent()
    agent.cart = [
        {"name": "Items", "quantity": 1, "price": 4999}
    ]
    pricing = agent.calculate_order_total()
    print(f"Subtotal: ₹{pricing['subtotal']}")
    print(f"Delivery: ₹{pricing['delivery_charge']} (FREE!)")
    print(f"Discount: ₹{pricing['discount']} (₹1 away from discount!)")
    print(f"Total: ₹{pricing['total']}")
    assert pricing['subtotal'] == 4999
    assert pricing['delivery_charge'] == 0
    assert pricing['discount'] == 0
    assert pricing['total'] == 4999
    print("✅ PASSED")
    
    print("\n" + "=" * 60)
    print("✅ All Tests Passed!")
    print("=" * 60)
    
    # Summary
    print("\n📊 Pricing Rules Summary:")
    print(f"  • Delivery: ₹50 (FREE above ₹1000)")
    print(f"  • Discount: 10% (on orders above ₹5000, festival only)")
    print(f"  • Formula: Total = Subtotal + Delivery - Discount")

if __name__ == "__main__":
    test_pricing()
