'use client';

import { useEffect, useRef, useState } from 'react';
import { motion } from 'framer-motion';

interface ChatOverlayProps {
  messages: string[];
}

export function ChatOverlay({ messages }: ChatOverlayProps) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [isUserScrolling, setIsUserScrolling] = useState(false);

  // Auto-scroll to bottom when new messages arrive (unless user is scrolling)
  useEffect(() => {
    if (scrollRef.current && !isUserScrolling) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages, isUserScrolling]);

  // Detect if user is manually scrolling
  const handleScroll = () => {
    if (scrollRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = scrollRef.current;
      const isAtBottom = scrollHeight - scrollTop - clientHeight < 50;
      setIsUserScrolling(!isAtBottom);
    }
  };

  // Don't show if no messages
  if (messages.length === 0) {
    return null;
  }

  return (
    <div 
      ref={scrollRef}
      onScroll={handleScroll}
      className="bg-black/60 backdrop-blur-lg rounded-2xl p-4 max-h-96 overflow-y-auto space-y-2 shadow-2xl border border-white/10 custom-scrollbar"
      style={{ scrollBehavior: 'smooth' }}
    >
      {messages.map((message, idx) => {
        const isUser = message.includes('🎤 You:');
        const isHost = message.includes('🤖 Host:');
        const cleanMessage = message.replace(/^\[.*?\]\s*/, '').replace(/^(🎤 You:|🤖 Host:)\s*/, '');
        
        return (
          <motion.div
            key={`overlay-${idx}-${message.slice(0, 20)}`}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3 }}
            className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'}`}
          >
            <span className={`text-xs font-bold px-2 ${
              isUser ? 'text-blue-300' : 'text-green-300'
            }`}>
              {isUser ? '🎤 You' : '🤖 Host'}
            </span>
            <div className={`px-4 py-2.5 rounded-2xl text-sm max-w-[85%] shadow-lg ${
              isUser 
                ? 'bg-blue-500 text-white rounded-br-md' 
                : 'bg-gradient-to-br from-green-600 to-green-700 text-white rounded-bl-md border border-green-500/30'
            }`}>
              <p className="leading-relaxed whitespace-pre-wrap break-words">
                {cleanMessage}
              </p>
            </div>
          </motion.div>
        );
      })}
    </div>
  );
}