"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/livekit/button";
import { LoginScreen } from "./login-screen";

interface Product {
  id: string;
  name: string;
  price: number;
  currency: string;
  category: string;
  description: string;
  color?: string;
  size?: string;
}

interface CartItem extends Product {
  quantity: number;
}

interface NotificationItem {
  id: string;
  message: string;
  type: 'success' | 'info' | 'error';
}

export function ProductGrid() {
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [user, setUser] = useState<any>(null);
  const [showAuth, setShowAuth] = useState(false);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);

  useEffect(() => {
    checkAuthStatus();
    const interval = setInterval(checkAuthStatus, 2000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (user) {
      fetchProducts();
    } else {
      setLoading(false);
    }
  }, [user]);

  const checkAuthStatus = async () => {
    try {
      const response = await fetch('/api/auth');
      const data = await response.json();
      if (data.success && data.user) {
        setUser(data.user);
        setShowAuth(false);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    }
  };

  const fetchProducts = async () => {
    try {
      setLoading(true);
      const response = await fetch('http://localhost:8000/acp/catalog');
      const data = await response.json();
      setProducts(data.products || []);
      showNotification('✅ Catalog loaded successfully!', 'success');
    } catch (error) {
      console.error('Failed to fetch products:', error);
      // Fallback to sample data
      setProducts([
        { id: "mug-001", name: "☕ Stoneware Coffee Mug", price: 800, currency: "INR", category: "beverages", description: "Premium ceramic coffee mug" },
        { id: "tshirt-001", name: "👕 Cotton T-Shirt", price: 1200, currency: "INR", category: "clothing", description: "100% cotton casual t-shirt" },
        { id: "hoodie-001", name: "🧥 Black Hoodie", price: 2500, currency: "INR", category: "clothing", description: "Comfortable cotton hoodie" },
        { id: "book-001", name: "📚 JavaScript Guide", price: 599, currency: "INR", category: "books", description: "Complete JavaScript learning guide" },
        { id: "backpack-001", name: "🎒 Travel Backpack", price: 3999, currency: "INR", category: "bags", description: "Durable travel backpack" },
      ]);
      showNotification('ℹ️ Using sample catalog', 'info');
    } finally {
      setLoading(false);
    }
  };

  const showNotification = (message: string, type: 'success' | 'info' | 'error' = 'info') => {
    const id = Date.now().toString();
    setNotifications(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setNotifications(prev => prev.filter(n => n.id !== id));
    }, 4000);
  };

  const addToCart = (product: Product) => {
    if (!user) {
      setShowAuth(true);
      showNotification('❌ Please login first to add items to cart', 'error');
      return;
    }

    setCart(prev => {
      const existing = prev.find(item => item.id === product.id);
      if (existing) {
        return prev.map(item => 
          item.id === product.id 
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...prev, { ...product, quantity: 1 }];
    });

    showNotification(`✅ Added "${product.name}" to cart!`, 'success');

    // Notify agent
    try {
      fetch('http://localhost:8000/webhook/cart-update', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user: user.email,
          product: product.name,
          action: 'add_to_cart',
          timestamp: new Date().toISOString(),
        }),
      }).catch(() => {});
    } catch (error) {
      console.error('Failed to notify agent:', error);
    }
  };

  const removeFromCart = (productId: string) => {
    const product = cart.find(item => item.id === productId);
    setCart(prev => prev.filter(item => item.id !== productId));
    if (product) {
      showNotification(`🗑️ Removed "${product.name}"`, 'info');
    }
  };

  const updateQuantity = (productId: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }
    setCart(prev => 
      prev.map(item => 
        item.id === productId 
          ? { ...item, quantity: newQuantity }
          : item
      )
    );
  };

  const buyNow = async (product: Product) => {
    if (!user) {
      setShowAuth(true);
      showNotification('❌ Please login first', 'error');
      return;
    }
    
    try {
      const response = await fetch('http://localhost:8000/acp/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          line_items: [{ product_id: product.id, quantity: 1 }],
          buyer_info: {
            name: user.name || 'User',
            email: user.email,
          }
        })
      });
      
      if (response.ok) {
        const order = await response.json();
        showNotification(`📦 Order placed! ID: ${order.order?.id || 'Processing'}`, 'success');

        // Notify agent
        try {
          fetch('http://localhost:8000/webhook/purchase', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              user: user.email,
              product: product.name,
              timestamp: new Date().toISOString(),
            }),
          }).catch(() => {});
        } catch (error) {
          console.error('Failed to notify agent:', error);
        }
      } else {
        showNotification('❌ Failed to place order', 'error');
      }
    } catch (error) {
      console.error('Failed to place order:', error);
      showNotification('❌ Order error', 'error');
    }
  };

  const getTotalItems = () => cart.reduce((sum, item) => sum + item.quantity, 0);
  const getTotalPrice = () => cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  // Show login screen if not authenticated
  if (!user) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50 p-6">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-2">🛍️ E-commerce Marketplace</h1>
            <p className="text-gray-600 text-lg">Login or register to browse products and shop</p>
          </div>

          <LoginScreen
            onLoginSuccess={(user) => {
              setUser(user);
              showNotification(`✅ Welcome, ${user.name}! Now browse our catalog.`, 'success');
            }}
            onCancel={() => {
              showNotification('Please login to continue shopping', 'info');
            }}
          />
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="p-6 max-w-6xl mx-auto">
        <div className="text-center py-20">
          <div className="inline-block animate-spin mb-4">
            <span className="text-4xl">⏳</span>
          </div>
          <p className="text-gray-600 text-lg">Loading products...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-6xl mx-auto">
      {/* Notifications */}
      <div className="fixed top-6 right-6 z-50 space-y-2">
        {notifications.map((notif) => (
          <div
            key={notif.id}
            className={`p-4 rounded-lg shadow-lg animate-slideIn ${
              notif.type === 'success'
                ? 'bg-green-100 border border-green-300 text-green-800'
                : notif.type === 'error'
                ? 'bg-red-100 border border-red-300 text-red-800'
                : 'bg-blue-100 border border-blue-300 text-blue-800'
            }`}
          >
            {notif.message}
          </div>
        ))}
      </div>

      {/* Header */}
      <div className="flex justify-between items-center mb-8 p-4 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl shadow-lg">
        <div className="text-white">
          <h1 className="text-3xl font-bold">🛍️ E-commerce Store</h1>
          <p className="text-blue-100">Welcome, {user.name}!</p>
        </div>
        <div className="text-right">
          <div className="bg-white bg-opacity-20 backdrop-blur px-4 py-2 rounded-lg text-white font-semibold">
            🛒 Cart: {getTotalItems()} items | ₹{getTotalPrice()}
          </div>
        </div>
      </div>

      {/* Products Grid */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">Available Products</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {products.map((product) => (
          <div
            key={product.id}
            className="border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-lg transition-shadow duration-300 bg-white"
          >
            <div className="p-6">
              <div className="text-center mb-4">
                <span className="text-5xl">{product.name.charAt(0)}</span>
              </div>
              <h3 className="font-semibold text-lg text-gray-900">{product.name}</h3>
              <p className="text-gray-600 text-sm mb-4">{product.description}</p>
              <div className="flex justify-between items-center mb-4">
                <span className="text-2xl font-bold text-green-600">₹{product.price}</span>
                <span className="text-xs bg-gray-100 px-3 py-1 rounded-full text-gray-700">
                  {product.category}
                </span>
              </div>
              {product.color && (
                <p className="text-sm text-gray-500 mb-2">Color: {product.color}</p>
              )}
              {product.size && (
                <p className="text-sm text-gray-500 mb-4">Size: {product.size}</p>
              )}

              <div className="flex gap-2">
                <Button
                  onClick={() => addToCart(product)}
                  variant="outline"
                  className="flex-1 border-blue-600 text-blue-600 hover:bg-blue-50"
                >
                  Add to Cart
                </Button>
                <Button
                  onClick={() => buyNow(product)}
                  className="flex-1 bg-blue-600 hover:bg-blue-700 text-white"
                >
                  Buy Now
                </Button>
              </div>
            </div>
          </div>
        ))}
      </div>
      </div>

      {/* Shopping Cart */}
      {cart.length > 0 && (
        <div className="bg-white rounded-lg shadow-lg border border-gray-200 p-6">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">🛒 Shopping Cart ({getTotalItems()} items)</h2>
          <div className="space-y-4 mb-6">
            {cart.map((item) => (
              <div key={item.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900">{item.name}</h3>
                  <p className="text-sm text-gray-600">₹{item.price} each</p>
                </div>
                <div className="flex items-center gap-3">
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity - 1)}
                      className="w-8 h-8 rounded-full bg-gray-300 hover:bg-gray-400 flex items-center justify-center font-bold text-sm"
                    >
                      −
                    </button>
                    <span className="w-8 text-center font-semibold">{item.quantity}</span>
                    <button
                      onClick={() => updateQuantity(item.id, item.quantity + 1)}
                      className="w-8 h-8 rounded-full bg-gray-300 hover:bg-gray-400 flex items-center justify-center font-bold text-sm"
                    >
                      +
                    </button>
                  </div>
                  <div className="text-right min-w-[100px]">
                    <div className="font-semibold text-gray-900">₹{item.price * item.quantity}</div>
                    <button
                      onClick={() => removeFromCart(item.id)}
                      className="text-xs text-red-600 hover:text-red-800 font-semibold"
                    >
                      Remove
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="border-t pt-6">
            <div className="space-y-2 mb-6 text-right">
              <div className="flex justify-end gap-8">
                <span className="text-gray-600">Subtotal:</span>
                <span className="font-semibold">₹{getTotalPrice()}</span>
              </div>
              <div className="flex justify-end gap-8">
                <span className="text-gray-600">Tax (5%):</span>
                <span className="font-semibold">₹{Math.round(getTotalPrice() * 0.05)}</span>
              </div>
              <div className="flex justify-end gap-8 text-xl">
                <span className="font-bold text-gray-900">Total:</span>
                <span className="font-bold text-green-600">₹{Math.round(getTotalPrice() * 1.05)}</span>
              </div>
            </div>

            <Button
              onClick={() => {
                showNotification('🎉 Checkout initiated! Processing your order...', 'success');
                // Checkout logic here
              }}
              className="w-full bg-green-600 hover:bg-green-700 text-white font-semibold py-3 rounded-lg text-lg"
            >
              ✅ Checkout
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}