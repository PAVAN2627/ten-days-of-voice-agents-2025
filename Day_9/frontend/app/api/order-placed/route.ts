import { NextResponse } from 'next/server';

// Store last order for polling
let lastOrder: any = null;

export async function POST(request: Request) {
  try {
    const body = await request.json();
    const { order } = body;
    
    // Store order for GET requests
    lastOrder = order;
    
    return NextResponse.json({ 
      success: true,
      message: 'Order notification received',
      order
    });
  } catch (error) {
    return NextResponse.json({ 
      success: false, 
      error: 'Failed to process order notification' 
    }, { status: 500 });
  }
}

export async function GET() {
  const order = lastOrder;
  lastOrder = null; // Clear after reading
  return NextResponse.json({ 
    success: true,
    order
  });
}
