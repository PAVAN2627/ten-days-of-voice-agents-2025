import { NextRequest, NextResponse } from 'next/server';

// Simple session store for demo
let currentUser: any = null;

export async function POST(request: NextRequest) {
  try {
    const { action, name, email } = await request.json();
    
    if (action === 'login') {
      currentUser = { name, email, authenticated: true };
      return NextResponse.json({ success: true, user: currentUser });
    }
    
    if (action === 'logout') {
      currentUser = null;
      return NextResponse.json({ success: true });
    }
    
    return NextResponse.json({ success: false });
  } catch (error) {
    return NextResponse.json({ success: false });
  }
}

export async function GET() {
  return NextResponse.json({ 
    success: !!currentUser, 
    user: currentUser 
  });
}