import React, { useState, useEffect } from 'react';
import './ShoppingCart.css';

const ShoppingCart = ({ user, onCheckout, onSaveForLater, onClose }) => {
  const [cartItems, setCartItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [processingCheckout, setProcessingCheckout] = useState(false);

  useEffect(() => {
    fetchCart();
  }, [user]);

  const fetchCart = async () => {
    try {
      setLoading(true);
      setError(null);

      if (!user?.email) {
        setCartItems([]);
        return;
      }

      const response = await fetch(
        `http://localhost:8000/acp/users/${user.email}/cart`,
        { headers: { 'Content-Type': 'application/json' } }
      );

      if (!response.ok) {
        if (response.status === 404) {
          setCartItems([]);
          return;
        }
        throw new Error('Failed to fetch cart');
      }

      const data = await response.json();
      setCartItems(data.items || []);
    } catch (err) {
      console.error('Cart fetch error:', err);
      setError('Unable to load cart. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const updateQuantity = (productId, newQuantity) => {
    if (newQuantity < 1) {
      removeItem(productId);
      return;
    }

    setCartItems(cartItems.map(item =>
      item.product_id === productId
        ? { ...item, quantity: newQuantity, line_total: item.unit_amount * newQuantity }
        : item
    ));
  };

  const removeItem = (productId) => {
    setCartItems(cartItems.filter(item => item.product_id !== productId));
  };

  const calculateSubtotal = () => {
    return cartItems.reduce((sum, item) => sum + item.line_total, 0);
  };

  const calculateTax = () => {
    return Math.round(calculateSubtotal() * 0.05 * 100) / 100; // 5% tax
  };

  const calculateTotal = () => {
    return calculateSubtotal() + calculateTax();
  };

  const handleCheckout = async () => {
    if (cartItems.length === 0) {
      alert('Your cart is empty!');
      return;
    }

    setProcessingCheckout(true);
    try {
      const lineItems = cartItems.map(item => ({
        product_id: item.product_id,
        name: item.name,
        quantity: item.quantity,
        unit_amount: item.unit_amount,
        currency: item.currency || 'INR'
      }));

      const response = await fetch('http://localhost:8000/acp/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          line_items: lineItems,
          buyer_info: {
            name: user.name || 'Guest',
            email: user.email,
            phone: user.phone || '',
            address: user.address || ''
          }
        })
      });

      if (!response.ok) {
        throw new Error('Checkout failed');
      }

      const orderData = await response.json();
      await clearCart();
      onCheckout(orderData);
    } catch (err) {
      console.error('Checkout error:', err);
      alert('Checkout failed. Please try again.');
    } finally {
      setProcessingCheckout(false);
    }
  };

  const handleSaveForLater = async () => {
    if (cartItems.length === 0) {
      alert('Cart is empty!');
      return;
    }

    try {
      const response = await fetch(
        `http://localhost:8000/acp/users/${user.email}/cart`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ items: cartItems })
        }
      );

      if (!response.ok) {
        throw new Error('Failed to save cart');
      }

      onSaveForLater(cartItems);
      alert('Cart saved for later! ✓');
    } catch (err) {
      console.error('Save cart error:', err);
      alert('Failed to save cart.');
    }
  };

  const clearCart = async () => {
    try {
      await fetch(
        `http://localhost:8000/acp/users/${user.email}/cart`,
        { method: 'DELETE' }
      );
      setCartItems([]);
    } catch (err) {
      console.error('Clear cart error:', err);
    }
  };

  if (loading) {
    return (
      <div className="shopping-cart">
        <div className="cart-loader">Loading cart...</div>
      </div>
    );
  }

  return (
    <div className="shopping-cart">
      <div className="cart-header">
        <h2>🛒 Shopping Cart</h2>
        <button className="cart-close" onClick={onClose}>✕</button>
      </div>

      {error && (
        <div className="cart-error">
          ⚠️ {error}
        </div>
      )}

      {cartItems.length === 0 ? (
        <div className="cart-empty">
          <div className="empty-icon">🛒</div>
          <h3>Your cart is empty</h3>
          <p>Add items from the marketplace to get started!</p>
        </div>
      ) : (
        <>
          <div className="cart-items">
            {cartItems.map(item => (
              <div key={item.product_id} className="cart-item">
                <div className="item-emoji">
                  {item.category === 'mug' && '🍵'}
                  {item.category === 'clothing' && '👕'}
                  {item.category === 'books' && '📚'}
                  {item.category === 'accessories' && '🎒'}
                  {item.category === 'electronics' && '🎧'}
                </div>

                <div className="item-details">
                  <h4 className="item-name">{item.name}</h4>
                  <p className="item-price">Rs.{item.unit_amount} each</p>
                  <p className="item-category">{item.category}</p>
                </div>

                <div className="item-quantity">
                  <button
                    onClick={() => updateQuantity(item.product_id, item.quantity - 1)}
                    className="qty-btn"
                  >
                    −
                  </button>
                  <input
                    type="number"
                    value={item.quantity}
                    onChange={(e) => updateQuantity(item.product_id, parseInt(e.target.value) || 1)}
                    className="qty-input"
                  />
                  <button
                    onClick={() => updateQuantity(item.product_id, item.quantity + 1)}
                    className="qty-btn"
                  >
                    +
                  </button>
                </div>

                <div className="item-total">
                  <div className="total-label">Total</div>
                  <div className="total-amount">Rs.{item.line_total}</div>
                </div>

                <button
                  onClick={() => removeItem(item.product_id)}
                  className="item-remove"
                  title="Remove from cart"
                >
                  🗑️
                </button>
              </div>
            ))}
          </div>

          <div className="cart-summary">
            <div className="summary-row">
              <span>Subtotal:</span>
              <span className="summary-value">Rs.{calculateSubtotal()}</span>
            </div>
            <div className="summary-row">
              <span>Tax (5%):</span>
              <span className="summary-value">Rs.{calculateTax()}</span>
            </div>
            <div className="summary-row summary-total">
              <span>Total Amount:</span>
              <span className="summary-value-total">Rs.{calculateTotal()}</span>
            </div>
            <p className="summary-items">{cartItems.length} item(s) in cart</p>
          </div>

          <div className="cart-actions">
            <button
              onClick={handleSaveForLater}
              className="btn btn-save"
              disabled={processingCheckout}
            >
              💾 Save for Later
            </button>
            <button
              onClick={handleCheckout}
              className="btn btn-checkout"
              disabled={processingCheckout}
            >
              {processingCheckout ? '⏳ Processing...' : '💳 Checkout'}
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default ShoppingCart;
