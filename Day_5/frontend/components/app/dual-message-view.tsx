'use client';

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import type { ReceivedChatMessage } from '@livekit/components-react';
import Image from 'next/image';
import { cn } from '@/lib/utils';

interface DualMessageViewProps {
  messages?: ReceivedChatMessage[];
  hidden?: boolean;
}

const RazorpayLogo = () => (
  <motion.div
    className="flex flex-col items-center justify-center gap-3"
    initial={{ opacity: 0, scale: 0.8 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ duration: 0.5 }}
  >
    <div className="w-32 h-32 relative flex items-center justify-center">
      <Image
        src="/razorpaylogo.png"
        alt="Razorpay Logo"
        fill
        className="object-contain"
        priority
      />
    </div>
    <div className="text-center">
      <p className="text-base font-bold text-gray-900 dark:text-white">Razorpay</p>
      <p className="text-xs text-blue-600 dark:text-blue-400 font-semibold">Priya SDR</p>
    </div>
  </motion.div>
);

const MessageBubble = ({
  message,
  isAgent,
  timestamp,
}: {
  message: string;
  isAgent: boolean;
  timestamp: number;
}) => {
  const time = new Date(timestamp);
  const timeString = time.toLocaleTimeString('en-US', { timeStyle: 'short' });

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      exit={{ opacity: 0, y: -10 }}
      transition={{ duration: 0.3 }}
      className={cn('flex gap-2 mb-3', isAgent ? 'justify-start' : 'justify-end')}
    >
      {isAgent && (
        <div className="w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center flex-shrink-0 mt-0.5">
          <span className="text-white text-xs font-bold">P</span>
        </div>
      )}

      <div className={cn('flex flex-col gap-1', isAgent ? 'items-start' : 'items-end')}>
        <p className="text-xs font-semibold text-gray-600 dark:text-gray-400 px-3">
          {isAgent ? '🎤 Priya (Agent)' : '👤 You (Customer)'}
        </p>
        <div
          className={cn(
            'px-4 py-2 rounded-xl max-w-xs lg:max-w-md text-sm leading-relaxed break-words',
            isAgent
              ? 'bg-blue-100 dark:bg-blue-900 text-gray-900 dark:text-white rounded-bl-none'
              : 'bg-gray-200 dark:bg-gray-700 text-gray-900 dark:text-white rounded-br-none'
          )}
        >
          {message}
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 px-3">{timeString}</p>
      </div>

      {!isAgent && (
        <div className="w-8 h-8 rounded-full bg-green-500 flex items-center justify-center flex-shrink-0 mt-0.5">
          <span className="text-white text-xs font-bold">Y</span>
        </div>
      )}
    </motion.div>
  );
};

export function DualMessageView({
  messages = [],
  hidden = false,
}: DualMessageViewProps) {
  const localMessages = messages.filter((m) => m.from?.isLocal);
  const remoteMessages = messages.filter((m) => !m.from?.isLocal);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [messages]);

  if (hidden) return null;

  return (
    <div className="w-full h-full bg-white dark:bg-gray-950 flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-700 dark:from-blue-800 dark:to-blue-900 text-white px-6 py-4">
        <h2 className="text-xl font-bold">🎤 Live Conversation</h2>
        <p className="text-sm text-blue-100">Real-time Sales Agent - Razorpay</p>
      </div>

      {/* Main Content */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-6">
        {messages.length === 0 ? (
          <div className="h-full flex items-center justify-center">
            <div className="text-center">
              <RazorpayLogo />
              <p className="text-gray-500 dark:text-gray-400 mt-6 text-sm">
                Waiting for conversation to start...
              </p>
            </div>
          </div>
        ) : (
          <div className="flex gap-6 max-w-7xl mx-auto h-full">
            {/* Left - Your Messages - Fixed width, equal to right */}
            <div className="flex flex-col w-[calc(50%-80px)] flex-shrink-0">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-green-500"></div>
                <h3 className="font-bold text-gray-900 dark:text-white text-sm">Your Voice</h3>
              </div>
              <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-gray-800 dark:to-gray-900 rounded-lg p-4 flex-1 overflow-y-auto border border-green-200 dark:border-green-900">
                <div className="space-y-3">
                  <AnimatePresence mode="popLayout">
                    {localMessages.map((msg) => (
                      <motion.div
                        key={msg.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                        className="bg-white dark:bg-gray-700 rounded-lg p-3 shadow-sm border-l-4 border-green-500 w-full"
                      >
                        <p className="text-xs text-green-600 dark:text-green-400 font-semibold mb-1">👤 You</p>
                        <p className="text-sm text-gray-900 dark:text-white break-words leading-relaxed overflow-wrap-anywhere">{msg.message}</p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                          {new Date(msg.timestamp).toLocaleTimeString('en-US', { timeStyle: 'short' })}
                        </p>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  {localMessages.length === 0 && (
                    <p className="text-center text-gray-400 dark:text-gray-500 text-sm py-8">
                      Your messages will appear here
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* Center - Logo - Fixed width */}
            <div className="flex items-center justify-center py-8 w-40 flex-shrink-0">
              <RazorpayLogo />
            </div>

            {/* Right - Agent Messages - Fixed width, equal to left */}
            <div className="flex flex-col w-[calc(50%-80px)] flex-shrink-0">
              <div className="flex items-center gap-2 mb-4">
                <div className="w-3 h-3 rounded-full bg-blue-500"></div>
                <h3 className="font-bold text-gray-900 dark:text-white text-sm">Priya (Agent)</h3>
              </div>
              <div className="bg-gradient-to-br from-blue-50 to-blue-100 dark:from-gray-800 dark:to-gray-900 rounded-lg p-4 flex-1 overflow-y-auto border border-blue-200 dark:border-blue-900">
                <div className="space-y-3">
                  <AnimatePresence mode="popLayout">
                    {remoteMessages.map((msg) => (
                      <motion.div
                        key={msg.id}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -10 }}
                        transition={{ duration: 0.2 }}
                        className="bg-white dark:bg-gray-700 rounded-lg p-3 shadow-sm border-l-4 border-blue-500 w-full"
                      >
                        <p className="text-xs text-blue-600 dark:text-blue-400 font-semibold mb-1">🎤 Priya</p>
                        <p className="text-sm text-gray-900 dark:text-white break-words leading-relaxed overflow-wrap-anywhere">{msg.message}</p>
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-2">
                          {new Date(msg.timestamp).toLocaleTimeString('en-US', { timeStyle: 'short' })}
                        </p>
                      </motion.div>
                    ))}
                  </AnimatePresence>
                  {remoteMessages.length === 0 && (
                    <p className="text-center text-gray-400 dark:text-gray-500 text-sm py-8">
                      Agent responses will appear here
                    </p>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 dark:border-gray-800 bg-gray-50 dark:bg-gray-900 px-6 py-3 text-center text-sm text-gray-600 dark:text-gray-400">
        <p>💬 {messages.length} messages • 🎤 Real-time Voice Agent</p>
      </div>
    </div>
  );
}
