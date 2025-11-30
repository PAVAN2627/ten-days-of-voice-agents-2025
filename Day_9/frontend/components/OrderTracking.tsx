import React, { useState, useEffect } from 'react';
import './OrderTracking.css';

const OrderTracking = ({ orderId, onClose }) => {
  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (orderId) {
      fetchOrderDetails();
    }
  }, [orderId]);

  const fetchOrderDetails = async () => {
    try {
      setLoading(true);
      setError(null);

      const response = await fetch(`http://localhost:8000/acp/orders/${orderId}`);
      if (!response.ok) {
        throw new Error('Order not found');
      }

      const data = await response.json();
      setOrder(data.order);
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Unable to load order details. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusTimeline = () => {
    const statuses = ['pending', 'processing', 'shipped', 'delivered'];
    const currentStatus = order?.status?.toLowerCase() || 'pending';
    const currentIndex = statuses.indexOf(currentStatus);

    return statuses.map((status, index) => ({
      status,
      completed: index <= currentIndex,
      current: index === currentIndex
    }));
  };

  const getStatusColor = (status) => {
    const colors = {
      'pending': '#f6ad55',
      'processing': '#4299e1',
      'shipped': '#48bb78',
      'delivered': '#38a169',
      'cancelled': '#f56565'
    };
    return colors[status?.toLowerCase()] || '#a0aec0';
  };

  const getStatusEmoji = (status) => {
    const emojis = {
      'pending': '⏳',
      'processing': '🔄',
      'shipped': '📦',
      'delivered': '✅',
      'cancelled': '❌'
    };
    return emojis[status?.toLowerCase()] || '❓';
  };

  if (loading) {
    return (
      <div className="order-tracking">
        <div className="tracking-loader">Loading order details...</div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="order-tracking">
        <div className="tracking-header">
          <h2>📍 Order Tracking</h2>
          <button className="tracking-close" onClick={onClose}>✕</button>
        </div>
        <div className="tracking-error">
          ⚠️ {error || 'Order not found'}
        </div>
      </div>
    );
  }

  const timeline = getStatusTimeline();

  return (
    <div className="order-tracking">
      <div className="tracking-header">
        <h2>📍 Order Tracking</h2>
        <button className="tracking-close" onClick={onClose}>✕</button>
      </div>

      {/* Order Summary */}
      <div className="order-summary">
        <div className="summary-section">
          <div className="summary-item">
            <span className="summary-label">Order ID</span>
            <span className="summary-value">{order.id.slice(0, 8)}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Order Date</span>
            <span className="summary-value">{formatDate(order.created_at)}</span>
          </div>
          <div className="summary-item">
            <span className="summary-label">Total Amount</span>
            <span className="summary-value-highlight">Rs.{order.total_amount}</span>
          </div>
        </div>

        <div className="status-section">
          <div className="status-badge" style={{ borderColor: getStatusColor(order.status) }}>
            <span style={{ color: getStatusColor(order.status) }}>
              {getStatusEmoji(order.status)} {order.status}
            </span>
          </div>
        </div>
      </div>

      {/* Status Timeline */}
      <div className="status-timeline">
        <h3>Delivery Timeline</h3>
        <div className="timeline-track">
          {timeline.map((item, index) => (
            <div key={item.status} className="timeline-item">
              <div
                className={`timeline-dot ${item.completed ? 'completed' : ''} ${item.current ? 'current' : ''}`}
                style={{
                  backgroundColor: item.completed ? getStatusColor('shipped') : '#e2e8f0'
                }}
              >
                {item.completed && '✓'}
              </div>
              <div className="timeline-label">{item.status}</div>
            </div>
          ))}
        </div>
        <div className="timeline-note">
          {order.status === 'delivered'
            ? '✅ Your order has been delivered successfully!'
            : order.status === 'shipped'
            ? '📦 Your order is on its way!'
            : order.status === 'processing'
            ? '⏳ We\'re preparing your order'
            : '⏳ Your order is pending processing'}
        </div>
      </div>

      {/* Shipping Details */}
      <div className="shipping-details">
        <h3>Shipping Information</h3>
        {order.buyer ? (
          <div className="details-box">
            <div className="detail-row">
              <span className="detail-label">Recipient Name</span>
              <span className="detail-value">{order.buyer.name || 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Email</span>
              <span className="detail-value">{order.buyer.email || 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Phone</span>
              <span className="detail-value">{order.buyer.phone || 'N/A'}</span>
            </div>
            <div className="detail-row">
              <span className="detail-label">Address</span>
              <span className="detail-value">{order.buyer.address || 'N/A'}</span>
            </div>
          </div>
        ) : (
          <p className="no-shipping">No shipping information available</p>
        )}
      </div>

      {/* Order Items */}
      <div className="order-items-detail">
        <h3>Items in This Order</h3>
        <div className="items-list">
          {order.line_items && order.line_items.length > 0 ? (
            order.line_items.map((item, index) => (
              <div key={index} className="item-detail-row">
                <div className="item-detail-info">
                  <div className="item-detail-name">{item.name}</div>
                  <div className="item-detail-meta">
                    Qty: {item.quantity} × Rs.{item.unit_amount}
                  </div>
                </div>
                <div className="item-detail-total">Rs.{item.line_total}</div>
              </div>
            ))
          ) : (
            <p className="no-items">No items found</p>
          )}
        </div>
      </div>

      {/* Order Total */}
      <div className="order-total-detail">
        <div className="total-row">
          <span>Subtotal</span>
          <span>Rs.{order.line_items ? order.line_items.reduce((sum, item) => sum + item.line_total, 0) : 0}</span>
        </div>
        <div className="total-row">
          <span>Tax (Estimated)</span>
          <span>Rs.{Math.round(order.total_amount * 0.05)}</span>
        </div>
        <div className="total-row total-final">
          <span>Total Amount</span>
          <span>Rs.{order.total_amount}</span>
        </div>
      </div>

      {/* Action Buttons */}
      <div className="tracking-actions">
        <button className="btn btn-refresh" onClick={fetchOrderDetails}>
          🔄 Refresh Status
        </button>
        <button className="btn btn-close" onClick={onClose}>
          Close
        </button>
      </div>
    </div>
  );
};

export default OrderTracking;
