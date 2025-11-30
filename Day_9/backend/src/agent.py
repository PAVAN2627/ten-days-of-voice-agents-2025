import logging
import sys
from pathlib import Path
from typing import Optional

# Add parent directory to path to import commerce module
sys.path.append(str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    MetricsCollectedEvent,
    RoomInputOptions,
    WorkerOptions,
    cli,
    metrics,
    tokenize,
    function_tool,
    RunContext
)
from livekit.plugins import murf, silero, google, deepgram, noise_cancellation
from livekit.plugins.turn_detector.multilingual import MultilingualModel

# Import our commerce functions
from commerce import (
    list_products,
    create_order,
    get_order,
    get_recent_orders,
    get_categories,
    search_products,
    get_product_by_id,
    get_orders_by_user,
    get_orders_by_status,
    calculate_user_spending,
    get_spending_by_category,
    update_order_status,
    get_cart,
    save_cart
)
from auth import (
    create_user,
    authenticate_user,
    get_user_by_email
)
from email_service import send_order_confirmation_email

logger = logging.getLogger("agent")
logger.info("E-commerce Voice Agent Starting...")

load_dotenv(".env.local")

# Session state for shopping cart
class ShoppingSession:
    def __init__(self):
        self.user = None  # Current authenticated user
        self.cart = []  # List of {product_id, quantity, name, price}
        self.last_shown_products = []  # For reference like "the second item"
        self.last_order_id = None
    
    def reset(self):
        """Reset session state"""
        self.user = None
        self.cart = []
        self.last_shown_products = []
        self.last_order_id = None

shopping_session = ShoppingSession()


class ECommerceAgent(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""You are a friendly e-commerce voice shopping assistant following ACP (Agentic Commerce Protocol) patterns.

Your role:
1. First, help users login or create account
2. Help customers browse products by voice
3. Add items to their shopping cart
4. Process orders and provide confirmations
5. Answer questions about products and orders

User Authentication:
- Always ask new users if they have an account or need to create one
- For existing users: ask for email and password
- For new users: collect name, email, password, phone, and address

Available product categories: mugs, clothing, books, accessories, electronics

When customers ask to browse:
- Use browse_catalog to show products
- Remember the order you show them for references like "the second item"

When customers want to buy:
- Add items to cart first
- Show cart contents
- Confirm before placing order
- If customer wants to change size of an item already in cart, use update_item_size instead of adding a duplicate

IMPORTANT - Size Requirements:
- ONLY ask for size when adding CLOTHING items (t-shirts, hoodies, etc.)
- DO NOT ask for size for electronics, mugs, books, or accessories
- For non-clothing items, add them directly to cart without asking about size
- Valid sizes are: S, M, L, XL, XXL (single letter M, not EM or other variations)
- When user says "M" or "medium", use "M" as the size

Be conversational, helpful, and always confirm important actions.
Prices are in Indian Rupees (Rs.).
Do not use complex formatting, emojis, or asterisks in your responses.""",
        )

    @function_tool
    async def browse_catalog(
        self, 
        context: RunContext, 
        category: str = "", 
        search_query: str = "", 
        max_price: int = 0
    ) -> str:
        """Browse the product catalog with optional filters.
        
        Args:
            category: Filter by category (mug, clothing, books, accessories, electronics). Leave empty for all.
            search_query: Search in product names and descriptions. Leave empty to skip search.
            max_price: Maximum price filter in rupees. Set to 0 to skip price filter.
        """
        filters = {}
        if category and category.strip():
            filters['category'] = category
        if search_query and search_query.strip():
            filters['search'] = search_query
        if max_price and max_price > 0:
            filters['max_price'] = max_price
            
        products = list_products(filters)
        
        if not products:
            return "No products found matching your criteria. Try browsing all categories or adjusting your filters."
        
        # Store for reference ("the second item")
        shopping_session.last_shown_products = products[:10]  # Limit to 10 for voice
        
        result = f"Found {len(products)} products. Here are the first few:\n"
        for i, product in enumerate(products[:5], 1):
            result += f"{i}. {product['name']} - Rs.{product['price']} ({product.get('description', 'No description')})\n"
        
        if len(products) > 5:
            result += f"And {len(products) - 5} more items available."
            
        return result
    
    @function_tool
    async def add_to_cart(self, context: RunContext, product_reference: str, quantity: int = 1, size: str = "") -> str:
        """Add item to shopping cart.
        
        Args:
            product_reference: Product name, ID, or reference like "first item", "second hoodie"
            quantity: Number of items to add
            size: Size for clothing items (S, M, L, XL). Required for t-shirts, hoodies, and clothing.
        """
        if not shopping_session.user:
            return "Please login or create an account first to add items to cart. Say 'I want to login with email [your-email] and password [your-password]' or 'Create account for [your-name] with email [your-email]'."
        
        # Sync cart from frontend first
        try:
            import requests
            response = requests.get('http://localhost:3000/api/cart', timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('cart'):
                    shopping_session.cart = [{
                        'product_id': item['id'],
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': item['quantity'],
                        'size': item.get('size', '')
                    } for item in data['cart']]
        except:
            pass
        
        product = None
        
        # Handle references like "first item", "second item"
        if "first" in product_reference.lower() or "1" in product_reference:
            if shopping_session.last_shown_products:
                product = shopping_session.last_shown_products[0]
        elif "second" in product_reference.lower() or "2" in product_reference:
            if len(shopping_session.last_shown_products) > 1:
                product = shopping_session.last_shown_products[1]
        elif "third" in product_reference.lower() or "3" in product_reference:
            if len(shopping_session.last_shown_products) > 2:
                product = shopping_session.last_shown_products[2]
        else:
            # Search by name or ID
            # First try exact ID match
            product = get_product_by_id(product_reference)
            
            # If not found, search by name
            if not product:
                search_results = search_products(product_reference)
                if search_results:
                    product = search_results[0]  # Take first match
        
        if not product:
            return f"Could not find '{product_reference}'. Please browse the catalog first or be more specific."
        
        # Check if clothing item requires size
        if product['category'] == 'clothing' and not size:
            return f"Please specify the size for {product['name']}. Available sizes are S, M, L, XL, XXL. Say 'Add {product['name']} size M to cart' or similar."
        
        # Add to cart
        cart_item = {
            'product_id': product['id'],
            'name': product['name'],
            'price': product['price'],
            'quantity': quantity,
            'size': size if size else ''
        }
        
        # Normalize size input
        if size:
            size = size.strip().upper()
            # Handle common variations
            if size in ['MEDIUM', 'MED']:
                size = 'M'
            elif size in ['SMALL']:
                size = 'S'
            elif size in ['LARGE']:
                size = 'L'
            elif size in ['EXTRA LARGE', 'XLARGE', 'X-LARGE']:
                size = 'XL'
            elif size in ['DOUBLE XL', 'DOUBLE EXTRA LARGE', '2XL', 'XX-LARGE']:
                size = 'XXL'
            # Remove invalid sizes like "EM"
            if size not in ['S', 'M', 'L', 'XL', 'XXL']:
                size = ''
        
        # Check if item already in cart (same product and size)
        found = False
        for item in shopping_session.cart:
            if item['product_id'] == product['id'] and item.get('size', '') == size:
                item['quantity'] += quantity
                total_price = item['quantity'] * item['price']
                found = True
                
                # Sync with frontend
                try:
                    import requests
                    cart_for_frontend = [{
                        'id': item['product_id'],
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': item['quantity'],
                        'size': item.get('size', '')
                    } for item in shopping_session.cart]
                    requests.post('http://localhost:3000/api/cart', 
                        json={'action': 'sync', 'cart': cart_for_frontend}, timeout=1)
                except:
                    pass
                
                return f"Updated {product['name']} quantity to {item['quantity']}. Item total: Rs.{total_price}"
        
        if not found:
            shopping_session.cart.append(cart_item)
            item_total = quantity * product['price']
            
            # Sync with frontend
            try:
                import requests
                cart_for_frontend = [{
                    'id': item['product_id'],
                    'name': item['name'],
                    'price': item['price'],
                    'quantity': item['quantity'],
                    'size': item.get('size', '')
                } for item in shopping_session.cart]
                requests.post('http://localhost:3000/api/cart', 
                    json={'action': 'sync', 'cart': cart_for_frontend}, timeout=1)
            except:
                pass
            
            size_text = f" (size {size})" if size else ""
            return f"Added {quantity} {product['name']}{size_text} to cart for Rs.{item_total}. Say 'show cart' to review."
    
    @function_tool
    async def show_cart(self, context: RunContext) -> str:
        """Show current shopping cart contents."""
        # Sync with frontend cart first
        try:
            import requests
            response = requests.get('http://localhost:3000/api/cart', timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('cart'):
                    # Update backend cart from frontend
                    shopping_session.cart = [{
                        'product_id': item['id'],
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': item['quantity']
                    } for item in data['cart']]
        except:
            pass  # If sync fails, use backend cart
        
        if not shopping_session.cart:
            return "Your cart is empty. Browse products and add items to get started."
        
        result = "Your shopping cart:\n"
        total = 0
        
        for i, item in enumerate(shopping_session.cart, 1):
            item_total = item['quantity'] * item['price']
            result += f"{i}. {item['name']} x{item['quantity']} = Rs.{item_total}\n"
            total += item_total
        
        result += f"\nTotal: Rs.{total}"
        result += "\nSay 'place order' to checkout or 'remove item' to modify cart."
        
        return result
    
    @function_tool
    async def remove_from_cart(self, context: RunContext, product_reference: str) -> str:
        """Remove item from shopping cart.
        
        Args:
            product_reference: Product name or reference to remove
        """
        # Sync cart from frontend first
        try:
            import requests
            response = requests.get('http://localhost:3000/api/cart', timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('cart'):
                    shopping_session.cart = [{
                        'product_id': item['id'],
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': item['quantity'],
                        'size': item.get('size', '')
                    } for item in data['cart']]
        except:
            pass
        
        if not shopping_session.cart:
            return "Your cart is empty."
        
        # Find item to remove
        for i, item in enumerate(shopping_session.cart):
            if (product_reference.lower() in item['name'].lower() or 
                product_reference == item['product_id']):
                removed_item = shopping_session.cart.pop(i)
                
                # Sync with frontend
                try:
                    import requests
                    cart_for_frontend = [{
                        'id': item['product_id'],
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': item['quantity'],
                        'size': item.get('size', '')
                    } for item in shopping_session.cart]
                    requests.post('http://localhost:3000/api/cart', 
                        json={'action': 'sync', 'cart': cart_for_frontend}, timeout=1)
                except:
                    pass
                
                return f"Removed {removed_item['name']} from cart."
        
        return f"Could not find '{product_reference}' in your cart."
    
    @function_tool
    async def place_order(self, context: RunContext) -> str:
        """Place the current order."""
        if not shopping_session.user:
            return "Please login first to place an order."
        
        # Sync cart from frontend first
        try:
            import requests
            response = requests.get('http://localhost:3000/api/cart', timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('cart'):
                    shopping_session.cart = [{
                        'product_id': item['id'],
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': item['quantity'],
                        'size': item.get('size', '')
                    } for item in data['cart']]
        except:
            pass
        
        if not shopping_session.cart:
            return "Your cart is empty. Add items before placing an order."
        
        # Convert cart to line items
        line_items = []
        for item in shopping_session.cart:
            line_item = {
                'product_id': item['product_id'],
                'quantity': item['quantity']
            }
            # Include size if present
            if item.get('size'):
                line_item['size'] = item['size']
            line_items.append(line_item)
        
        # Prepare buyer info from logged-in user
        buyer_info = {
            'name': shopping_session.user['name'],
            'email': shopping_session.user['email'],
            'phone': shopping_session.user['phone'],
            'address': shopping_session.user['address']
        }
        
        # Create order with error handling
        try:
            order = create_order(line_items, buyer_info)
            shopping_session.last_order_id = order['id']
            
            # Send order confirmation email
            try:
                email_sent = send_order_confirmation_email(
                    order=order,
                    user_email=shopping_session.user['email'],
                    user_name=shopping_session.user['name']
                )
                if email_sent:
                    logger.info(f"✅ Order confirmation email sent to {shopping_session.user['email']}")
                else:
                    logger.warning(f"⚠️ Failed to send order confirmation email")
            except Exception as email_error:
                logger.error(f"❌ Error sending email: {str(email_error)}")
            
            # Clear cart after successful order
            shopping_session.cart = []
            
            # Notify frontend to clear cart and show success message
            try:
                import requests
                # Send order details to frontend
                requests.post('http://localhost:3000/api/order-placed', 
                    json={'order': {
                        'id': order['id'],
                        'total_amount': order['total_amount'],
                        'line_items': order['line_items']
                    }}, timeout=1)
                # Also clear frontend cart
                requests.post('http://localhost:3000/api/cart', 
                    json={'action': 'sync', 'cart': []}, timeout=1)
            except Exception as e:
                logger.warning(f"Could not notify frontend: {e}")
                pass  # Frontend notification is optional
            
            result = f"Order placed successfully!\n"
            result += f"Order ID: {order['id']}\n"
            result += f"Total: Rs.{order['total_amount']}\n"
            result += f"Delivery to: {shopping_session.user['address']}\n"
            result += f"Status: {order['status']}\n"
            result += "A confirmation email has been sent to your email address.\n"
            result += "Thank you for your purchase!"
            
            return result
        
        except ValueError as e:
            return f"Error creating order: {str(e)}"
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
    
    @function_tool
    async def show_last_order(self, context: RunContext) -> str:
        """Show details of the last placed order."""
        if not shopping_session.last_order_id:
            # Try to get most recent order
            recent_orders = get_recent_orders(1)
            if not recent_orders:
                return "No orders found."
            order = recent_orders[0]
        else:
            order = get_order(shopping_session.last_order_id)
        
        if not order:
            return "Could not find your last order."
        
        result = f"Your last order (ID: {order['id']}):\n"
        result += f"Status: {order['status']}\n"
        result += f"Total: Rs.{order['total_amount']}\n"
        result += "Items:\n"
        
        for item in order['line_items']:
            result += f"- {item['name']} x{item['quantity']} = Rs.{item['line_total']}\n"
        
        result += f"Ordered on: {order['created_at'][:10]}"
        
        return result
    
    @function_tool
    async def get_categories(self, context: RunContext) -> str:
        """Show available product categories."""
        categories = get_categories()
        return f"Available categories: {', '.join(categories)}. Say 'show me [category]' to browse."
    
    @function_tool
    async def login_user(self, context: RunContext, email: str, password: str) -> str:
        """Login existing user."""
        user = authenticate_user(email, password)
        if user:
            shopping_session.user = user
            # Sync with frontend
            try:
                import requests
                requests.post('http://localhost:3000/api/auth', 
                    json={'action': 'login', 'name': user['name'], 'email': user['email']})
            except:
                pass  # Frontend sync is optional
            return f"Welcome back, {user['name']}! You can now start shopping."
        else:
            return "Invalid email or password. Please try again or create a new account."
    
    @function_tool
    async def create_account(self, context: RunContext, name: str, email: str, password: str, phone: str, address: str) -> str:
        """Create new user account."""
        user = create_user(email, password, name, phone, address)
        if user:
            shopping_session.user = user
            # Sync with frontend
            try:
                import requests
                requests.post('http://localhost:3000/api/auth', 
                    json={'action': 'login', 'name': user['name'], 'email': user['email']})
            except:
                pass  # Frontend sync is optional
            return f"Account created successfully! Welcome {name}. You can now start shopping."
        else:
            return "Email already exists. Please login or use a different email."
    
    @function_tool
    async def update_item_size(self, context: RunContext, product_reference: str, new_size: str) -> str:
        """Update the size of a clothing item already in cart.
        
        Args:
            product_reference: Product name or reference
            new_size: New size (S, M, L, XL)
        """
        # Sync cart from frontend first
        try:
            import requests
            response = requests.get('http://localhost:3000/api/cart', timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('cart'):
                    shopping_session.cart = [{
                        'product_id': item['id'],
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': item['quantity'],
                        'size': item.get('size', '')
                    } for item in data['cart']]
        except:
            pass
        
        if not shopping_session.cart:
            return "Your cart is empty."
        
        # Normalize size
        new_size = new_size.strip().upper()
        if new_size in ['MEDIUM', 'MED']:
            new_size = 'M'
        elif new_size in ['SMALL']:
            new_size = 'S'
        elif new_size in ['LARGE']:
            new_size = 'L'
        elif new_size in ['EXTRA LARGE', 'XLARGE', 'X-LARGE']:
            new_size = 'XL'
        elif new_size in ['DOUBLE XL', 'DOUBLE EXTRA LARGE', '2XL', 'XX-LARGE']:
            new_size = 'XXL'
        
        if new_size not in ['S', 'M', 'L', 'XL', 'XXL']:
            return f"Invalid size '{new_size}'. Valid sizes are S, M, L, XL, XXL."
        
        # Find item and update size
        for item in shopping_session.cart:
            if (product_reference.lower() in item['name'].lower() or 
                product_reference == item['product_id']):
                old_size = item.get('size', 'no size')
                item['size'] = new_size
                
                # Sync with frontend
                try:
                    import requests
                    cart_for_frontend = [{
                        'id': cart_item['product_id'],
                        'name': cart_item['name'],
                        'price': cart_item['price'],
                        'quantity': cart_item['quantity'],
                        'size': cart_item.get('size', '')
                    } for cart_item in shopping_session.cart]
                    requests.post('http://localhost:3000/api/cart', 
                        json={'action': 'sync', 'cart': cart_for_frontend}, timeout=1)
                except:
                    pass
                
                return f"Updated {item['name']} size from {old_size} to {new_size}."
        
        return f"Could not find '{product_reference}' in your cart."
    
    @function_tool
    async def update_cart_quantity(self, context: RunContext, product_reference: str, quantity: int) -> str:
        """Update quantity of item in cart."""
        # Sync cart from frontend first
        try:
            import requests
            response = requests.get('http://localhost:3000/api/cart', timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and data.get('cart'):
                    shopping_session.cart = [{
                        'product_id': item['id'],
                        'name': item['name'],
                        'price': item['price'],
                        'quantity': item['quantity'],
                        'size': item.get('size', '')
                    } for item in data['cart']]
        except:
            pass
        
        if not shopping_session.cart:
            return "Your cart is empty."
        
        for item in shopping_session.cart:
            if (product_reference.lower() in item['name'].lower() or 
                product_reference == item['product_id']):
                old_qty = item['quantity']
                item['quantity'] = quantity
                
                if quantity <= 0:
                    shopping_session.cart.remove(item)
                    
                    # Sync with frontend
                    try:
                        import requests
                        cart_for_frontend = [{
                            'id': item['product_id'],
                            'name': item['name'],
                            'price': item['price'],
                            'quantity': item['quantity'],
                            'size': item.get('size', '')
                        } for item in shopping_session.cart]
                        requests.post('http://localhost:3000/api/cart', 
                            json={'action': 'sync', 'cart': cart_for_frontend}, timeout=1)
                    except:
                        pass
                    
                    return f"Removed {item['name']} from cart."
                else:
                    # Sync with frontend
                    try:
                        import requests
                        cart_for_frontend = [{
                            'id': cart_item['product_id'],
                            'name': cart_item['name'],
                            'price': cart_item['price'],
                            'quantity': cart_item['quantity'],
                            'size': cart_item.get('size', '')
                        } for cart_item in shopping_session.cart]
                        requests.post('http://localhost:3000/api/cart', 
                            json={'action': 'sync', 'cart': cart_for_frontend}, timeout=1)
                    except:
                        pass
                    
                    return f"Updated {item['name']} quantity from {old_qty} to {quantity}."
        
        return f"Could not find '{product_reference}' in your cart."
    
    @function_tool
    async def get_order_history(self, context: RunContext) -> str:
        """Get order history for the logged-in user."""
        if not shopping_session.user:
            return "Please login first to view your order history."
        
        email = shopping_session.user['email']
        orders = get_orders_by_user(email)
        
        if not orders:
            return "You have not placed any orders yet."
        
        result = f"Your order history ({len(orders)} orders):\n\n"
        for i, order in enumerate(orders[:5], 1):  # Show last 5
            result += f"{i}. Order ID: {order['id']}\n"
            result += f"   Total: Rs.{order['total_amount']}\n"
            result += f"   Status: {order['status']}\n"
            result += f"   Date: {order['created_at'][:10]}\n"
            result += f"   Items: {len(order['line_items'])}\n\n"
        
        if len(orders) > 5:
            result += f"... and {len(orders) - 5} more orders."
        
        return result
    
    @function_tool
    async def get_spending_info(self, context: RunContext) -> str:
        """Get spending summary for the logged-in user."""
        if not shopping_session.user:
            return "Please login first to view your spending."
        
        email = shopping_session.user['email']
        total_spending = calculate_user_spending(email)
        category_spending = get_spending_by_category(email)
        
        result = f"Your spending summary:\n"
        result += f"Total spent: Rs.{total_spending}\n\n"
        
        if category_spending:
            result += "Spending by category:\n"
            for category, amount in sorted(category_spending.items(), key=lambda x: x[1], reverse=True):
                result += f"- {category}: Rs.{amount}\n"
        else:
            result += "No purchases yet."
        
        return result
    
    @function_tool
    async def save_cart_for_later(self, context: RunContext) -> str:
        """Save current cart for later."""
        if not shopping_session.user:
            return "Please login first to save cart."
        
        if not shopping_session.cart:
            return "Your cart is empty."
        
        email = shopping_session.user['email']
        save_cart(email, shopping_session.cart)
        
        return f"Cart saved successfully with {len(shopping_session.cart)} items. You can continue shopping anytime."
    
    @function_tool
    async def load_saved_cart(self, context: RunContext) -> str:
        """Load previously saved cart."""
        if not shopping_session.user:
            return "Please login first to load saved cart."
        
        email = shopping_session.user['email']
        saved_cart = get_cart(email)
        
        if not saved_cart:
            return "You don't have a saved cart."
        
        shopping_session.cart = saved_cart
        
        total = sum(item['quantity'] * item['price'] for item in saved_cart)
        
        return f"Loaded saved cart with {len(saved_cart)} items. Total: Rs.{total}. Say 'show cart' to review."
    
    @function_tool
    async def track_order(self, context: RunContext, order_id: str) -> str:
        """Track a specific order by ID."""
        try:
            order = get_order(order_id)
            if not order:
                return f"Order {order_id} not found."
            
            result = f"Order Status: {order['id']}\n"
            result += f"Status: {order['status']}\n"
            result += f"Total: Rs.{order['total_amount']}\n"
            result += f"Items:\n"
            
            for item in order['line_items']:
                result += f"- {item['name']} x{item['quantity']} = Rs.{item['line_total']}\n"
            
            result += f"\nOrdered: {order['created_at'][:10]}\n"
            result += f"Last updated: {order['updated_at'][:10]}"
            
            return result
        except Exception as e:
            return f"Error retrieving order: {str(e)}"
    
    @function_tool
    async def list_order_statuses(self, context: RunContext) -> str:
        """Show available order statuses."""
        statuses = {
            "PENDING": "Order placed, awaiting confirmation",
            "CONFIRMED": "Order confirmed, being prepared",
            "SHIPPED": "Order shipped and on the way",
            "DELIVERED": "Order delivered",
            "CANCELLED": "Order cancelled"
        }
        
        result = "Available order statuses:\n"
        for status, description in statuses.items():
            result += f"• {status}: {description}\n"
        
        return result


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


async def entrypoint(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, AssemblyAI, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=deepgram.STT(model="nova-3"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=google.LLM(
                model="gemini-2.5-flash",
            ),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=murf.TTS(
                voice="en-IN-anusha", 
                style="Conversation",
                tokenizer=tokenize.basic.SentenceTokenizer(min_sentence_len=2),
                text_pacing=True
            ),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        turn_detection=MultilingualModel(),
        vad=ctx.proc.userdata["vad"],
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # Metrics collection, to measure pipeline performance
    # For more information, see https://docs.livekit.io/agents/build/metrics/
    usage_collector = metrics.UsageCollector()

    @session.on("metrics_collected")
    def _on_metrics_collected(ev: MetricsCollectedEvent):
        metrics.log_metrics(ev.metrics)
        usage_collector.collect(ev.metrics)

    async def log_usage():
        summary = usage_collector.get_summary()
        logger.info(f"Usage: {summary}")

    ctx.add_shutdown_callback(log_usage)

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=ECommerceAgent(),
        room=ctx.room,
        room_input_options=RoomInputOptions(
            # For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()


if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))