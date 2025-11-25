'use client';

import React, { useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import Image from 'next/image';
import type { ReceivedChatMessage } from '@livekit/components-react';
import {
  BarVisualizer,
  useVoiceAssistant,
} from '@livekit/components-react';
import { cn } from '@/lib/utils';
import { ScrollArea } from '@/components/livekit/scroll-area/scroll-area';

const MotionDiv = motion.create('div');

interface Day5SplitViewProps {
  messages: ReceivedChatMessage[];
  className?: string;
}

export const Day5SplitView: React.FC<Day5SplitViewProps> = ({
  messages = [],
  className,
}) => {
  const { state: agentState, audioTrack: agentAudioTrack } = useVoiceAssistant();
  const leftScrollRef = useRef<HTMLDivElement>(null);
  const rightScrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to latest messages
  useEffect(() => {
    if (leftScrollRef.current) {
      setTimeout(() => {
        if (leftScrollRef.current) {
          leftScrollRef.current.scrollTop = leftScrollRef.current.scrollHeight;
        }
      }, 0);
    }
  }, [messages]);

  useEffect(() => {
    if (rightScrollRef.current) {
      setTimeout(() => {
        if (rightScrollRef.current) {
          rightScrollRef.current.scrollTop = rightScrollRef.current.scrollHeight;
        }
      }, 0);
    }
  }, [messages]);

  // Separate agent and user messages
  const agentMessages = messages.filter((msg) => msg.from?.isLocal === false);
  const userMessages = messages.filter((msg) => msg.from?.isLocal === true);
  
  // Check if we have any messages at all
  const hasMessages = messages && messages.length > 0;

  return (
    <section className={cn('h-full w-full bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 overflow-hidden flex flex-col', className)}>
      {/* Show welcome message if no messages yet */}
      {!hasMessages && (
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex-1 flex items-center justify-center"
        >
          <div className="text-center">
            <p className="text-2xl font-bold text-white mb-4">🎤 Call Connected</p>
            <p className="text-lg text-gray-300">Waiting for conversation to begin...</p>
            <div className="mt-8 flex justify-center gap-4">
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity }}
                className="w-3 h-3 rounded-full bg-blue-500"
              />
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity, delay: 0.2 }}
                className="w-3 h-3 rounded-full bg-blue-500"
              />
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 1, repeat: Infinity, delay: 0.4 }}
                className="w-3 h-3 rounded-full bg-blue-500"
              />
            </div>
          </div>
        </motion.div>
      )}

      {/* Show split view when messages arrive */}
      {hasMessages && (
        <div className="flex h-full flex-col justify-between px-4 py-8">
          {/* Top Section - Three Columns Layout */}
          <div className="flex flex-1 items-stretch justify-between gap-8">
          {/* Left Side - Agent Photo + Box */}
          <div className="flex items-center gap-3">
            {/* Agent Photo */}
            <motion.div
              initial={{ opacity: 0, x: -40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              whileHover={{ scale: 1.05 }}
              className="relative h-32 w-32 flex-shrink-0 overflow-hidden rounded-full border-4 border-blue-500 shadow-xl bg-gradient-to-br from-blue-400 to-blue-600"
            >
              <Image
                src="/razorpaylogo.png"
                alt="Priya - Razorpay SDR"
                fill
                className="object-contain p-2"
                priority
                unoptimized
              />
            </motion.div>

            {/* Left Panel - Agent Messages */}
            <MotionDiv
              initial={{ opacity: 0, x: -40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              className="flex w-full max-w-5xl flex-col gap-3 rounded-2xl border-2 border-blue-500/30 bg-gradient-to-br from-blue-900/40 to-slate-900/20 p-5 backdrop-blur-md shadow-2xl"
            >
              {/* Header */}
              <div className="flex items-center gap-2">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="h-3 w-3 rounded-full bg-blue-500"
                />
                <h3 className="text-sm font-bold text-blue-700 dark:text-blue-300">🎤 Priya (Agent)</h3>
              </div>
              
              {/* Messages Scroll Area */}
              <ScrollArea
                ref={leftScrollRef}
                className="h-72 pr-3"
              >
                <div className="flex flex-col gap-2">
                  {agentMessages && agentMessages.length > 0 ? (
                    agentMessages.map((msg, idx) => (
                      <AnimatePresence key={msg.id || idx} mode="popLayout">
                        <MotionDiv
                          initial={{ opacity: 0, y: 10, x: -10 }}
                          animate={{ opacity: 1, y: 0, x: 0 }}
                          exit={{ opacity: 0, y: -10, x: -10 }}
                          transition={{ duration: 0.3, delay: idx * 0.05 }}
                          className="rounded-xl border-2 border-blue-400 bg-blue-600 p-4 text-sm text-white leading-relaxed shadow-lg font-medium"
                        >
                          {msg.message || 'Message sent'}
                        </MotionDiv>
                      </AnimatePresence>
                    ))
                  ) : (
                    <div className="flex h-full items-center justify-center">
                      <p className="text-center text-sm text-blue-300 font-semibold">
                        👂 Waiting for conversation...
                      </p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </MotionDiv>
          </div>

          {/* Center - Voice Visualizer with Razorpay Logo */}
          <MotionDiv
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.2, ease: 'easeOut' }}
            className="flex flex-col items-center justify-center gap-6"
          >
            {/* Animated Outer Ring with Razorpay branding */}
            <div className="relative h-56 w-56 rounded-full">
              {/* Pulsing background rings */}
              <motion.div
                animate={{ scale: [1, 1.15, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="absolute inset-0 rounded-full border-2 border-blue-400/30 dark:border-blue-500/30"
              />
              <motion.div
                animate={{ scale: [1, 1.3, 1] }}
                transition={{ duration: 2.5, repeat: Infinity }}
                className="absolute inset-0 rounded-full border border-blue-300/20 dark:border-blue-500/20"
              />

              {/* Center Visualizer */}
              <div className="absolute inset-0 flex items-center justify-center rounded-full border-4 border-blue-500 bg-gradient-to-br from-blue-100 dark:from-blue-900/40 to-transparent shadow-xl">
                <BarVisualizer
                  barCount={8}
                  state={agentState}
                  options={{ minHeight: 16 }}
                  trackRef={agentAudioTrack}
                  className="flex h-full w-full items-center justify-center gap-2.5"
                >
                  <span
                    className={cn([
                      'rounded-full transition-all duration-200 ease-linear',
                      'data-[lk-highlighted=true]:bg-blue-600 data-[lk-muted=true]:bg-blue-300',
                      'w-3 min-h-4',
                    ])}
                    style={{
                      background:
                        'linear-gradient(180deg, rgba(59, 130, 246, 1) 0%, rgba(59, 130, 246, 0.4) 100%)',
                    }}
                  />
                </BarVisualizer>
              </div>
            </div>

            {/* Razorpay Logo - Centered */}
            <motion.div
              initial={{ scale: 0, rotate: -180 }}
              animate={{ scale: 1, rotate: 0 }}
              transition={{ duration: 0.8, delay: 0.3, ease: 'easeOut' }}
              className="relative w-24 h-24 flex-shrink-0 rounded-full bg-white border-4 border-blue-500 shadow-2xl flex items-center justify-center"
            >
              <Image
                src="/razorpaylogo.png"
                alt="Razorpay Logo"
                width={96}
                height={96}
                className="object-contain p-3"
                priority
                unoptimized
              />
            </motion.div>

            {/* Status Text */}
            <div className="text-center">
              <motion.p
                className="text-sm font-bold text-blue-700 dark:text-blue-300 capitalize"
                animate={{ opacity: [1, 0.7, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {agentState === 'speaking' && '🎤 Speaking'}
                {agentState === 'listening' && '👂 Listening'}
                {agentState === 'idle' && '✨ Ready'}
                {!agentState && '⏳ Connecting'}
              </motion.p>
              <p className="text-xs text-blue-600 dark:text-blue-400 font-semibold">Priya - SDR Agent</p>
            </div>
          </MotionDiv>

          {/* Right Side - Box + User Photo */}
          <div className="flex items-center gap-3 flex-row-reverse">
            {/* User Photo */}
            <motion.div
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              whileHover={{ scale: 1.05 }}
              className="relative h-32 w-32 flex-shrink-0 overflow-hidden rounded-full border-4 border-green-500 shadow-xl bg-gradient-to-br from-green-400 to-green-600"
            >
              <div className="w-full h-full flex items-center justify-center bg-green-500 text-white text-5xl font-bold">
                👤
              </div>
            </motion.div>

            {/* Right Panel - User Messages */}
            <MotionDiv
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              className="flex w-full max-w-5xl flex-col gap-3 rounded-3xl border-2 border-green-200 dark:border-green-800 bg-gradient-to-br from-green-50 dark:from-green-900/20 to-transparent p-5 backdrop-blur-sm shadow-lg"
            >
              {/* Header */}
              <div className="flex items-center gap-2">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 0.2 }}
                  className="h-3 w-3 rounded-full bg-green-500"
                />
                <h3 className="text-sm font-bold text-green-700 dark:text-green-300">👤 You (Customer)</h3>
              </div>
              
              {/* Messages Scroll Area */}
              <ScrollArea
                ref={rightScrollRef}
                className="h-72 pr-3"
              >
                <div className="flex flex-col gap-2">
                  {userMessages && userMessages.length > 0 ? (
                    userMessages.map((msg, idx) => (
                      <AnimatePresence key={msg.id || idx} mode="popLayout">
                        <MotionDiv
                          initial={{ opacity: 0, y: 10, x: 10 }}
                          animate={{ opacity: 1, y: 0, x: 0 }}
                          exit={{ opacity: 0, y: -10, x: 10 }}
                          transition={{ duration: 0.3, delay: idx * 0.05 }}
                          className="ml-auto max-w-xs rounded-lg border-2 border-green-400 bg-green-600 p-4 text-sm text-white leading-relaxed shadow-lg font-medium"
                        >
                          {msg.message || 'Message sent'}
                        </MotionDiv>
                      </AnimatePresence>
                    ))
                  ) : (
                    <div className="flex h-full items-center justify-center">
                      <p className="text-center text-sm text-green-300 font-semibold">
                        🎙️ Your messages will appear here...
                      </p>
                    </div>
                  )}
                </div>
              </ScrollArea>
            </MotionDiv>
          </div>
        </div>
        </div>
      )}
    </section>
  );
};
