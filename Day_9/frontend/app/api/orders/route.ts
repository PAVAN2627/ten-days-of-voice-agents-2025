import { NextResponse } from 'next/server';

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { line_items } = body;
    
    // Generate order ID
    const orderId = `ORD_${Date.now()}_${Math.random().toString(36).substr(2, 8)}`;
    
    // Calculate total (simplified)
    let total = 0;
    const processedItems = line_items.map((item: any) => {
      const price = getProductPrice(item.product_id);
      const lineTotal = price * item.quantity;
      total += lineTotal;
      
      return {
        product_id: item.product_id,
        quantity: item.quantity,
        unit_amount: price,
        line_total: lineTotal
      };
    });
    
    const order = {
      id: orderId,
      line_items: processedItems,
      total_amount: total,
      currency: "INR",
      status: "PENDING",
      created_at: new Date().toISOString()
    };
    
    return NextResponse.json(order);
  } catch (error) {
    console.error('Failed to create order:', error);
    return NextResponse.json({ error: 'Failed to create order' }, { status: 500 });
  }
}

function getProductPrice(productId: string): number {
  const prices: { [key: string]: number } = {
    "mug-001": 800,
    "mug-002": 600,
    "tshirt-001": 1200,
    "hoodie-001": 2500,
    "book-001": 1500,
    "phone-001": 500,
    "headphones-001": 3500
  };
  
  return prices[productId] || 1000;
}