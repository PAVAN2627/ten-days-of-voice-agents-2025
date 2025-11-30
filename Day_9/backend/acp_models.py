"""
Type-Safe ACP (Agentic Commerce Protocol) Models
Using Pydantic for runtime validation and type safety
"""

from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    """Valid order statuses"""
    PENDING = "PENDING"
    CONFIRMED = "CONFIRMED"
    SHIPPED = "SHIPPED"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Product(BaseModel):
    """Type-safe product model"""
    id: str = Field(..., description="Unique product identifier")
    name: str = Field(..., min_length=1, description="Product name")
    price: float = Field(..., gt=0, description="Product price (must be positive)")
    currency: str = Field(default="INR", description="Currency code")
    category: str = Field(..., description="Product category")
    description: str = Field(default="", description="Product description")
    color: Optional[str] = Field(None, description="Product color")
    size: Optional[str] = Field(None, description="Product size")
    stock: int = Field(default=100, ge=0, description="Available stock")
    image_url: Optional[str] = Field(None, description="Product image URL")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "mug-001",
                "name": "Stoneware Coffee Mug",
                "price": 800,
                "currency": "INR",
                "category": "mug",
                "description": "Handcrafted stoneware mug",
                "stock": 50
            }
        }


class LineItem(BaseModel):
    """Type-safe line item model"""
    product_id: str = Field(..., description="Product identifier")
    name: str = Field(..., description="Product name")
    quantity: int = Field(..., gt=0, description="Quantity (must be positive)")
    unit_amount: float = Field(..., gt=0, description="Price per unit")
    currency: str = Field(default="INR", description="Currency code")
    line_total: float = Field(..., ge=0, description="Total for this line")
    
    @validator('line_total')
    def validate_line_total(cls, v, values):
        """Ensure line_total matches quantity * unit_amount"""
        if 'quantity' in values and 'unit_amount' in values:
            expected = values['quantity'] * values['unit_amount']
            if abs(v - expected) > 0.01:  # Allow small floating point differences
                raise ValueError(f"line_total {v} doesn't match quantity * unit_amount = {expected}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "mug-001",
                "name": "Stoneware Coffee Mug",
                "quantity": 2,
                "unit_amount": 800,
                "currency": "INR",
                "line_total": 1600
            }
        }


class Buyer(BaseModel):
    """Type-safe buyer information model"""
    name: str = Field(..., min_length=1, description="Buyer name")
    email: EmailStr = Field(..., description="Buyer email address")
    phone: str = Field(default="N/A", description="Phone number")
    address: str = Field(default="N/A", description="Delivery address")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+91-9876543210",
                "address": "123 Main St, Mumbai"
            }
        }


class Order(BaseModel):
    """Type-safe order model"""
    id: str = Field(..., description="Unique order identifier")
    buyer: Buyer = Field(..., description="Buyer information")
    line_items: List[LineItem] = Field(..., min_length=1, description="Order items")
    total_amount: float = Field(..., ge=0, description="Total order amount")
    currency: str = Field(default="INR", description="Currency code")
    status: OrderStatus = Field(default=OrderStatus.PENDING, description="Order status")
    created_at: datetime = Field(default_factory=datetime.now, description="Creation timestamp")
    updated_at: datetime = Field(default_factory=datetime.now, description="Last update timestamp")
    
    @validator('total_amount')
    def validate_total_amount(cls, v, values):
        """Ensure total_amount matches sum of line_items"""
        if 'line_items' in values:
            expected = sum(item.line_total for item in values['line_items'])
            if abs(v - expected) > 0.01:
                raise ValueError(f"total_amount {v} doesn't match sum of line items = {expected}")
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "ORD_20241130_123456_abc123",
                "buyer": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+91-9876543210",
                    "address": "123 Main St, Mumbai"
                },
                "line_items": [
                    {
                        "product_id": "mug-001",
                        "name": "Stoneware Coffee Mug",
                        "quantity": 2,
                        "unit_amount": 800,
                        "currency": "INR",
                        "line_total": 1600
                    }
                ],
                "total_amount": 1600,
                "currency": "INR",
                "status": "PENDING"
            }
        }


class CartItem(BaseModel):
    """Type-safe cart item model"""
    product_id: str = Field(..., description="Product identifier")
    quantity: int = Field(..., gt=0, description="Quantity (must be positive)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "product_id": "mug-001",
                "quantity": 2
            }
        }


class OrderCreateRequest(BaseModel):
    """Type-safe order creation request"""
    line_items: List[CartItem] = Field(..., min_length=1, description="Items to order")
    buyer_info: Optional[Buyer] = Field(None, description="Buyer information")
    
    class Config:
        json_schema_extra = {
            "example": {
                "line_items": [
                    {"product_id": "mug-001", "quantity": 2},
                    {"product_id": "tshirt-001", "quantity": 1}
                ],
                "buyer_info": {
                    "name": "John Doe",
                    "email": "john@example.com",
                    "phone": "+91-9876543210",
                    "address": "123 Main St, Mumbai"
                }
            }
        }


class ProductFilter(BaseModel):
    """Type-safe product filter model"""
    category: Optional[str] = None
    search: Optional[str] = None
    max_price: Optional[float] = Field(None, gt=0)
    min_price: Optional[float] = Field(None, ge=0)
    color: Optional[str] = None
    size: Optional[str] = None
    in_stock: Optional[bool] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "category": "mug",
                "max_price": 1000,
                "in_stock": True
            }
        }


class CatalogResponse(BaseModel):
    """Type-safe catalog response"""
    success: bool = True
    count: int = Field(..., ge=0)
    products: List[Product]
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "count": 2,
                "products": [
                    {
                        "id": "mug-001",
                        "name": "Stoneware Coffee Mug",
                        "price": 800,
                        "currency": "INR",
                        "category": "mug",
                        "description": "Handcrafted stoneware mug"
                    }
                ]
            }
        }


class OrderResponse(BaseModel):
    """Type-safe order response"""
    success: bool = True
    message: str = "Order created successfully"
    order: Order
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Order created successfully",
                "order": {
                    "id": "ORD_20241130_123456_abc123",
                    "total_amount": 1600,
                    "status": "PENDING"
                }
            }
        }


class ErrorResponse(BaseModel):
    """Type-safe error response"""
    success: bool = False
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": False,
                "error": "Product not found",
                "details": {"product_id": "invalid-123"}
            }
        }
