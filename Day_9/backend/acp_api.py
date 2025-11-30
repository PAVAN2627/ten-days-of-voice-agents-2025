"""
Type-Safe ACP API Layer
FastAPI with Pydantic models for request/response validation
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from datetime import datetime
from pydantic import ValidationError
import logging

from acp_models import (
    Product, Order, OrderCreateRequest, ProductFilter,
    CatalogResponse, OrderResponse, ErrorResponse, OrderStatus, CartItem
)
from acp_commerce import (
    list_products, get_product_by_id, create_order, get_order,
    get_recent_orders, get_categories, search_products,
    get_orders_by_user, get_orders_by_status,
    calculate_user_spending, get_spending_by_category,
    update_order_status, get_cart, save_cart, clear_cart
)

# Initialize FastAPI app
app = FastAPI(
    title="Type-Safe E-commerce ACP API",
    description="ACP-compliant E-commerce API with full type safety",
    version="2.0.0"
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

@app.get("/acp/catalog", response_model=CatalogResponse)
async def get_catalog(
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    max_price: Optional[float] = Query(None),
    min_price: Optional[float] = Query(None),
    limit: Optional[int] = Query(100)
):
    """Get product catalog with optional filters - Type-safe"""
    try:
        filters = ProductFilter(
            category=category,
            search=search,
            max_price=max_price,
            min_price=min_price
        )
        
        products = list_products(filters)
        
        return CatalogResponse(
            success=True,
            count=len(products),
            products=products[:limit]
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/acp/products/{product_id}", response_model=Product)
async def get_product(product_id: str):
    """Get a specific product by ID - Type-safe"""
    try:
        product = get_product_by_id(product_id)
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/acp/products/search", response_model=CatalogResponse)
async def search_catalog(q: str = Query(...)):
    """Search products by name or description - Type-safe"""
    try:
        products = search_products(q)
        return CatalogResponse(
            success=True,
            count=len(products),
            products=products
        )
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

@app.post("/acp/orders", response_model=OrderResponse)
async def create_new_order(request: OrderCreateRequest):
    """Create a new order - Type-safe with validation"""
    try:
        order = create_order(request)
        
        return OrderResponse(
            success=True,
            message="Order created successfully",
            order=order
        )
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(status_code=422, detail=e.errors())
    except ValueError as e:
        logger.error(f"Business logic error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/acp/orders/{order_id}", response_model=Order)
async def get_order_details(order_id: str):
    """Get order details by ID - Type-safe"""
    try:
        order = get_order(order_id)
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/acp/orders")
async def get_all_orders(limit: Optional[int] = Query(50)):
    """Get recent orders"""
    try:
        orders = get_recent_orders(limit)
        # Convert to dicts for JSON serialization
        orders_data = [order.model_dump() for order in orders]
        return {
            "success": True,
            "count": len(orders),
            "orders": orders_data
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== USER ORDER ENDPOINTS ====================

@app.get("/acp/users/{email}/orders")
async def get_user_orders(email: str):
    """Get all orders for a specific user - Type-safe"""
    try:
        orders = get_orders_by_user(email)
        orders_data = [order.model_dump() for order in orders]
        return {
            "success": True,
            "email": email,
            "count": len(orders),
            "orders": orders_data
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
    """Get orders by status - Type-safe"""
    try:
        # Validate status
        order_status = OrderStatus(status.upper())
        orders = get_orders_by_status(order_status)
        orders_data = [order.model_dump() for order in orders]
        
        return {
            "success": True,
            "status": status,
            "count": len(orders),
            "orders": orders_data
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {[s.value for s in OrderStatus]}"
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/acp/orders/{order_id}/status")
async def update_status(order_id: str, status_data: dict):
    """Update order status - Type-safe"""
    try:
        new_status_str = status_data.get('status')
        if not new_status_str:
            raise ValueError("Status is required")
        
        # Validate status
        new_status = OrderStatus(new_status_str.upper())
        
        success = update_order_status(order_id, new_status)
        if not success:
            raise HTTPException(status_code=404, detail="Order not found")
        
        updated_order = get_order(order_id)
        return {
            "success": True,
            "message": "Order status updated",
            "order": updated_order.model_dump() if updated_order else None
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# ==================== CART ENDPOINTS ====================

@app.get("/acp/users/{email}/cart")
async def get_user_cart(email: str):
    """Get saved cart for a user - Type-safe"""
    try:
        cart = get_cart(email)
        cart_data = [item.model_dump() for item in cart]
        return {
            "success": True,
            "email": email,
            "cart": cart_data,
            "item_count": len(cart)
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/acp/users/{email}/cart")
async def save_user_cart(email: str, cart_data: dict):
    """Save cart for a user - Type-safe"""
    try:
        cart_items_data = cart_data.get('cart', [])
        
        # Validate cart items
        cart_items = []
        for item_data in cart_items_data:
            cart_item = CartItem(**item_data)
            cart_items.append(cart_item)
        
        save_cart(email, cart_items)
        
        return {
            "success": True,
            "message": "Cart saved successfully",
            "email": email,
            "item_count": len(cart_items)
        }
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())
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
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "type_safe": True
    }


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Type-Safe E-commerce ACP API",
        "version": "2.0.0",
        "type_safe": True,
        "docs": "/docs",
        "openapi": "/openapi.json"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
