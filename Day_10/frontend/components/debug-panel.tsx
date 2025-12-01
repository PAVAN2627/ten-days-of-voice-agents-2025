'use client';

import { useEffect, useState } from 'react';
import { useRoomContext, useConnectionState, useParticipants } from '@livekit/components-react';
import { ConnectionState } from 'livekit-client';

export function DebugPanel() {
  const room = useRoomContext();
  const connectionState = useConnectionState();
  const participants = useParticipants();
  const [events, setEvents] = useState<string[]>([]);

  useEffect(() => {
    if (!room) return;

    const addEvent = (event: string) => {
      const timestamp = new Date().toLocaleTimeString();
      setEvents(prev => [...prev.slice(-10), `[${timestamp}] ${event}`]);
    };

    // Monitor various room events
    const eventHandlers = {
      connected: () => addEvent('Room connected'),
      disconnected: () => addEvent('Room disconnected'),
      participantConnected: (participant: any) => addEvent(`Participant connected: ${participant.identity}`),
      participantDisconnected: (participant: any) => addEvent(`Participant disconnected: ${participant.identity}`),
      dataReceived: (payload: Uint8Array, participant: any) => {
        try {
          const text = new TextDecoder().decode(payload);
          addEvent(`Data received from ${participant?.identity || 'unknown'}: ${text.slice(0, 50)}...`);
        } catch (e) {
          addEvent(`Data received (binary) from ${participant?.identity || 'unknown'}`);
        }
      },
      trackSubscribed: (track: any, publication: any, participant: any) => {
        addEvent(`Track subscribed: ${track.kind} from ${participant.identity}`);
      },
      trackUnsubscribed: (track: any, publication: any, participant: any) => {
        addEvent(`Track unsubscribed: ${track.kind} from ${participant.identity}`);
      },
    };

    // Add all event listeners
    Object.entries(eventHandlers).forEach(([event, handler]) => {
      room.on(event as any, handler);
    });

    addEvent('Debug panel initialized');

    return () => {
      // Remove all event listeners
      Object.entries(eventHandlers).forEach(([event, handler]) => {
        room.off(event as any, handler);
      });
    };
  }, [room]);

  return (
    <div className="bg-black/50 backdrop-blur-md rounded-lg p-4 border border-gray-500/20 max-h-64 overflow-hidden">
      <h4 className="text-gray-300 font-bold mb-2 text-sm">Debug Panel</h4>
      <div className="space-y-1">
        <div className="text-xs text-gray-400">
          Connection: <span className={connectionState === ConnectionState.Connected ? 'text-green-400' : 'text-red-400'}>
            {connectionState}
          </span>
        </div>
        <div className="text-xs text-gray-400">
          Participants: {participants.length}
        </div>
        <div className="text-xs text-gray-400">
          Room: {room?.name || 'Not connected'}
        </div>
      </div>
      
      <div className="mt-3">
        <h5 className="text-gray-400 text-xs font-semibold mb-1">Recent Events:</h5>
        <div className="max-h-32 overflow-y-auto space-y-1">
          {events.map((event, idx) => (
            <div key={idx} className="text-xs text-gray-300 font-mono">
              {event}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}