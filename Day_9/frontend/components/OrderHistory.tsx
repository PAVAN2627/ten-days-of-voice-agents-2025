import React, { useState, useEffect } from 'react';
import './OrderHistory.css';

const OrderHistory = ({ user, onSelectOrder, onClose }) => {
  const [orders, setOrders] = useState([]);
  const [spending, setSpending] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('orders');

  useEffect(() => {
    if (user?.email) {
      fetchOrdersAndSpending();
    }
  }, [user]);

  const fetchOrdersAndSpending = async () => {
    try {
      setLoading(true);
      setError(null);

      const [ordersRes, spendingRes] = await Promise.all([
        fetch(`http://localhost:8000/acp/users/${user.email}/orders`),
        fetch(`http://localhost:8000/acp/users/${user.email}/spending`)
      ]);

      if (!ordersRes.ok || !spendingRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const ordersData = await ordersRes.json();
      const spendingData = await spendingRes.json();

      setOrders(ordersData.orders || []);
      setSpending(spendingData);
    } catch (err) {
      console.error('Fetch error:', err);
      setError('Unable to load order history. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
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
      <div className="order-history">
        <div className="history-loader">Loading order history...</div>
      </div>
    );
  }

  return (
    <div className="order-history">
      <div className="history-header">
        <h2>📦 Order History</h2>
        <button className="history-close" onClick={onClose}>✕</button>
      </div>

      {error && (
        <div className="history-error">
          ⚠️ {error}
        </div>
      )}

      <div className="history-tabs">
        <button
          className={`tab-btn ${activeTab === 'orders' ? 'active' : ''}`}
          onClick={() => setActiveTab('orders')}
        >
          Orders ({orders.length})
        </button>
        <button
          className={`tab-btn ${activeTab === 'spending' ? 'active' : ''}`}
          onClick={() => setActiveTab('spending')}
        >
          Analytics
        </button>
      </div>

      <div className="history-content">
        {activeTab === 'orders' && (
          <>
            {orders.length === 0 ? (
              <div className="history-empty">
                <div className="empty-icon">📦</div>
                <h3>No orders yet</h3>
                <p>Start shopping to see your order history!</p>
              </div>
            ) : (
              <div className="orders-list">
                {orders.map(order => (
                  <div
                    key={order.id}
                    className="order-card"
                    onClick={() => onSelectOrder(order)}
                  >
                    <div className="order-header-row">
                      <div className="order-id-section">
                        <h4 className="order-id">Order #{order.id.slice(0, 8)}</h4>
                        <p className="order-date">
                          {formatDate(order.created_at)}
                        </p>
                      </div>
                      <div className="order-status-badge">
                        <span style={{ color: getStatusColor(order.status) }}>
                          {getStatusEmoji(order.status)} {order.status}
                        </span>
                      </div>
                    </div>

                    <div className="order-items-preview">
                      {order.line_items.slice(0, 3).map((item, idx) => (
                        <div key={idx} className="item-preview">
                          <span className="item-name">{item.name}</span>
                          <span className="item-qty">x{item.quantity}</span>
                        </div>
                      ))}
                      {order.line_items.length > 3 && (
                        <div className="items-more">
                          +{order.line_items.length - 3} more
                        </div>
                      )}
                    </div>

                    <div className="order-footer">
                      <div className="order-amount">
                        <span className="amount-label">Total:</span>
                        <span className="amount-value">Rs.{order.total_amount}</span>
                      </div>
                      <span className="order-click-hint">Click to view →</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {activeTab === 'spending' && spending && (
          <div className="spending-analytics">
            <div className="spending-overview">
              <div className="overview-card">
                <div className="card-label">Total Spending</div>
                <div className="card-value">Rs.{spending.total_spent}</div>
                <div className="card-note">Across {spending.total_orders} orders</div>
              </div>

              <div className="overview-card">
                <div className="card-label">Average Order Value</div>
                <div className="card-value">
                  Rs.{spending.total_orders > 0 ? Math.round(spending.total_spent / spending.total_orders) : 0}
                </div>
                <div className="card-note">Per order</div>
              </div>
            </div>

            <div className="category-breakdown">
              <h3>Spending by Category</h3>
              {spending.by_category && Object.entries(spending.by_category).length > 0 ? (
                <div className="categories-list">
                  {Object.entries(spending.by_category).map(([category, amount]) => (
                    <div key={category} className="category-item">
                      <div className="category-info">
                        <span className="category-name">
                          {category.charAt(0).toUpperCase() + category.slice(1)}
                        </span>
                        <div className="category-bar">
                          <div
                            className="category-progress"
                            style={{
                              width: `${(amount / spending.total_spent) * 100}%`
                            }}
                          />
                        </div>
                      </div>
                      <div className="category-amount">Rs.{amount}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-categories">No category data available</p>
              )}
            </div>

            <div className="spending-note">
              💡 Track your spending patterns to make informed shopping decisions!
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default OrderHistory;
