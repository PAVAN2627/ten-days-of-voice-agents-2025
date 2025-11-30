import { NextRequest, NextResponse } from 'next/server';

let currentCart: any[] = [];

export async function GET() {
  return NextResponse.json({ success: true, cart: currentCart });
}

export async function POST(request: NextRequest) {
  try {
    const { action, ...data } = await request.json();
    
    if (action === 'sync') {
      currentCart = data.cart || [];
      return NextResponse.json({ success: true });
    }
    
    if (action === 'add') {
      const { product } = data;
      const existing = currentCart.find(item => item.id === product.id);
      if (existing) {
        existing.quantity += 1;
      } else {
        currentCart.push({ ...product, quantity: 1 });
      }
      return NextResponse.json({ success: true, cart: currentCart });
    }
    
    return NextResponse.json({ success: false });
  } catch (error) {
    return NextResponse.json({ success: false });
  }
}