'use client';

import { useEffect, useRef } from 'react';
import { useTranscriptions, useRoomContext, useDataChannel } from '@livekit/components-react';

interface MessageLoggerProps {
  onMessage: (message: string, isUser: boolean) => void;
}

export function MessageLogger({ onMessage }: MessageLoggerProps) {
  const room = useRoomContext();
  const transcriptions = useTranscriptions();
  const processedIdsRef = useRef<Set<string>>(new Set());
  const lastTextByStreamRef = useRef<Map<string, string>>(new Map());
  const timeoutsByStreamRef = useRef<Map<string, NodeJS.Timeout>>(new Map());

  // Log participant info when room changes
  useEffect(() => {
    if (room) {
      console.log('Room participants:', {
        local: room.localParticipant.identity,
        remote: Array.from(room.remoteParticipants.values()).map(p => p.identity)
      });
    }
  }, [room]);

  // Listen for data channel messages (agent responses)
  useDataChannel((message) => {
    try {
      const decoder = new TextDecoder();
      const text = decoder.decode(message.payload);
      console.log('Data channel message received:', text);
      onMessage(`🤖 Host: ${text}`, false);
    } catch (error) {
      console.error('Error processing data channel message:', error);
    }
  });

  // Process transcriptions (user speech AND agent speech) - STREAMING MODE
  useEffect(() => {
    if (!transcriptions || !room) return;

    console.log('📝 Processing transcriptions:', transcriptions.length);
    
    // Process transcriptions with real-time streaming updates
    transcriptions.forEach((transcription) => {
      const streamId = transcription.streamInfo.id;
      const currentText = transcription.text.trim();
      const lastText = lastTextByStreamRef.current.get(streamId) || '';
      
      // Skip if empty or same as last
      if (!currentText || currentText === lastText) return;
      
      // Update the cached text
      lastTextByStreamRef.current.set(streamId, currentText);
      
      const participantIdentity = transcription.participantInfo.identity || '';
      const isLocal = participantIdentity === room.localParticipant.identity;
      
      // Check if this stream was already started
      const streamKey = `${streamId}-started`;
      const isNewStream = !processedIdsRef.current.has(streamKey);
      
      if (isNewStream) {
        // Mark this stream as started
        processedIdsRef.current.add(streamKey);
        
        console.log('🆕 New message stream from:', {
          identity: participantIdentity,
          isLocal,
          text: currentText.slice(0, 50)
        });
        
        // Send initial message
        if (isLocal) {
          onMessage(`🎤 You: ${currentText}`, true);
        } else {
          onMessage(`🤖 Host: ${currentText}`, false);
        }
      } else {
        // Update existing message - send update with special flag
        console.log('📝 Updating message:', currentText.slice(0, 50));
        
        if (isLocal) {
          onMessage(`🎤 You: ${currentText}`, true);
        } else {
          onMessage(`🤖 Host: ${currentText}`, false);
        }
      }
    });
  }, [transcriptions, room, onMessage]);

  // Fallback: Listen to room events for agent messages
  useEffect(() => {
    if (!room) return;

    const handleDataReceived = (payload: Uint8Array, participant: any) => {
      try {
        const decoder = new TextDecoder();
        const text = decoder.decode(payload);
        console.log('Room data received:', text);
        if (participant && participant.identity !== room.localParticipant.identity) {
          onMessage(`🤖 Host: ${text}`, false);
        }
      } catch (error) {
        console.error('Error processing room data:', error);
      }
    };

    room.on('dataReceived', handleDataReceived);

    return () => {
      room.off('dataReceived', handleDataReceived);
    };
  }, [room, onMessage]);

  return null;
}
