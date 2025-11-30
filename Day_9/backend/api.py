"""
FastAPI Backend for E-commerce Agent
Implements ACP-inspired REST API endpoints
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from datetime import datetime
import logging

from commerce import (
    list_products,
    create_order,
    get_order,
    get_recent_orders,
    get_categories,
    search_products,
    get_product_by_id,
    get_orders_by_user,
    get_orders_by_date_range,
    get_orders_by_status,
    calculate_user_spending,
    get_spending_by_category,
    update_order_status,
    get_cart,
    save_cart,
    clear_cart
)

# Initialize FastAPI app
app = FastAPI(
    title="E-commerce Agent API",
    description="ACP-inspired E-commerce API",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ==================== CATALOG ENDPOINTS ====================

@app.get("/acp/catalog")
async def get_catalog(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    max_price: Optional[int] = Query(None),
    limit: Optional[int] = Query(100)
):
    """Get product catalog with optional filters"""
    try:
        filters = {}
        if category:
            filters['category'] = category
        if search:
            filters['search'] = search
        if max_price:
            filters['max_price'] = max_price
        
        products = list_products(filters)
        return {
            "success": True,
            "count": len(products),
            "products": products[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/acp/products/{product_id}")
async def get_product(product_id: str):
    """Get a specific product by ID"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return {
            "success": True,
            "product": product
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/acp/products/search")
async def search_catalog(q: str = Query(...)):
    """Search products by name or description"""
    try:
        products = search_products(q)
        return {
            "success": True,
            "query": q,
            "count": len(products),
            "products": products
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/acp/categories")
async def get_all_categories():
    """Get all product categories"""
    try:
        categories = get_categories()
        return {
            "success": True,
            "categories": categories
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== ORDER ENDPOINTS ====================

@app.post("/acp/orders")
async def create_new_order(order_data: Dict[str, Any]):
    """Create a new order"""
    try:
        line_items = order_data.get('line_items', [])
        buyer_info = order_data.get('buyer_info', {})
        
        if not line_items:
            raise ValueError("Cart cannot be empty")
        
        order = create_order(line_items, buyer_info)
        
        return {
            "success": True,
            "message": "Order created successfully",
            "order": order
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/acp/orders/{order_id}")
async def get_order_details(order_id: str):
    """Get order details by ID"""
    try:
        order = get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        return {
            "success": True,
            "order": order
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/acp/orders")
async def get_all_orders(limit: Optional[int] = Query(50)):
    """Get recent orders"""
    try:
        orders = get_recent_orders(limit)
        return {
            "success": True,
            "count": len(orders),
            "orders": orders
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== USER ORDER ENDPOINTS ====================

@app.get("/acp/users/{email}/orders")
async def get_user_orders(email: str):
    """Get all orders for a specific user"""
    try:
        orders = get_orders_by_user(email)
        return {
            "success": True,
            "email": email,
            "count": len(orders),
            "orders": orders
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/acp/users/{email}/spending")
async def get_user_spending(email: str):
    """Get total spending for a user"""
    try:
        total_spending = calculate_user_spending(email)
        category_spending = get_spending_by_category(email)
        
        return {
            "success": True,
            "email": email,
            "total_spending": total_spending,
            "by_category": category_spending
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/acp/orders/status/{status}")
async def get_orders_by_order_status(status: str):
    """Get orders by status"""
    try:
        orders = get_orders_by_status(status)
        return {
            "success": True,
            "status": status,
            "count": len(orders),
            "orders": orders
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/acp/orders/{order_id}/status")
async def update_status(order_id: str, status_data: Dict[str, str]):
    """Update order status"""
    try:
        new_status = status_data.get('status')
        if not new_status:
            raise ValueError("Status is required")
        
        success = update_order_status(order_id, new_status)
        if not success:
            raise ValueError(f"Invalid status: {new_status}")
        
        updated_order = get_order(order_id)
        return {
            "success": True,
            "message": "Order status updated",
            "order": updated_order
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== CART ENDPOINTS ====================

@app.get("/acp/users/{email}/cart")
async def get_user_cart(email: str):
    """Get saved cart for a user"""
    try:
        cart = get_cart(email)
        return {
            "success": True,
            "email": email,
            "cart": cart,
            "item_count": len(cart)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/acp/users/{email}/cart")
async def save_user_cart(email: str, cart_data: Dict[str, Any]):
    """Save cart for a user"""
    try:
        cart = cart_data.get('cart', [])
        save_cart(email, cart)
        
        return {
            "success": True,
            "message": "Cart saved successfully",
            "email": email,
            "item_count": len(cart)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.delete("/acp/users/{email}/cart")
async def delete_user_cart(email: str):
    """Clear cart for a user"""
    try:
        clear_cart(email)
        return {
            "success": True,
            "message": "Cart cleared"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== HEALTH CHECK ====================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "E-commerce Agent API",
        "version": "1.0.0",
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
