'use client';

import { useState, useEffect } from 'react';
import { useVoiceAssistant } from '@livekit/components-react';
import { AgentControlBar } from '@/components/app/agent-control-bar';

interface Product {
  id: string;
  name: string;
  price: number;
  currency: string;
  category: string;
  description: string;
  image?: string;
  color?: string;
  size?: string;
}

interface OrderConfirmation {
  id: string;
  total_amount: number;
  line_items: Array<{
    name: string;
    quantity: number;
    line_total: number;
  }>;
}

export function EnhancedShoppingView() {
  const { state, audioTrack } = useVoiceAssistant();
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [categories, setCategories] = useState<string[]>([]);
  const [messages, setMessages] = useState<Array<{ role: string; content: string }>>([]);
  const [showOrderPopup, setShowOrderPopup] = useState(false);
  const [orderConfirmation, setOrderConfirmation] = useState<OrderConfirmation | null>(null);

  // Fetch products
  useEffect(() => {
    fetch('http://localhost:8000/acp/catalog')
      .then(res => res.json())
      .then(data => {
        if (data.products) {
          setProducts(data.products);
          // Extract unique categories
          const cats = Array.from(new Set(data.products.map((p: Product) => p.category)));
          setCategories(['all', ...cats]);
        }
      })
      .catch(err => console.error('Error fetching products:', err));
  }, []);

  // Listen for agent messages
  useEffect(() => {
    if (state === 'speaking' && audioTrack) {
      // Add agent message
      setMessages(prev => [...prev, { role: 'agent', content: 'Speaking...' }]);
    }
  }, [state, audioTrack]);

  // Filter products by category
  const filteredProducts = selectedCategory === 'all' 
    ? products 
    : products.filter(p => p.category === selectedCategory);

  // Handle order confirmation (listen for order events)
  useEffect(() => {
    const handleOrderPlaced = (event: CustomEvent) => {
      setOrderConfirmation(event.detail);
      setShowOrderPopup(true);
      
      // Auto-close after 10 seconds
      setTimeout(() => {
        setShowOrderPopup(false);
      }, 10000);
    };

    window.addEventListener('orderPlaced' as any, handleOrderPlaced);
    return () => window.removeEventListener('orderPlaced' as any, handleOrderPlaced);
  }, []);

  return (
    <div className="flex h-screen bg-gradient-to-br from-purple-50 to-blue-50">
      {/* Left Sidebar - Products */}
      <div className="w-1/3 bg-white shadow-lg overflow-y-auto">
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-800 mb-4">🛍️ Products</h2>
          
          {/* Category Filter */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">Category</label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              {categories.map(cat => (
                <key={cat} value={cat}>
                  {cat.charAt(0).toUpperCase() + cat.slice(1)}
                </option>
              ))}
            </select>
          </div>

          {/* Products Grid */}
          <div className="space-y-4">
            {filteredProducts.map(product => (
              <div key={product.id} className="bg-gradient-to-br from-white to-gray-50 rounded-lg shadow-md hover:shadow-xl transition-shadow duration-300 overflow-hidden">
                {/* Product Image */}
                {product.image && (
                  <div className="h-48 overflow-hidden">
                    <img
                      src={product.image}
                      alt={product.name}
                      className="w-full h-full object-cover hover:scale-110 transition-transform duration-300"
                    />
                  </div>
                )}
                
                {/* Product Info */}
                <div className="p-4">
                  <div className="flex justify-between items-start mb-2">
                    <h3 className="text-lg font-semibold text-gray-800">{product.name}</h3>
                    <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded-full">
                      {product.category}
                    </span>
                  </div>
                  
                  <p className="text-sm text-gray-600 mb-3">{product.description}</p>
                  
                  <div className="flex justify-between items-center">
                    <span className="text-2xl font-bold text-purple-600">
                      ₹{product.price}
                    </span>
                    {product.color && (
                      <span className="text-xs text-gray-500">Color: {product.color}</span>
                    )}
                    {product.size && (
                      <span className="text-xs text-gray-500">Size: {product.size}</span>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Middle - Chat Messages */}
      <div className="flex-1 flex flex-col">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto p-6">
          <div className="max-w-3xl mx-auto space-y-4">
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold text-gray-800 mb-2">
                🎤 Voice Shopping Assistant
              </h1>
              <p className="text-gray-600">
                Speak to browse products, add to cart, and place orders
              </p>
            </div>

            {messages.map((msg, idx) => (
              <div
                key={idx}
                className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-3 ${
                    msg.role === 'user'
                      ? 'bg-purple-600 text-white'
                      : 'bg-white text-gray-800 shadow-md'
                  }`}
                >
                  <div className="flex items-start gap-2">
                    <span className="text-lg">
                      {msg.role === 'user' ? '👤' : '🤖'}
                    </span>
                    <p className="text-sm">{msg.content}</p>
                  </div>
                </div>
              </div>
            ))}

            {/* Agent Status */}
            {state === 'listening' && (
              <div className="flex justify-center">
                <div className="bg-green-100 text-green-700 px-4 py-2 rounded-full text-sm font-medium animate-pulse">
                  🎤 Listening...
                </div>
              </div>
            )}

            {state === 'thinking' && (
              <div className="flex justify-center">
                <div className="bg-blue-100 text-blue-700 px-4 py-2 rounded-full text-sm font-medium">
                  🤔 Thinking...
                </div>
              </div>
            )}

            {state === 'speaking' && (
              <div className="flex justify-center">
                <div className="bg-purple-100 text-purple-700 px-4 py-2 rounded-full text-sm font-medium animate-pulse">
                  🗣️ Speaking...
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Control Bar */}
        <div className="border-t border-gray-200 bg-white p-4">
          <AgentControlBar />
        </div>
      </div>

      {/* Order Confirmation Popup */}
      {showOrderPopup && orderConfirmation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 animate-fadeIn">
          <div className="bg-white rounded-2xl shadow-2xl max-w-md w-full mx-4 animate-slideUp">
            {/* Header */}
            <div className="bg-gradient-to-r from-green-500 to-emerald-600 text-white p-6 rounded-t-2xl">
              <div className="flex items-center justify-center mb-2">
                <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center">
                  <span className="text-4xl">✅</span>
                </div>
              </div>
              <h2 className="text-2xl font-bold text-center">Order Placed Successfully!</h2>
              <p className="text-center text-green-100 mt-2">
                Thank you for your purchase
              </p>
            </div>

            {/* Order Details */}
            <div className="p-6">
              <div className="mb-4">
                <p className="text-sm text-gray-600">Order ID</p>
                <p className="text-lg font-mono font-semibold text-gray-800">
                  {orderConfirmation.id}
                </p>
              </div>

              <div className="border-t border-gray-200 pt-4 mb-4">
                <p className="text-sm font-medium text-gray-700 mb-2">Items:</p>
                <div className="space-y-2">
                  {orderConfirmation.line_items.map((item, idx) => (
                    <div key={idx} className="flex justify-between text-sm">
                      <span className="text-gray-600">
                        {item.name} x{item.quantity}
                      </span>
                      <span className="font-medium text-gray-800">
                        ₹{item.line_total}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="border-t border-gray-200 pt-4 mb-6">
                <div className="flex justify-between items-center">
                  <span className="text-lg font-semibold text-gray-800">Total Amount</span>
                  <span className="text-2xl font-bold text-green-600">
                    ₹{orderConfirmation.total_amount}
                  </span>
                </div>
              </div>

              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mb-4">
                <p className="text-sm text-blue-800 text-center">
                  📧 A confirmation email has been sent to your email address
                </p>
              </div>

              <button
                onClick={() => setShowOrderPopup(false)}
                className="w-full bg-gradient-to-r from-purple-600 to-blue-600 text-white py-3 rounded-lg font-semibold hover:from-purple-700 hover:to-blue-700 transition-all duration-300 shadow-lg hover:shadow-xl"
              >
                Continue Shopping
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Animations */}
      <style jsx>{`
        @keyframes fadeIn {
          from { opacity: 0; }
          to { opacity: 1; }
        }
        @keyframes slideUp {
          from {
            opacity: 0;
            transform: translateY(20px);
          }
          to {
            opacity: 1;
            transform: translateY(0);
          }
        }
        .animate-fadeIn {
          animation: fadeIn 0.3s ease-out;
        }
        .animate-slideUp {
          animation: slideUp 0.4s ease-out;
        }
      `}</style>
    </div>
  );
}
