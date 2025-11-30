"use client";

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import type { AppConfig } from '@/app-config';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { PreConnectMessage } from '@/components/app/preconnect-message';
import { TileLayout } from '@/components/app/tile-layout';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { useChatMessages } from '@/hooks/useChatMessages';
import { useConnectionTimeout } from '@/hooks/useConnectionTimout';
import { useDebugMode } from '@/hooks/useDebug';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../livekit/scroll-area/scroll-area';
import { Button } from '@/components/livekit/button';

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';

interface Product {
  id: string;
  name: string;
  price: number;
  currency: string;
  category: string;
  description: string;
  color?: string;
  size?: string;
  image?: string;
}

interface CartItem {
  id: string;
  name: string;
  price: number;
  quantity: number;
  size?: string;
  color?: string;
}

interface UnifiedShoppingViewProps {
  appConfig: AppConfig;
}

export const UnifiedShoppingView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & UnifiedShoppingViewProps) => {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: IN_DEVELOPMENT });

  const messages = useChatMessages();
  const [chatOpen, setChatOpen] = useState(true); // Always show chat
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [categories, setCategories] = useState<string[]>(['all']);
  const [showOrderSuccess, setShowOrderSuccess] = useState(false);
  const [lastOrderId, setLastOrderId] = useState<string>('');
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsVideoInput,
  };

  useEffect(() => {
    // Clear cart on component mount (fresh session)
    setCart([]);
    
    // Clear backend cart as well
    fetch('/api/cart', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ action: 'sync', cart: [] })
    }).catch(err => console.error('Failed to clear cart:', err));
    
    fetchProducts();
    syncCart();
    const cartInterval = setInterval(syncCart, 2000);
    
    // Poll for order placed events
    const orderInterval = setInterval(async () => {
      try {
        const response = await fetch('/api/order-placed');
        const data = await response.json();
        if (data.success && data.order) {
          console.log('Order placed event received:', data.order);
          // Trigger order placed event
          handleOrderPlaced({ detail: data });
        }
      } catch (error) {
        // Ignore polling errors
      }
    }, 1000);
    
    // Listen for order placed event to clear cart and show success
    const handleOrderPlaced = (event: any) => {
      const orderId = event.detail?.order?.id || 'Order placed';
      setCart([]);
      setLastOrderId(orderId);
      setShowOrderSuccess(true);
      // Don't auto-hide - keep showing until user adds new item
    };
    window.addEventListener('orderPlaced', handleOrderPlaced);
    
    return () => {
      clearInterval(cartInterval);
      clearInterval(orderInterval);
      window.removeEventListener('orderPlaced', handleOrderPlaced);
      // Clear cart when leaving
      setCart([]);
    };
  }, []);

  const syncCart = async () => {
    try {
      const response = await fetch('/api/cart');
      const data = await response.json();
      if (data.success && data.cart) {
        // Update cart from backend
        setCart(data.cart);
      }
    } catch (error) {
      console.error('Cart sync failed:', error);
    }
  };

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const fetchProducts = async () => {
    try {
      // Try backend API first
      const response = await fetch('http://localhost:8000/acp/catalog');
      const data = await response.json();
      if (data.success && data.products) {
        setProducts(data.products);
        // Extract unique categories
        const cats = Array.from(new Set(data.products.map((p: Product) => p.category))) as string[];
        setCategories(['all', ...cats]);
      }
    } catch (error) {
      console.error('Failed to fetch products from backend, using fallback:', error);
      // Fallback: Load from local catalog
      try {
        const catalogResponse = await fetch('/catalog.json');
        const catalogData = await catalogResponse.json();
        if (catalogData.products) {
          setProducts(catalogData.products);
          const cats = Array.from(new Set(catalogData.products.map((p: Product) => p.category))) as string[];
          setCategories(['all', ...cats]);
        }
      } catch (fallbackError) {
        console.error('Fallback also failed:', fallbackError);
      }
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (product: Product) => {
    // Hide success message when adding new item
    if (showOrderSuccess) {
      setShowOrderSuccess(false);
    }
    
    // Check if user is authenticated
    try {
      const authResponse = await fetch('/api/auth');
      const authData = await authResponse.json();
      if (!authData.success || !authData.user) {
        alert('Please login first to add items to cart. Use voice commands: "I want to login with email [your-email] and password [your-password]"');
        return;
      }
    } catch (error) {
      alert('Please login first to add items to cart.');
      return;
    }
    
    const newCart = (() => {
      const existing = cart.find(item => item.id === product.id && item.size === product.size);
      if (existing) {
        return cart.map(item => 
          item.id === product.id && item.size === product.size
            ? { ...item, quantity: item.quantity + 1 }
            : item
        );
      }
      return [...cart, { 
        id: product.id,
        name: product.name,
        price: product.price,
        quantity: 1,
        size: product.size,
        color: product.color
      }];
    })();
    
    setCart(newCart);
    
    // Sync to backend
    try {
      await fetch('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'sync', cart: newCart })
      });
    } catch (error) {
      console.error('Failed to sync cart:', error);
    }
  };

  const removeFromCart = async (productId: string) => {
    const newCart = cart.filter(item => item.id !== productId);
    setCart(newCart);
    
    try {
      await fetch('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'sync', cart: newCart })
      });
    } catch (error) {
      console.error('Failed to sync cart:', error);
    }
  };

  const updateQuantity = async (productId: string, newQuantity: number) => {
    if (newQuantity <= 0) {
      removeFromCart(productId);
      return;
    }
    const newCart = cart.map(item => 
      item.id === productId 
        ? { ...item, quantity: newQuantity }
        : item
    );
    setCart(newCart);
    
    try {
      await fetch('/api/cart', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ action: 'sync', cart: newCart })
      });
    } catch (error) {
      console.error('Failed to sync cart:', error);
    }
  };

  const getTotalItems = () => cart.reduce((sum, item) => sum + item.quantity, 0);
  const getTotalPrice = () => cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);

  // Filter products by category
  const filteredProducts = selectedCategory === 'all' 
    ? products 
    : products.filter(p => p.category === selectedCategory);

  return (
    <section className="bg-background relative z-10 h-screen w-full overflow-hidden grid grid-cols-3" {...props}>
      {/* Left Panel - Product Catalog */}
      <div className="border-r bg-gray-50 overflow-y-auto h-screen">
        <div className="p-4 border-b bg-white">
          <h2 className="text-lg font-semibold mb-3">🛍️ Products</h2>
          {/* Category Filter */}
          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-purple-500 focus:border-transparent"
          >
            {categories.map(cat => (
              <option key={cat} value={cat}>
                {cat.charAt(0).toUpperCase() + cat.slice(1)}
              </option>
            ))}
          </select>
        </div>
        <div className="p-4 space-y-3">
          {loading ? (
            <div className="text-center text-gray-500">Loading products...</div>
          ) : filteredProducts.length === 0 ? (
            <div className="text-center text-gray-500">No products found</div>
          ) : (
            filteredProducts.map((product) => (
              <div key={product.id} className="bg-white rounded-lg shadow-sm border overflow-hidden hover:shadow-md transition-shadow">
                {/* Product Image */}
                {product.image && (
                  <div className="h-32 overflow-hidden bg-gray-100">
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                    />
                  </div>
                )}
                
                {/* Product Info */}
                <div className="p-3">
                  <div className="flex justify-between items-start mb-1">
                    <h3 className="font-medium text-sm">{product.name}</h3>
                    <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded-full">
                      {product.category}
                    </span>
                  </div>
                  <p className="text-xs text-gray-600 mb-2 line-clamp-2">{product.description}</p>
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-lg font-bold text-purple-600">₹{product.price}</span>
                    <div className="flex gap-2 text-xs text-gray-500">
                      {product.color && <span>Color: {product.color}</span>}
                      {product.size && <span>Size: {product.size}</span>}
                    </div>
                  </div>
                  <button
                    onClick={() => addToCart(product)}
                    className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-2 px-3 rounded-lg text-sm font-medium hover:from-purple-700 hover:to-blue-700 transition-all duration-200 shadow-sm hover:shadow-md"
                  >
                    🛒 Add to Cart
                  </button>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Middle Panel - Voice Chat (Always Visible) */}
      <div className="relative flex flex-col bg-gray-50 h-screen">
        {/* Header */}
        <div className="flex-shrink-0 p-4 border-b bg-white shadow-sm">
          <h2 className="text-lg font-semibold text-center">🎤 Voice Assistant</h2>
          <p className="text-xs text-gray-500 text-center mt-1">Speak to browse and order</p>
        </div>

        {/* Chat Transcript - Scrollable Area */}
        <div className="flex-1 overflow-y-auto px-4 pt-4 pb-4" ref={scrollAreaRef}>
          <div className="space-y-3 max-w-2xl mx-auto">
            {messages.length === 0 ? (
              <div className="text-center text-gray-400 mt-8">
                <div className="text-4xl mb-4">🎤</div>
                <p className="text-sm font-medium">Start speaking to interact</p>
                <p className="text-xs mt-2">Try: "Show me mugs" or "Add coffee mug to cart"</p>
              </div>
            ) : (
              <>
                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={cn(
                      'flex',
                      msg.from?.isLocal ? 'justify-end' : 'justify-start'
                    )}
                  >
                    <div
                      className={cn(
                        'max-w-[80%] rounded-lg px-4 py-3 shadow-sm',
                        msg.from?.isLocal
                          ? 'bg-purple-600 text-white'
                          : 'bg-white text-gray-800 border border-gray-200'
                      )}
                    >
                      <div className="flex items-start gap-2">
                        <span className="text-lg flex-shrink-0">
                          {msg.from?.isLocal ? '👤' : '🤖'}
                        </span>
                        <p className="text-sm whitespace-pre-wrap">{msg.message}</p>
                      </div>
                    </div>
                  </div>
                ))}
                {/* Invisible element to scroll to */}
                <div ref={messagesEndRef} />
              </>
            )}
          </div>
        </div>

        {/* Bottom Controls - Fixed at Bottom */}
        <div className="flex-shrink-0 bg-white border-t shadow-lg">
          <div className="p-4">
            <AgentControlBar controls={controls} onChatOpenChange={setChatOpen} />
          </div>
        </div>
      </div>

      {/* Right Panel - Shopping Cart */}
      <div className="border-l bg-gray-50 overflow-y-auto h-screen">
        <div className="p-4 border-b bg-white">
          <h2 className="text-lg font-semibold">Cart ({getTotalItems()})</h2>
        </div>
        <div className="p-4">
          {/* Order Success Message - Shows until new item added */}
          {showOrderSuccess && cart.length === 0 && (
            <div className="bg-green-50 border-2 border-green-500 rounded-lg p-4">
              <div className="flex items-center gap-2 mb-3">
                <span className="text-3xl">✅</span>
                <h3 className="font-bold text-green-800 text-lg">Order Placed Successfully!</h3>
              </div>
              <div className="bg-white rounded p-3 mb-3">
                <p className="text-sm text-gray-600 mb-1">Order ID:</p>
                <p className="text-base font-mono font-semibold text-gray-800">
                  {lastOrderId}
                </p>
              </div>
              <div className="flex items-center gap-2 text-sm text-green-700 bg-green-100 rounded p-2">
                <span>📧</span>
                <span>Confirmation email sent to your address</span>
              </div>
              <p className="text-xs text-gray-500 mt-3 text-center">
                Continue shopping to add more items
              </p>
            </div>
          )}
          
          {cart.length === 0 && !showOrderSuccess ? (
            <p className="text-gray-500 text-sm">Your cart is empty</p>
          ) : cart.length > 0 ? (
            <div className="space-y-3">
              {cart.map((item) => (
                <div key={`${item.id}-${item.size || 'no-size'}`} className="bg-white p-3 rounded-lg shadow-sm border">
                  <h3 className="font-medium text-sm">{item.name}</h3>
                  <p className="text-xs text-gray-600">₹{item.price} each</p>
                  {item.size && item.size !== 'NA' && item.size !== '' && (
                    <p className="text-xs text-purple-600">Size: {item.size}</p>
                  )}
                  {item.color && <p className="text-xs text-gray-500">Color: {item.color}</p>}
                  <div className="flex items-center justify-between mt-2">
                    <div className="flex items-center gap-2">
                      <button 
                        onClick={() => updateQuantity(item.id, item.quantity - 1)}
                        className="w-6 h-6 rounded bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-xs"
                      >
                        -
                      </button>
                      <span className="text-sm font-medium">{item.quantity}</span>
                      <button 
                        onClick={() => updateQuantity(item.id, item.quantity + 1)}
                        className="w-6 h-6 rounded bg-gray-200 hover:bg-gray-300 flex items-center justify-center text-xs"
                      >
                        +
                      </button>
                    </div>
                    <div className="text-right">
                      <div className="text-sm font-semibold">₹{item.price * item.quantity}</div>
                      <button 
                        onClick={() => removeFromCart(item.id)}
                        className="text-xs text-red-600 hover:text-red-800"
                      >
                        Remove
                      </button>
                    </div>
                  </div>
                </div>
              ))}
              <div className="border-t pt-3 mt-3">
                <div className="flex justify-between items-center mb-3">
                  <span className="font-semibold">Total: ₹{getTotalPrice()}</span>
                </div>
                <Button className="w-full bg-green-600 hover:bg-green-700">
                  Checkout
                </Button>
              </div>
            </div>
          ) : null}
        </div>
      </div>
    </section>
  );
};