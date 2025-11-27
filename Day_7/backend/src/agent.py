import asyncio
import json
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import Annotated, Dict, List, Optional, Any
from dataclasses import dataclass, field
from pydantic import Field
from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    function_tool,
    RunContext
)
from livekit.plugins import deepgram, google, murf, silero
import hashlib
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env.local")

logger = logging.getLogger("dailymart-agent")

# User database (in production, use proper database)
USERS_FILE = "users.json"
ORDERS_FILE = "orders.json"
CATALOG_FILE = "catalog.json"

class DailyMartAgent:
    def __init__(self):
        self.current_user = None
        self.cart = []
        self.catalog = self.load_catalog()
        self.users = self.load_users()
        self.orders = self.load_orders()
        self.pending_order = None
        self.language_preference = None
        self.customer_name_used = False
        self.budget_limit = None
        self.dietary_filter = None
        self.order_statuses = ["received", "confirmed", "being_prepared", "out_for_delivery", "delivered"]
        
        # Pricing rules
        self.DELIVERY_CHARGE = 50  # ₹50 delivery charge
        self.FREE_DELIVERY_THRESHOLD = 1000  # Free delivery above ₹1000
        self.DISCOUNT_THRESHOLD = 5000  # Discount on orders above ₹5000
        self.DISCOUNT_PERCENTAGE = 10  # 10% discount on orders above ₹5000
        
    def load_catalog(self):
        try:
            with open(CATALOG_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {"categories": {}, "recipes": {}}
    
    def load_users(self):
        try:
            with open(USERS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_users(self):
        with open(USERS_FILE, 'w') as f:
            json.dump(self.users, f, indent=2)
    
    def load_orders(self):
        try:
            with open(ORDERS_FILE, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def save_orders(self):
        with open(ORDERS_FILE, 'w') as f:
            json.dump(self.orders, f, indent=2)
    
    def normalize_password(self, password: str) -> str:
        # Convert spoken numbers to digits
        password = password.lower().strip()
        replacements = {
            "zero": "0", "one": "1", "two": "2", "three": "3", "four": "4",
            "five": "5", "six": "6", "seven": "7", "eight": "8", "nine": "9"
        }
        for word, digit in replacements.items():
            password = password.replace(word, digit)
        # Remove spaces
        password = password.replace(" ", "")
        return password
    
    def find_item_by_name(self, item_name: str):
        item_name_lower = item_name.lower()
        for category_data in self.catalog["categories"].values():
            for item in category_data["items"]:
                if item_name_lower in item["name"].lower():
                    return item
        return None
    
    def get_recipe_ingredients(self, recipe_name: str):
        recipe_name_lower = recipe_name.lower()
        for recipe_key, recipe_data in self.catalog["recipes"].items():
            if recipe_name_lower in recipe_data["name"].lower() or recipe_name_lower in recipe_key:
                ingredients = []
                for ingredient_id in recipe_data["ingredients"]:
                    for category_data in self.catalog["categories"].values():
                        for item in category_data["items"]:
                            if item["id"] == ingredient_id:
                                ingredients.append(item)
                                break
                return ingredients, recipe_data["serves"]
        return [], 0
    
    def send_confirmation_email(self, order):
        try:
            smtp_server = os.getenv('SMTP_SERVER')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            sender_email = os.getenv('SENDER_EMAIL')
            sender_password = os.getenv('SENDER_PASSWORD')
            sender_name = os.getenv('SENDER_NAME', 'DailyMart')
            
            if not all([smtp_server, sender_email, sender_password]):
                return False
            
            customer = self.users[order['customer_email']]
            
            # Create HTML email with enhanced information
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; margin: 0; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }}
                    .container {{ max-width: 650px; margin: 0 auto; background-color: white; border-radius: 15px; box-shadow: 0 10px 40px rgba(0,0,0,0.2); overflow: hidden; }}
                    .header {{ background: linear-gradient(135deg, #0066cc 0%, #00aa66 100%); color: white; padding: 40px 30px; text-align: center; }}
                    .header h1 {{ margin: 0; font-size: 32px; font-weight: bold; }}
                    .header p {{ margin: 10px 0 0 0; font-size: 16px; opacity: 0.9; }}
                    .content {{ padding: 30px; }}
                    .greeting {{ font-size: 18px; color: #333; margin-bottom: 20px; }}
                    .order-info {{ background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); padding: 25px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #0066cc; }}
                    .order-info h3 {{ margin: 0 0 15px 0; color: #0066cc; font-size: 20px; }}
                    .info-row {{ display: flex; justify-content: space-between; padding: 8px 0; }}
                    .info-label {{ color: #666; font-weight: 500; }}
                    .info-value {{ color: #333; font-weight: bold; }}
                    .items-section {{ margin: 25px 0; }}
                    .items-section h3 {{ color: #333; font-size: 20px; margin-bottom: 15px; border-bottom: 2px solid #0066cc; padding-bottom: 10px; }}
                    .item-row {{ display: flex; justify-content: space-between; padding: 15px; margin: 10px 0; background-color: #f8f9fa; border-radius: 8px; border-left: 3px solid #00aa66; }}
                    .item-details {{ flex: 1; }}
                    .item-name {{ font-weight: bold; color: #333; font-size: 16px; }}
                    .item-meta {{ color: #666; font-size: 13px; margin-top: 5px; }}
                    .item-price {{ text-align: right; color: #0066cc; font-weight: bold; font-size: 16px; }}
                    .pricing-summary {{ background: linear-gradient(135deg, #e8f5e9 0%, #c8e6c9 100%); padding: 20px; border-radius: 10px; margin: 25px 0; }}
                    .price-row {{ display: flex; justify-content: space-between; padding: 8px 0; font-size: 15px; }}
                    .price-label {{ color: #555; }}
                    .price-value {{ color: #333; font-weight: 600; }}
                    .total-row {{ border-top: 2px solid #00aa66; margin-top: 10px; padding-top: 15px; font-size: 20px; font-weight: bold; }}
                    .total-row .price-label {{ color: #00aa66; }}
                    .total-row .price-value {{ color: #00aa66; }}
                    .address-section {{ background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%); padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #ff9800; }}
                    .address-section h3 {{ margin: 0 0 10px 0; color: #ff9800; font-size: 18px; }}
                    .contact-info {{ background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0; }}
                    .contact-info h3 {{ margin: 0 0 15px 0; color: #333; font-size: 18px; }}
                    .contact-row {{ padding: 5px 0; color: #555; }}
                    .status-badge {{ display: inline-block; padding: 8px 16px; background-color: #4caf50; color: white; border-radius: 20px; font-size: 14px; font-weight: bold; }}
                    .footer {{ background-color: #f8f9fa; padding: 25px 30px; text-align: center; color: #666; font-size: 13px; }}
                    .footer-links {{ margin: 15px 0; }}
                    .footer-links a {{ color: #0066cc; text-decoration: none; margin: 0 10px; }}
                    .highlight {{ background-color: #fff3cd; padding: 15px; border-radius: 8px; border-left: 4px solid #ffc107; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🛒 DailyMart</h1>
                        <p>Your Daily Essentials, Delivered Fresh</p>
                    </div>
                    
                    <div class="content">
                        <div class="greeting">
                            <p>Dear <strong>{customer['name']}</strong>,</p>
                            <p>Thank you for choosing DailyMart! Your order has been successfully confirmed and is being processed.</p>
                        </div>
                        
                        <div class="order-info">
                            <h3>📋 Order Information</h3>
                            <div class="info-row">
                                <span class="info-label">Order ID:</span>
                                <span class="info-value">{order['order_id']}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Order Date:</span>
                                <span class="info-value">{datetime.fromisoformat(order['timestamp']).strftime('%B %d, %Y at %I:%M %p')}</span>
                            </div>
                            <div class="info-row">
                                <span class="info-label">Status:</span>
                                <span class="status-badge">{order['status'].replace('_', ' ').title()}</span>
                            </div>
                        </div>
                        
                        <div class="items-section">
                            <h3>🛍️ Items Ordered</h3>
            """
            
            for item in order['items']:
                item_total = item['quantity'] * item['price']
                html_content += f"""
                            <div class="item-row">
                                <div class="item-details">
                                    <div class="item-name">{item['name']}</div>
                                    <div class="item-meta">{item['brand']} • {item['size']} • Qty: {item['quantity']}</div>
                                </div>
                                <div class="item-price">
                                    ₹{item['price']} × {item['quantity']}<br>
                                    <strong>₹{item_total}</strong>
                                </div>
                            </div>
                """
            
            # Get pricing details
            subtotal = order.get('subtotal', order['total'])
            delivery = order.get('delivery_charge', 0)
            discount = order.get('discount', 0)
            
            html_content += f"""
                        </div>
                        
                        <div class="pricing-summary">
                            <div class="price-row">
                                <span class="price-label">Subtotal:</span>
                                <span class="price-value">₹{subtotal}</span>
                            </div>
                            <div class="price-row">
                                <span class="price-label">Delivery Charge:</span>
                                <span class="price-value">{'FREE' if delivery == 0 else f'₹{delivery}'}</span>
                            </div>
            """
            
            if discount > 0:
                html_content += f"""
                            <div class="price-row" style="color: #4caf50;">
                                <span class="price-label">Discount (10%):</span>
                                <span class="price-value">-₹{discount}</span>
                            </div>
                """
            
            html_content += f"""
                            <div class="price-row total-row">
                                <span class="price-label">Total Amount:</span>
                                <span class="price-value">₹{order['total']}</span>
                            </div>
                        </div>
                        
                        <div class="address-section">
                            <h3>📍 Delivery Address</h3>
                            <p style="margin: 0; color: #555; font-size: 15px;">{order['delivery_address']}</p>
                        </div>
                        
                        <div class="contact-info">
                            <h3>👤 Customer Information</h3>
                            <div class="contact-row"><strong>Name:</strong> {customer['name']}</div>
                            <div class="contact-row"><strong>Email:</strong> {customer['email']}</div>
                            <div class="contact-row"><strong>Mobile:</strong> {customer.get('mobile', 'N/A')}</div>
                        </div>
                        
                        <div class="highlight">
                            <strong>📦 What's Next?</strong><br>
                            • Your order is being prepared<br>
                            • You'll receive updates via email and SMS<br>
                            • Expected delivery: Within 2-3 business days<br>
                            • Track your order using Order ID: <strong>{order['order_id']}</strong>
                        </div>
                        
                        <p style="text-align: center; color: #555; margin: 25px 0;">
                            Thank you for shopping with DailyMart!<br>
                            We appreciate your business and look forward to serving you again.
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Need Help?</strong></p>
                        <p>Contact us: support@dailymart.com | +91-1800-123-4567</p>
                        <div class="footer-links">
                            <a href="#">Track Order</a> |
                            <a href="#">FAQs</a> |
                            <a href="#">Contact Support</a>
                        </div>
                        <p style="margin-top: 20px; font-size: 11px; color: #999;">
                            This is an automated email. Please do not reply to this message.<br>
                            © 2025 DailyMart. All rights reserved.
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Order Confirmation - {order['order_id']}"
            msg['From'] = f"{sender_name} <{sender_email}>"
            msg['To'] = customer['email']
            
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)
            server.quit()
            
            return True
        except Exception as e:
            logger.error(f"Failed to send email: {e}")
            return False
    
    def update_order_status(self, order_id: str):
        """Simulate order status progression over time"""
        if order_id not in self.orders:
            return False
        
        order = self.orders[order_id]
        current_status = order["status"]
        
        if current_status in self.order_statuses:
            current_index = self.order_statuses.index(current_status)
            if current_index < len(self.order_statuses) - 1:
                order["status"] = self.order_statuses[current_index + 1]
                order["last_updated"] = datetime.now().isoformat()
                self.save_orders()
                return True
        return False
    
    def get_frequent_items(self):
        """Get frequently ordered items for recommendations"""
        if not self.current_user:
            return []
        
        item_counts = {}
        customer_orders = [order for order in self.orders.values() 
                         if order["customer_email"] == self.current_user]
        
        for order in customer_orders:
            for item in order["items"]:
                item_id = item["id"]
                item_counts[item_id] = item_counts.get(item_id, 0) + item["quantity"]
        
        # Return top 3 most frequent items
        sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)[:3]
        frequent_items = []
        
        for item_id, count in sorted_items:
            for category_data in self.catalog["categories"].values():
                for item in category_data["items"]:
                    if item["id"] == item_id:
                        frequent_items.append(item)
                        break
        
        return frequent_items
    
    def calculate_cart_subtotal(self):
        """Calculate cart subtotal (before delivery and discount)"""
        return sum(item["quantity"] * item["price"] for item in self.cart)
    
    def calculate_delivery_charge(self, subtotal: float) -> float:
        """Calculate delivery charge based on order value"""
        if subtotal >= self.FREE_DELIVERY_THRESHOLD:
            return 0
        return self.DELIVERY_CHARGE
    
    def calculate_discount(self, subtotal: float) -> float:
        """Calculate discount based on order value"""
        if subtotal >= self.DISCOUNT_THRESHOLD:
            return subtotal * (self.DISCOUNT_PERCENTAGE / 100)
        return 0
    
    def calculate_order_total(self):
        """Calculate final order total with delivery and discount"""
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

@dataclass
class Userdata:
    """User session data"""
    agent: DailyMartAgent

@function_tool
async def register_new_customer(
    ctx: RunContext[Userdata],
    name: Annotated[str, Field(description="Customer's full name")],
    email: Annotated[str, Field(description="Customer's email address")],
    password: Annotated[str, Field(description="Customer's chosen password")],
    address: Annotated[str, Field(description="Customer's delivery address")],
    mobile: Annotated[str, Field(description="Customer's mobile number")]
) -> str:
    """Register a new customer with their details."""
    agent = ctx.userdata.agent
    if email in agent.users:
        return f"Email {email} is already registered. Please try logging in instead."
    
    agent.users[email] = {
        "name": name,
        "email": email,
        "password": agent.normalize_password(password),
        "address": address,
        "mobile": mobile,
        "created_at": datetime.now().isoformat()
    }
    agent.save_users()
    agent.current_user = email
    return f"Welcome {name}! Your account has been created successfully. You're now logged in and ready to shop."

@function_tool
async def login_customer(
    ctx: RunContext[Userdata],
    email: Annotated[str, Field(description="Customer's email address")],
    password: Annotated[str, Field(description="Customer's password")]
) -> str:
    """Login existing customer with email and password."""
    agent = ctx.userdata.agent
    if email not in agent.users:
        return "Email not found. Please check your email or register as a new customer."
    
    if agent.users[email]["password"] != agent.normalize_password(password):
        return "Incorrect password. Please try again."
    
    agent.current_user = email
    user_name = agent.users[email]["name"]
    return f"Welcome back {user_name}! You're now logged in and ready to shop."

@function_tool
async def add_item_to_cart(
    ctx: RunContext[Userdata],
    item_name: Annotated[str, Field(description="Name of the item to add")],
    quantity: Annotated[int, Field(description="Quantity of the item")] = 1
) -> str:
    """Add an item to the shopping cart."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first to start shopping."
    
    item = agent.find_item_by_name(item_name)
    if not item:
        return f"Sorry, I couldn't find '{item_name}' in our catalog. Could you try a different name?"
    
    # Check if item already in cart
    for cart_item in agent.cart:
        if cart_item["id"] == item["id"]:
            cart_item["quantity"] += quantity
            total_price = cart_item["quantity"] * item["price"]
            return f"Updated {item['name']} quantity to {cart_item['quantity']} (₹{total_price})"
    
    # Check dietary filter
    if agent.dietary_filter:
        item_tags = [tag.lower() for tag in item.get("tags", [])]
        if agent.dietary_filter not in item_tags:
            return f"Sorry, {item['name']} doesn't match your {agent.dietary_filter} dietary preference."
    
    # Check budget limit
    if agent.budget_limit:
        current_total = sum(cart_item["quantity"] * cart_item["price"] for cart_item in agent.cart)
        new_total = current_total + (quantity * item["price"])
        if new_total > agent.budget_limit:
            return f"Adding {item['name']} would exceed your budget limit of ₹{agent.budget_limit}. Current total would be ₹{new_total}."
    
    # Add new item to cart
    cart_item = {
        "id": item["id"],
        "name": item["name"],
        "price": item["price"],
        "quantity": quantity,
        "brand": item.get("brand", ""),
        "size": item.get("size", "")
    }
    agent.cart.append(cart_item)
    total_price = quantity * item["price"]
    return f"Added {quantity} {item['name']} to your cart (₹{total_price})"

@function_tool
async def add_recipe_ingredients(
    ctx: RunContext[Userdata],
    recipe_name: Annotated[str, Field(description="Name of the recipe or dish")]
) -> str:
    """Add all ingredients for a specific recipe to the cart."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first to start shopping."
    
    ingredients, serves = agent.get_recipe_ingredients(recipe_name)
    if not ingredients:
        return f"Sorry, I don't have a recipe for '{recipe_name}'. Try asking for specific ingredients instead."
    
    added_items = []
    total_cost = 0
    
    for ingredient in ingredients:
        # Check if already in cart
        found = False
        for cart_item in agent.cart:
            if cart_item["id"] == ingredient["id"]:
                cart_item["quantity"] += 1
                found = True
                break
        
        if not found:
            cart_item = {
                "id": ingredient["id"],
                "name": ingredient["name"],
                "price": ingredient["price"],
                "quantity": 1,
                "brand": ingredient.get("brand", ""),
                "size": ingredient.get("size", "")
            }
            agent.cart.append(cart_item)
        
        added_items.append(ingredient["name"])
        total_cost += ingredient["price"]
    
    return f"Added ingredients for {recipe_name} (serves {serves}): {', '.join(added_items)}. Total: ₹{total_cost}"

@function_tool
async def show_catalog(
    ctx: RunContext[Userdata],
    category: Annotated[str, Field(description="Category to show: groceries, spices, snacks, prepared_food, beverages, sweets, or all")] = "all"
) -> str:
    """Show catalog items by category or all categories."""
    agent = ctx.userdata.agent
    
    if category.lower() == "all":
        catalog_text = "Here are our available categories:\n\n"
        for cat_key, cat_data in agent.catalog["categories"].items():
            catalog_text += f"📂 {cat_data['name']} ({len(cat_data['items'])} items)\n"
        catalog_text += "\nWhich category would you like to see? Say 'show groceries' or 'show snacks' etc."
        return catalog_text
    
    # Find matching category
    category_lower = category.lower()
    matching_category = None
    
    for cat_key, cat_data in agent.catalog["categories"].items():
        if category_lower in cat_key.lower() or category_lower in cat_data["name"].lower():
            matching_category = cat_data
            break
    
    if not matching_category:
        available_cats = ", ".join([cat_data["name"] for cat_data in agent.catalog["categories"].values()])
        return f"Category not found. Available categories: {available_cats}"
    
    catalog_text = f"📂 {matching_category['name']}:\n\n"
    
    for item in matching_category["items"]:
        catalog_text += f"• {item['name']} - ₹{item['price']} ({item['brand']}, {item['size']})\n"
    
    catalog_text += f"\nTotal {len(matching_category['items'])} items available. Say 'add [item name]' to add to cart."
    return catalog_text

@function_tool
async def remove_item_from_cart(
    ctx: RunContext[Userdata],
    item_name: Annotated[str, Field(description="Name of the item to remove")]
) -> str:
    """Remove an item from the shopping cart."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    for i, cart_item in enumerate(agent.cart):
        if item_name.lower() in cart_item["name"].lower():
            removed_item = agent.cart.pop(i)
            return f"Removed {removed_item['name']} from your cart"
    
    return f"'{item_name}' not found in your cart"

@function_tool
async def update_item_quantity(
    ctx: RunContext[Userdata],
    item_name: Annotated[str, Field(description="Name of the item to update")],
    new_quantity: Annotated[int, Field(description="New quantity for the item")]
) -> str:
    """Update the quantity of an item in the cart."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    for cart_item in agent.cart:
        if item_name.lower() in cart_item["name"].lower():
            if new_quantity <= 0:
                agent.cart.remove(cart_item)
                return f"Removed {cart_item['name']} from your cart"
            else:
                cart_item["quantity"] = new_quantity
                total_price = cart_item["quantity"] * cart_item["price"]
                return f"Updated {cart_item['name']} quantity to {new_quantity} (₹{total_price})"
    
    return f"'{item_name}' not found in your cart"

# Removed language preference - English only

@function_tool
async def view_cart(ctx: RunContext[Userdata]) -> str:
    """Show all items currently in the shopping cart."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    if not agent.cart:
        return "Your cart is empty. Start adding some items!"
    
    cart_summary = "Your cart contains:\n"
    total = 0
    
    for item in agent.cart:
        item_total = item["quantity"] * item["price"]
        total += item_total
        cart_summary += f"- {item['quantity']}x {item['name']} (₹{item['price']} each) = ₹{item_total}\n"
    
    cart_summary += f"\nTotal: ₹{total}"
    return cart_summary

@function_tool
async def review_order_details(ctx: RunContext[Userdata]) -> str:
    """Review order details before confirmation with delivery charges and discounts."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    if not agent.cart:
        return "Your cart is empty. Add some items before placing an order."
    
    customer = agent.users[agent.current_user]
    pricing = agent.calculate_order_total()
    
    # Create pending order with pricing details
    order_id = f"ORD_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    agent.pending_order = {
        "order_id": order_id,
        "customer_email": agent.current_user,
        "customer_name": customer["name"],
        "items": agent.cart.copy(),
        "subtotal": pricing["subtotal"],
        "delivery_charge": pricing["delivery_charge"],
        "discount": pricing["discount"],
        "total": pricing["total"],
        "status": "pending_confirmation",
        "timestamp": datetime.now().isoformat(),
        "delivery_address": customer["address"]
    }
    
    review_text = f"Please review your order details:\n\n"
    review_text += f"Name: {customer['name']}\n"
    review_text += f"Email: {customer['email']}\n"
    review_text += f"Delivery Address: {customer['address']}\n\n"
    review_text += f"Order Items:\n"
    
    for item in agent.cart:
        item_total = item["quantity"] * item["price"]
        review_text += f"- {item['quantity']}x {item['name']} = ₹{item_total}\n"
    
    review_text += f"\nSubtotal: ₹{pricing['subtotal']}"
    
    if pricing['delivery_charge'] > 0:
        review_text += f"\nDelivery Charge: ₹{pricing['delivery_charge']}"
    else:
        review_text += f"\nDelivery Charge: FREE"
    
    if pricing['discount'] > 0:
        review_text += f"\nDiscount ({agent.DISCOUNT_PERCENTAGE}%): -₹{pricing['discount']}"
    
    review_text += f"\n\nTotal Amount: ₹{pricing['total']}\n\n"
    review_text += "Are all these details correct? Say 'yes' to confirm your order or 'no' to make changes."
    
    return review_text

@function_tool
async def reset_password(
    ctx: RunContext[Userdata],
    email: Annotated[str, Field(description="Customer's email address")],
    new_password: Annotated[str, Field(description="Customer's new password")]
) -> str:
    """Reset customer password."""
    agent = ctx.userdata.agent
    
    if email not in agent.users:
        return "Email not found. Please register as a new customer."
    
    agent.users[email]["password"] = agent.normalize_password(new_password)
    agent.save_users()
    
    return f"Password reset successfully for {email}. You can now log in with your new password."

@function_tool
async def show_order_history(ctx: RunContext[Userdata]) -> str:
    """Show customer's order history with detailed information about previous orders."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    # Show recent orders for this customer
    customer_orders = [order for order in agent.orders.values() 
                     if order["customer_email"] == agent.current_user]
    if not customer_orders:
        return "You have no orders yet. Start shopping to place your first order!"
    
    recent_orders = sorted(customer_orders, key=lambda x: x["timestamp"], reverse=True)[:5]
    summary = f"You have {len(customer_orders)} order(s). Here are your recent orders:\n\n"
    
    for idx, order in enumerate(recent_orders, 1):
        order_date = datetime.fromisoformat(order['timestamp']).strftime('%B %d, %Y')
        summary += f"{idx}. Order ID: {order['order_id']}\n"
        summary += f"   Date: {order_date}\n"
        summary += f"   Status: {order['status'].replace('_', ' ').title()}\n"
        summary += f"   Total: ₹{order['total']}\n"
        
        # Build items list
        items_list = [f"{item['quantity']}x {item['name']}" for item in order['items'][:3]]
        summary += f"   Items: {', '.join(items_list)}"
        if len(order['items']) > 3:
            summary += f" and {len(order['items']) - 3} more"
        summary += "\n\n"
    
    summary += "To reorder any of these, just say 'reorder my last order' or 'reorder order number 2' or provide the Order ID."
    return summary

@function_tool
async def show_last_order(ctx: RunContext[Userdata]) -> str:
    """Show details of the most recent order without needing Order ID."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    # Get customer's orders
    customer_orders = [order for order in agent.orders.values() 
                     if order["customer_email"] == agent.current_user]
    
    if not customer_orders:
        return "You don't have any previous orders yet. Start shopping to place your first order!"
    
    # Get the most recent order
    last_order = sorted(customer_orders, key=lambda x: x["timestamp"], reverse=True)[0]
    
    # Format order details
    order_date = datetime.fromisoformat(last_order['timestamp']).strftime('%B %d, %Y at %I:%M %p')
    
    summary = "Here's your last order:\n\n"
    summary += f"Order ID: {last_order['order_id']}\n"
    summary += f"Date: {order_date}\n"
    summary += f"Status: {last_order['status'].replace('_', ' ').title()}\n"
    summary += f"Delivery Address: {last_order['delivery_address']}\n\n"
    
    summary += "Items:\n"
    for item in last_order['items']:
        item_total = item['quantity'] * item['price']
        summary += f"- {item['quantity']}x {item['name']} (₹{item['price']} each) = ₹{item_total}\n"
    
    summary += f"\nTotal: ₹{last_order['total']}"
    summary += f"\n\nWould you like to reorder this? Just say 'reorder my last order'."
    
    return summary

@function_tool
async def reorder_last_order(ctx: RunContext[Userdata]) -> str:
    """Reorder items from the most recent order without needing Order ID."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    # Get customer's orders
    customer_orders = [order for order in agent.orders.values() 
                     if order["customer_email"] == agent.current_user]
    
    if not customer_orders:
        return "You don't have any previous orders to reorder. Start shopping to place your first order!"
    
    # Get the most recent order
    last_order = sorted(customer_orders, key=lambda x: x["timestamp"], reverse=True)[0]
    
    # Add all items from last order to current cart
    added_items = []
    total_cost = 0
    
    for item in last_order["items"]:
        # Check if item already in cart
        found = False
        for cart_item in agent.cart:
            if cart_item["id"] == item["id"]:
                cart_item["quantity"] += item["quantity"]
                found = True
                break
        
        if not found:
            agent.cart.append(item.copy())
        
        added_items.append(f"{item['quantity']}x {item['name']}")
        total_cost += item["quantity"] * item["price"]
    
    order_date = datetime.fromisoformat(last_order['timestamp']).strftime('%B %d, %Y')
    return f"Great! I've added items from your last order ({last_order['order_id']} placed on {order_date}) to your cart: {', '.join(added_items)}. Total added: ₹{total_cost}. Say 'show cart' to review."

@function_tool
async def reorder_previous_order(
    ctx: RunContext[Userdata],
    order_id: Annotated[str, Field(description="Order ID to reorder")]
) -> str:
    """Reorder items from a specific previous order by Order ID."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    if order_id not in agent.orders:
        # Try to find by partial match or order number
        customer_orders = [order for order in agent.orders.values() 
                         if order["customer_email"] == agent.current_user]
        if not customer_orders:
            return "You don't have any previous orders."
        
        return f"I couldn't find order {order_id}. Please say 'show my orders' to see your order history."
    
    order = agent.orders[order_id]
    if order["customer_email"] != agent.current_user:
        return "Order not found or doesn't belong to you."
    
    # Add all items from previous order to current cart
    added_items = []
    total_cost = 0
    
    for item in order["items"]:
        # Check if item already in cart
        found = False
        for cart_item in agent.cart:
            if cart_item["id"] == item["id"]:
                cart_item["quantity"] += item["quantity"]
                found = True
                break
        
        if not found:
            agent.cart.append(item.copy())
        
        added_items.append(f"{item['quantity']}x {item['name']}")
        total_cost += item["quantity"] * item["price"]
    
    order_date = datetime.fromisoformat(order['timestamp']).strftime('%B %d, %Y')
    return f"Perfect! I've added items from order {order_id} (placed on {order_date}) to your cart: {', '.join(added_items)}. Total added: ₹{total_cost}. Say 'show cart' to review."

@function_tool
async def check_order_status(
    ctx: RunContext[Userdata],
    order_id: Annotated[str, Field(description="Order ID to check")]
) -> str:
    """Check the status of a specific order by order ID."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    if order_id in agent.orders:
        order = agent.orders[order_id]
        if order["customer_email"] == agent.current_user:
            return f"Order {order_id}: Status is '{order['status']}'. Total: ₹{order['total']}"
        else:
            return "Order not found or doesn't belong to you."
    else:
        return f"Order {order_id} not found."

@function_tool
async def set_budget_limit(
    ctx: RunContext[Userdata],
    budget: Annotated[int, Field(description="Budget limit in rupees")]
) -> str:
    """Set budget limit for shopping."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    agent.budget_limit = budget
    return f"Budget limit set to ₹{budget}. I'll help you stay within this limit."

@function_tool
async def set_dietary_filter(
    ctx: RunContext[Userdata],
    filter_type: Annotated[str, Field(description="Dietary filter: vegan, vegetarian, gluten-free, or none")]
) -> str:
    """Set dietary filter for shopping."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    if filter_type.lower() == "none":
        agent.dietary_filter = None
        return "Dietary filter removed. All items are now available."
    else:
        agent.dietary_filter = filter_type.lower()
        return f"Dietary filter set to {filter_type}. I'll only suggest {filter_type} items."

@function_tool
async def get_recommendations(
    ctx: RunContext[Userdata]
) -> str:
    """Get personalized recommendations based on order history."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    frequent_items = agent.get_frequent_items()
    if not frequent_items:
        return "You don't have enough order history for recommendations yet. Try browsing our catalog!"
    
    recommendations = "Based on your order history, you might like:\n"
    for item in frequent_items:
        recommendations += f"• {item['name']} - ₹{item['price']} ({item['brand']})\n"
    
    recommendations += "\nWould you like to add any of these to your cart?"
    return recommendations

@function_tool
async def check_delivery_charges(ctx: RunContext[Userdata]) -> str:
    """Check delivery charges for current cart."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    if not agent.cart:
        return "Your cart is empty. Add items to check delivery charges."
    
    pricing = agent.calculate_order_total()
    
    if pricing['delivery_charge'] == 0:
        return f"Great news! Your order qualifies for FREE delivery as it's above ₹{agent.FREE_DELIVERY_THRESHOLD}. Current subtotal: ₹{pricing['subtotal']}"
    else:
        remaining = agent.FREE_DELIVERY_THRESHOLD - pricing['subtotal']
        return f"Delivery charge is ₹{pricing['delivery_charge']}. Add items worth ₹{remaining} more to get FREE delivery! Current subtotal: ₹{pricing['subtotal']}"

@function_tool
async def check_discount_eligibility(ctx: RunContext[Userdata]) -> str:
    """Check if order is eligible for discount."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    if not agent.cart:
        return "Your cart is empty. Add items to check discount eligibility."
    
    pricing = agent.calculate_order_total()
    
    if pricing['discount'] > 0:
        return f"Congratulations! You're getting a {agent.DISCOUNT_PERCENTAGE}% discount of ₹{pricing['discount']} on your order of ₹{pricing['subtotal']}. Discounts are available on orders above ₹{agent.DISCOUNT_THRESHOLD} and during festival seasons!"
    else:
        remaining = agent.DISCOUNT_THRESHOLD - pricing['subtotal']
        return f"Currently, discounts are available only during festival seasons and on orders above ₹{agent.DISCOUNT_THRESHOLD}. Add items worth ₹{remaining} more to qualify for {agent.DISCOUNT_PERCENTAGE}% discount! Current subtotal: ₹{pricing['subtotal']}"

@function_tool
async def advance_order_status(
    ctx: RunContext[Userdata],
    order_id: Annotated[str, Field(description="Order ID to advance status")]
) -> str:
    """Advance order status to next stage (for testing)."""
    agent = ctx.userdata.agent
    if not agent.current_user:
        return "Please log in first."
    
    if agent.update_order_status(order_id):
        order = agent.orders[order_id]
        return f"Order {order_id} status updated to: {order['status']}"
    else:
        return f"Could not advance status for order {order_id}"

@function_tool
async def confirm_order(
    ctx: RunContext[Userdata],
    confirmation: Annotated[str, Field(description="Customer's confirmation response (yes/no)")]
) -> str:
    """Confirm and place the order after customer approval."""
    agent = ctx.userdata.agent
    if not agent.current_user or not agent.pending_order:
        return "No pending order to confirm. Please review your order first."
    
    confirmation_lower = confirmation.lower()
    
    if "yes" in confirmation_lower or "confirm" in confirmation_lower or "correct" in confirmation_lower:
        # Confirm the order
        order = agent.pending_order
        order["status"] = "received"
        order["last_updated"] = datetime.now().isoformat()
        
        # Save order
        agent.orders[order["order_id"]] = order
        agent.save_orders()
        
        # Send confirmation email
        email_sent = agent.send_confirmation_email(order)
        
        # Clear cart and pending order
        agent.cart = []
        agent.pending_order = None
        
        email_msg = " A confirmation email has been sent to your registered email address." if email_sent else ""
        
        return f"Order confirmed successfully! Order ID: {order['order_id']}. Total: ₹{order['total']}. We'll deliver to {order['delivery_address']}.{email_msg} Thank you for choosing DailyMart!"
    
    elif "no" in confirmation_lower or "change" in confirmation_lower or "incorrect" in confirmation_lower:
        agent.pending_order = None
        return "Order cancelled. You can continue shopping and modify your cart, or update your profile details if needed."
    
    else:
        return "Please say 'yes' to confirm your order or 'no' to make changes."

class DailyMartVoiceAgent(Agent):
    def __init__(self):
        super().__init__(
            instructions="""
            You are a friendly DailyMart grocery ordering assistant. ONLY speak in English.
            
            GREETING: Always start with a warm introduction:
            "Hello! Welcome to DailyMart, your friendly neighborhood grocery store. I can help you order groceries, spices, snacks, and prepared foods. Are you a new customer or do you already have an account with us?"
            
            IMPORTANT: Only use customer's name ONCE after login/registration. Don't repeat their name in every response.
            
            CUSTOMER FLOW:
            - For new: collect name, email, password, address, mobile for registration
            - For existing: ask email and password to log in
            
            PASSWORD HANDLING:
            - Accept spoken numbers like "two two three three" as "2233"
            - Be flexible with password input
            
            ORDER HISTORY & REORDERING:
            - When user asks "show my previous orders" or "show my orders" - use show_order_history() function
            - When user asks "show my last order" or "what was my last order" - use show_last_order() function (NO ORDER ID NEEDED)
            - When user says "reorder my last order" or "order again" or "same order" - use reorder_last_order() function (NO ORDER ID NEEDED)
            - When user provides specific Order ID like "reorder ORD_123" - use reorder_previous_order() function
            - If user says "reorder" without specifying, ALWAYS use reorder_last_order() first
            - When user asks "where is my order" or order status - use check_order_status() function
            - When user asks for recommendations - use get_recommendations() function
            - NEVER ask for Order ID when user says "show last order" or "reorder" - handle it automatically
            
            BUDGET & DIETARY:
            - When user sets budget limit like "keep it under 1000" - use set_budget_limit() function
            - When user wants dietary filter like "only vegan items" - use set_dietary_filter() function
            - Always check budget and dietary constraints when adding items
            
            DELIVERY CHARGES & DISCOUNTS:
            - When user asks about delivery charges - use check_delivery_charges() function
            - Delivery is ₹50, but FREE on orders above ₹1000
            - When user asks about discounts - use check_discount_eligibility() function
            - Discounts are available ONLY during festival seasons AND on orders above ₹5000 (10% off)
            - Always mention both conditions: festival season + order value
            - The view_cart and review_order_details functions automatically show delivery and discount
            
            Once logged in, help with:
            - Browse catalog (use show_catalog function)
            - Add/remove items from cart
            - Handle 'ingredients for X' requests for Indian recipes
            - Cart management (view, update quantities, remove items)
            - Order history and reordering
            - Check delivery charges and discount eligibility
            
            Available categories: Groceries, Spices & Masalas, Snacks & Namkeen, Ready to Eat, Beverages, Sweets & Desserts.
            All prices in Indian Rupees. Always confirm actions clearly but don't overuse customer's name.
            """,
            tools=[
                register_new_customer,
                login_customer,
                reset_password,
                set_budget_limit,
                set_dietary_filter,
                show_catalog,
                add_item_to_cart,
                add_recipe_ingredients,
                remove_item_from_cart,
                update_item_quantity,
                view_cart,
                review_order_details,
                confirm_order,
                show_order_history,
                show_last_order,
                check_order_status,
                reorder_last_order,
                reorder_previous_order,
                get_recommendations,
                check_delivery_charges,
                check_discount_eligibility,
                advance_order_status,
            ],
        )

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    # Create user session data with agent
    userdata = Userdata(agent=DailyMartAgent())
    
    session = AgentSession(
        stt=deepgram.STT(model="nova-3"),
        llm=google.LLM(model="gemini-2.5-flash"),
        tts=murf.TTS(
            voice="en-IN-anusha",
            style="Conversation",
            text_pacing=True,
        ),
        vad=ctx.proc.userdata["vad"],
        userdata=userdata,
    )

    await session.start(
        agent=DailyMartVoiceAgent(),
        room=ctx.room,
    )

    await ctx.connect()
    
    # Give initial greeting
    await asyncio.sleep(1)
    await session.agent_publication.say(
        "Hello! Welcome to DailyMart, your friendly neighborhood grocery store. I can help you order groceries, spices, snacks, and prepared foods. Are you a new customer or do you already have an account with us?",
        allow_interruptions=True
    )

if __name__ == "__main__":
    cli.run_app(WorkerOptions(entrypoint_fnc=entrypoint, prewarm_fnc=prewarm))