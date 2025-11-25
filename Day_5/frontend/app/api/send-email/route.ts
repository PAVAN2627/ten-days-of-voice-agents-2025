import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const emailData = await request.json();

    // Forward to backend LiveKit agent for sending
    const backendUrl = process.env.NEXT_PUBLIC_LIVEKIT_SERVER_URL || 'http://localhost:8081';
    
    const response = await fetch(`${backendUrl}/send-email`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.LIVEKIT_API_KEY}`,
      },
      body: JSON.stringify(emailData),
    });

    if (!response.ok) {
      throw new Error(`Backend error: ${response.statusText}`);
    }

    const result = await response.json();

    return NextResponse.json(
      { 
        success: true, 
        message: 'Email sent successfully',
        data: result 
      },
      { status: 200 }
    );
  } catch (error) {
    console.error('Email sending error:', error);
    return NextResponse.json(
      { 
        success: false, 
        message: error instanceof Error ? error.message : 'Failed to send email',
      },
      { status: 500 }
    );
  }
}

export async function OPTIONS() {
  return NextResponse.json({}, { status: 200 });
}
