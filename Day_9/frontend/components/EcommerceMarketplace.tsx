import React, { useState, useEffect, useRef } from 'react';
import ProductCard from './ProductCard';
import ShoppingCart from './ShoppingCart';
import OrderHistory from './OrderHistory';
import OrderTracking from './OrderTracking';
import './EcommerceMarketplace.css';

const EcommerceMarketplace = ({ user, appConfig }) => {
  const [activeView, setActiveView] = useState('marketplace');
  const [cart, setCart] = useState([]);
  const [orders, setOrders] = useState([]);
  const [selectedOrder, setSelectedOrder] = useState(null);
  const [notificationMessage, setNotificationMessage] = useState(null);

  // Show notification
  const showNotification = (message) => {
    setNotificationMessage(message);
    setTimeout(() => setNotificationMessage(null), 3000);
  };

  // Handle add to cart
  const handleAddToCart = (product, quantity) => {
    const existing = cart.find(item => item.product_id === product.id);
    if (existing) {
      setCart(cart.map(item =>
        item.product_id === product.id
          ? { ...item, quantity: item.quantity + quantity, line_total: item.unit_amount * (item.quantity + quantity) }
          : item
      ));
    } else {
      setCart([...cart, {
        product_id: product.id,
        name: product.name,
        category: product.category,
        quantity,
        unit_amount: product.price,
        currency: product.currency || 'INR',
        line_total: product.price * quantity
      }]);
    }
    showNotification(`✓ Added "${product.name}" (x${quantity}) to cart`);
  };

  // Handle buy now
  const handleBuyNow = (product, quantity) => {
    setCart([{
      product_id: product.id,
      name: product.name,
      category: product.category,
      quantity,
      unit_amount: product.price,
      currency: product.currency || 'INR',
      line_total: product.price * quantity
    }]);
    setActiveView('cart');
    showNotification('Proceed to checkout');
  };

  // Handle checkout
  const handleCheckout = (orderData) => {
    setOrders([...orders, orderData.order]);
    setCart([]);
    setActiveView('history');
    showNotification('✓ Order placed successfully! Order ID: ' + orderData.order.id.slice(0, 8));
  };

  // Handle save for later
  const handleSaveForLater = (cartItems) => {
    setCart(cartItems);
    showNotification('Cart saved to your account');
  };

  // Handle select order
  const handleSelectOrder = (order) => {
    setSelectedOrder(order);
    setActiveView('tracking');
  };

  return (
    <div className="ecommerce-marketplace">
      {/* Header */}
      <header className="marketplace-header">
        <div className="header-content">
          <div className="logo-section">
            <h1 className="marketplace-title">🛍️ E-Commerce Marketplace</h1>
            <p className="marketplace-subtitle">ACP Protocol - Voice-Enabled Shopping</p>
          </div>

          {user && (
            <div className="user-section">
              <div className="user-info">
                <span className="user-name">{user.name || user.email}</span>
                <span className="user-email">{user.email}</span>
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="marketplace-nav">
        <button
          className={`nav-tab ${activeView === 'marketplace' ? 'active' : ''}`}
          onClick={() => setActiveView('marketplace')}
        >
          🛒 Marketplace
        </button>
        <button
          className={`nav-tab ${activeView === 'cart' ? 'active' : ''}`}
          onClick={() => setActiveView('cart')}
        >
          🛒 Cart {cart.length > 0 && `(${cart.length})`}
        </button>
        <button
          className={`nav-tab ${activeView === 'history' ? 'active' : ''}`}
          onClick={() => setActiveView('history')}
        >
          📦 Orders
        </button>
      </nav>

      {/* Notification */}
      {notificationMessage && (
        <div className="notification-toast">
          {notificationMessage}
        </div>
      )}

      {/* Main Content */}
      <main className="marketplace-content">
        {activeView === 'marketplace' && (
          <div className="view-container">
            <ProductGrid
              onAddToCart={handleAddToCart}
              onBuyNow={handleBuyNow}
            />
          </div>
        )}

        {activeView === 'cart' && (
          <div className="view-container">
            <ShoppingCart
              user={user}
              onCheckout={handleCheckout}
              onSaveForLater={handleSaveForLater}
              onClose={() => setActiveView('marketplace')}
            />
          </div>
        )}

        {activeView === 'history' && (
          <div className="view-container">
            <OrderHistory
              user={user}
              onSelectOrder={handleSelectOrder}
              onClose={() => setActiveView('marketplace')}
            />
          </div>
        )}

        {activeView === 'tracking' && selectedOrder && (
          <div className="view-container">
            <OrderTracking
              orderId={selectedOrder.id}
              onClose={() => {
                setSelectedOrder(null);
                setActiveView('history');
              }}
            />
          </div>
        )}
      </main>
    </div>
  );
};

// Product Grid Component (inline)
const ProductGrid = ({ onAddToCart, onBuyNow }) => {
  const [products, setProducts] = useState([]);
  const [filteredProducts, setFilteredProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    category: 'all',
    search: '',
    maxPrice: 10000
  });

  useEffect(() => {
    fetchProducts();
    fetchCategories();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [products, filters]);

  const fetchProducts = async () => {
    try {
      const response = await fetch('http://localhost:8000/acp/catalog');
      if (!response.ok) throw new Error('Failed to fetch');
      const data = await response.json();
      setProducts(data.products || []);
    } catch (error) {
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await fetch('http://localhost:8000/acp/categories');
      if (!response.ok) throw new Error('Failed to fetch');
      const data = await response.json();
      setCategories(data.categories || []);
    } catch (error) {
      console.error('Error fetching categories:', error);
    }
  };

  const applyFilters = () => {
    let filtered = products;

    if (filters.category !== 'all') {
      filtered = filtered.filter(p => p.category === filters.category);
    }

    if (filters.search) {
      const search = filters.search.toLowerCase();
      filtered = filtered.filter(p =>
        p.name.toLowerCase().includes(search) ||
        p.description.toLowerCase().includes(search)
      );
    }

    filtered = filtered.filter(p => p.price <= filters.maxPrice);

    setFilteredProducts(filtered);
  };

  return (
    <div className="product-grid-wrapper">
      <div className="filter-section">
        <div className="filter-group">
          <label>Category</label>
          <select
            value={filters.category}
            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
            className="filter-select"
          >
            <option value="all">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>

        <div className="filter-group">
          <label>Search</label>
          <input
            type="text"
            placeholder="Search products..."
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            className="filter-input"
          />
        </div>

        <div className="filter-group">
          <label>Price: Rs.{filters.maxPrice}</label>
          <input
            type="range"
            min="100"
            max="10000"
            value={filters.maxPrice}
            onChange={(e) => setFilters({ ...filters, maxPrice: parseInt(e.target.value) })}
            className="filter-slider"
          />
        </div>
      </div>

      <div className="products-container">
        {loading ? (
          <div className="loading-spinner">Loading products...</div>
        ) : filteredProducts.length === 0 ? (
          <div className="empty-state">
            <p>No products found matching your filters</p>
          </div>
        ) : (
          <div className="products-grid">
            {filteredProducts.map(product => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={onAddToCart}
                onBuyNow={onBuyNow}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default EcommerceMarketplace;
