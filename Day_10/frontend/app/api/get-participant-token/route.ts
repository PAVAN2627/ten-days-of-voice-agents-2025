import { NextResponse } from 'next/server';
import { AccessToken, type AccessTokenOptions, type VideoGrant } from 'livekit-server-sdk';

interface ConnectionDetails {
  token: string;
  url: string;
}

// NOTE: you are expected to define the following environment variables in `.env.local`:
const API_KEY = process.env.LIVEKIT_API_KEY;
const API_SECRET = process.env.LIVEKIT_API_SECRET;
const LIVEKIT_URL = process.env.LIVEKIT_URL;

// don't cache the results
export const revalidate = 0;

export async function POST(req: Request) {
  try {
    if (LIVEKIT_URL === undefined) {
      throw new Error('LIVEKIT_URL is not defined');
    }
    if (API_KEY === undefined) {
      throw new Error('LIVEKIT_API_KEY is not defined');
    }
    if (API_SECRET === undefined) {
      throw new Error('LIVEKIT_API_SECRET is not defined');
    }

    // Parse username from request body
    const body = await req.json();
    const username = body?.username || 'user';

    // Generate participant token
    const participantIdentity = `improv_player_${Math.floor(Math.random() * 100_000)}`;
    const roomName = `improv_battle_room`;

    const token = await createParticipantToken(
      { identity: participantIdentity, name: username },
      roomName
    );

    // Return connection details
    const data: ConnectionDetails = {
      token: token,
      url: LIVEKIT_URL,
    };
    
    const headers = new Headers({
      'Cache-Control': 'no-store',
    });
    
    return NextResponse.json(data, { headers });
  } catch (error) {
    if (error instanceof Error) {
      console.error('Error generating token:', error);
      return new NextResponse(JSON.stringify({ error: error.message }), { 
        status: 500,
        headers: { 'Content-Type': 'application/json' }
      });
    }
    return new NextResponse(JSON.stringify({ error: 'Unknown error' }), { 
      status: 500,
      headers: { 'Content-Type': 'application/json' }
    });
  }
}

function createParticipantToken(
  userInfo: AccessTokenOptions,
  roomName: string
): Promise<string> {
  const at = new AccessToken(API_KEY, API_SECRET, {
    ...userInfo,
    ttl: '24h',
  });
  const grant: VideoGrant = {
    room: roomName,
    roomJoin: true,
    canPublish: true,
    canPublishData: true,
    canSubscribe: true,
  };
  at.addGrant(grant);

  return at.toJwt();
}
