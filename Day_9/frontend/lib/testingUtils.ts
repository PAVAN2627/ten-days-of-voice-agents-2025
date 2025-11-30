/**
 * E-Commerce Agent - Frontend Component Testing Utilities
 * Helper functions for testing React components
 */

export const testData = {
  products: [
    {
      id: 'mug-001',
      name: 'Coffee Mug',
      price: 800,
      currency: 'INR',
      category: 'mug',
      description: 'Premium ceramic coffee mug',
      color: 'white'
    },
    {
      id: 'tshirt-001',
      name: 'Cotton T-Shirt',
      price: 1200,
      currency: 'INR',
      category: 'clothing',
      description: '100% cotton casual t-shirt',
      color: 'blue'
    },
    {
      id: 'book-001',
      name: 'JavaScript Guide',
      price: 450,
      currency: 'INR',
      category: 'books',
      description: 'Comprehensive JavaScript programming guide',
    }
  ],
  
  user: {
    name: 'Test User',
    email: 'test@example.com',
    phone: '9876543210',
    address: '123 Test Street'
  },
  
  cartItem: {
    product_id: 'mug-001',
    name: 'Coffee Mug',
    category: 'mug',
    quantity: 1,
    unit_amount: 800,
    currency: 'INR',
    line_total: 800
  },
  
  order: {
    id: 'order-12345678',
    buyer: {
      name: 'Test User',
      email: 'test@example.com',
      phone: '9876543210',
      address: '123 Test Street'
    },
    line_items: [
      {
        product_id: 'mug-001',
        name: 'Coffee Mug',
        quantity: 2,
        unit_amount: 800,
        currency: 'INR',
        line_total: 1600
      }
    ],
    total_amount: 1680,
    currency: 'INR',
    status: 'processing',
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
};

/**
 * Mock API responses for testing without backend
 */
export const mockAPI = {
  getCatalog: async (filters = {}) => {
    return {
      success: true,
      count: testData.products.length,
      products: testData.products
    };
  },
  
  getCategories: async () => {
    return {
      success: true,
      categories: ['mug', 'clothing', 'books', 'accessories', 'electronics']
    };
  },
  
  getProduct: async (id) => {
    const product = testData.products.find(p => p.id === id);
    return {
      success: !!product,
      product: product || null
    };
  },
  
  createOrder: async (lineItems, buyerInfo) => {
    return {
      success: true,
      order: {
        id: `order-${Date.now()}`,
        buyer: buyerInfo,
        line_items: lineItems,
        total_amount: lineItems.reduce((sum, item) => sum + item.line_total, 0) * 1.05,
        status: 'pending',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString()
      }
    };
  },
  
  getOrder: async (orderId) => {
    return {
      success: true,
      order: testData.order
    };
  },
  
  getUserOrders: async (email) => {
    return {
      success: true,
      orders: [testData.order]
    };
  },
  
  getUserSpending: async (email) => {
    return {
      success: true,
      total_spent: 3360,
      total_orders: 2,
      average_order_value: 1680,
      by_category: {
        mug: 1600,
        clothing: 1200,
        electronics: 560
      }
    };
  },
  
  getCart: async (email) => {
    return {
      success: true,
      items: [testData.cartItem]
    };
  },
  
  saveCart: async (email, items) => {
    return {
      success: true,
      message: 'Cart saved'
    };
  },
  
  clearCart: async (email) => {
    return {
      success: true,
      message: 'Cart cleared'
    };
  }
};

/**
 * Component testing helpers
 */
export const testHelpers = {
  /**
   * Simulate user interaction - adding product to cart
   */
  addProductToCart: (product, quantity = 1) => {
    return {
      product_id: product.id,
      name: product.name,
      category: product.category,
      quantity,
      unit_amount: product.price,
      currency: product.currency || 'INR',
      line_total: product.price * quantity
    };
  },
  
  /**
   * Calculate cart totals
   */
  calculateCartTotals: (cartItems) => {
    const subtotal = cartItems.reduce((sum, item) => sum + item.line_total, 0);
    const tax = Math.round(subtotal * 0.05 * 100) / 100;
    const total = subtotal + tax;
    
    return {
      subtotal,
      tax,
      total,
      itemCount: cartItems.reduce((sum, item) => sum + item.quantity, 0)
    };
  },
  
  /**
   * Verify product card rendering
   */
  verifyProductCard: (product) => {
    return {
      hasId: !!product.id,
      hasName: !!product.name,
      hasPrice: typeof product.price === 'number',
      hasCategory: !!product.category,
      hasDescription: !!product.description,
      isValid: !!(product.id && product.name && product.price && product.category)
    };
  },
  
  /**
   * Verify order data
   */
  verifyOrder: (order) => {
    return {
      hasId: !!order.id,
      hasBuyer: !!order.buyer && !!order.buyer.email,
      hasLineItems: Array.isArray(order.line_items) && order.line_items.length > 0,
      hasTotal: typeof order.total_amount === 'number',
      hasStatus: !!order.status,
      isValid: !!(order.id && order.buyer && order.line_items && order.total_amount && order.status)
    };
  },
  
  /**
   * Format price for display
   */
  formatPrice: (amount, currency = 'INR') => {
    if (currency === 'INR') {
      return `Rs.${amount}`;
    }
    return `${currency} ${amount}`;
  },
  
  /**
   * Format date
   */
  formatDate: (dateString) => {
    return new Date(dateString).toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
};

/**
 * Performance testing utilities
 */
export const performanceTests = {
  /**
   * Measure component render time
   */
  measureRenderTime: async (ComponentFn) => {
    const start = performance.now();
    await ComponentFn();
    const end = performance.now();
    return end - start;
  },
  
  /**
   * Measure API response time
   */
  measureAPITime: async (apiFn) => {
    const start = performance.now();
    await apiFn();
    const end = performance.now();
    return end - start;
  },
  
  /**
   * Check memory usage
   */
  checkMemoryUsage: () => {
    if (typeof window !== 'undefined' && performance.memory) {
      return {
        usedJSHeapSize: (performance.memory.usedJSHeapSize / 1048576).toFixed(2) + ' MB',
        totalJSHeapSize: (performance.memory.totalJSHeapSize / 1048576).toFixed(2) + ' MB',
        jsHeapSizeLimit: (performance.memory.jsHeapSizeLimit / 1048576).toFixed(2) + ' MB'
      };
    }
    return null;
  }
};

/**
 * E2E test scenarios
 */
export const e2eScenarios = {
  /**
   * Complete purchase flow
   */
  completePurchaseFlow: async (api = mockAPI) => {
    const steps = [];
    
    try {
      // Step 1: Browse catalog
      steps.push({ name: 'Browse Catalog', status: 'running' });
      const catalog = await api.getCatalog();
      steps[steps.length - 1].status = catalog.success ? 'passed' : 'failed';
      
      // Step 2: Select product
      steps.push({ name: 'Select Product', status: 'running' });
      const product = catalog.products[0];
      steps[steps.length - 1].status = product ? 'passed' : 'failed';
      
      // Step 3: Add to cart
      steps.push({ name: 'Add to Cart', status: 'running' });
      const cartItem = testHelpers.addProductToCart(product, 1);
      steps[steps.length - 1].status = cartItem ? 'passed' : 'failed';
      
      // Step 4: Create order
      steps.push({ name: 'Checkout', status: 'running' });
      const order = await api.createOrder([cartItem], testData.user);
      steps[steps.length - 1].status = order.success ? 'passed' : 'failed';
      
      // Step 5: View order
      steps.push({ name: 'View Order', status: 'running' });
      const orderDetails = await api.getOrder(order.order.id);
      steps[steps.length - 1].status = orderDetails.success ? 'passed' : 'failed';
      
      return {
        success: steps.every(s => s.status === 'passed'),
        steps
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        steps
      };
    }
  },
  
  /**
   * Cart persistence flow
   */
  cartPersistenceFlow: async (api = mockAPI) => {
    const steps = [];
    
    try {
      // Step 1: Save cart
      steps.push({ name: 'Save Cart', status: 'running' });
      const cartItems = [testHelpers.addProductToCart(testData.products[0], 2)];
      const saveResult = await api.saveCart(testData.user.email, cartItems);
      steps[steps.length - 1].status = saveResult.success ? 'passed' : 'failed';
      
      // Step 2: Load cart
      steps.push({ name: 'Load Cart', status: 'running' });
      const loadResult = await api.getCart(testData.user.email);
      steps[steps.length - 1].status = loadResult.success ? 'passed' : 'failed';
      
      // Step 3: Verify data
      steps.push({ name: 'Verify Data', status: 'running' });
      const verified = loadResult.items && loadResult.items.length === cartItems.length;
      steps[steps.length - 1].status = verified ? 'passed' : 'failed';
      
      // Step 4: Clear cart
      steps.push({ name: 'Clear Cart', status: 'running' });
      const clearResult = await api.clearCart(testData.user.email);
      steps[steps.length - 1].status = clearResult.success ? 'passed' : 'failed';
      
      return {
        success: steps.every(s => s.status === 'passed'),
        steps
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        steps
      };
    }
  },
  
  /**
   * Order tracking flow
   */
  orderTrackingFlow: async (api = mockAPI) => {
    const steps = [];
    
    try {
      // Step 1: Get user orders
      steps.push({ name: 'Get User Orders', status: 'running' });
      const ordersResult = await api.getUserOrders(testData.user.email);
      steps[steps.length - 1].status = ordersResult.success ? 'passed' : 'failed';
      
      // Step 2: Select order
      steps.push({ name: 'Select Order', status: 'running' });
      const order = ordersResult.orders[0];
      steps[steps.length - 1].status = order ? 'passed' : 'failed';
      
      // Step 3: View order details
      steps.push({ name: 'View Order Details', status: 'running' });
      const detailsResult = await api.getOrder(order.id);
      steps[steps.length - 1].status = detailsResult.success ? 'passed' : 'failed';
      
      // Step 4: Check spending
      steps.push({ name: 'Check Spending', status: 'running' });
      const spendingResult = await api.getUserSpending(testData.user.email);
      steps[steps.length - 1].status = spendingResult.success ? 'passed' : 'failed';
      
      return {
        success: steps.every(s => s.status === 'passed'),
        steps
      };
    } catch (error) {
      return {
        success: false,
        error: error.message,
        steps
      };
    }
  }
};

/**
 * Export all testing utilities
 */
export default {
  testData,
  mockAPI,
  testHelpers,
  performanceTests,
  e2eScenarios
};
