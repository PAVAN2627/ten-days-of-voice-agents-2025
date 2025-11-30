import React, { useState } from 'react';
import './ProductCard.css';

const ProductCard = ({ product, onAddToCart, onBuyNow }) => {
  const [quantity, setQuantity] = useState(1);
  const [showQuantity, setShowQuantity] = useState(false);

  const handleAddToCart = () => {
    onAddToCart(product, quantity);
    setQuantity(1);
    setShowQuantity(false);
  };

  const handleBuyNow = () => {
    onBuyNow(product, quantity);
    setQuantity(1);
    setShowQuantity(false);
  };

  return (
    <div className="product-card">
      {/* Product Image (Placeholder) */}
      <div className="product-image">
        <div className="image-placeholder">
          {product.category === 'mug' && '🍵'}
          {product.category === 'clothing' && '👕'}
          {product.category === 'books' && '📚'}
          {product.category === 'accessories' && '🎒'}
          {product.category === 'electronics' && '🎧'}
        </div>
        {product.color && (
          <div className="color-badge">{product.color}</div>
        )}
        {product.size && (
          <div className="size-badge">Size: {product.size}</div>
        )}
      </div>

      {/* Product Info */}
      <div className="product-info">
        <h4 className="product-name">{product.name}</h4>
        <p className="product-category">{product.category}</p>
        <p className="product-description">{product.description}</p>

        {/* Price */}
        <div className="product-price">
          <span className="price-amount">Rs.{product.price}</span>
          <span className="currency">{product.currency}</span>
        </div>

        {/* Quantity Selector */}
        {showQuantity && (
          <div className="quantity-selector">
            <button
              onClick={() => setQuantity(Math.max(1, quantity - 1))}
              className="qty-btn"
            >
              −
            </button>
            <input
              type="number"
              min="1"
              value={quantity}
              onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
              className="qty-input"
            />
            <button
              onClick={() => setQuantity(quantity + 1)}
              className="qty-btn"
            >
              +
            </button>
          </div>
        )}

        {/* Action Buttons */}
        <div className="product-actions">
          {!showQuantity ? (
            <>
              <button
                onClick={() => setShowQuantity(true)}
                className="btn btn-add-to-cart"
              >
                🛒 Add to Cart
              </button>
              <button
                onClick={() => setShowQuantity(true)}
                className="btn btn-buy-now"
              >
                💳 Buy Now
              </button>
            </>
          ) : (
            <>
              <button
                onClick={handleAddToCart}
                className="btn btn-add-to-cart-confirm"
              >
                Add {quantity}
              </button>
              <button
                onClick={handleBuyNow}
                className="btn btn-buy-now-confirm"
              >
                Buy {quantity}
              </button>
            </>
          )}
        </div>

        {/* Product ID */}
        <div className="product-id">
          ID: {product.id}
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
