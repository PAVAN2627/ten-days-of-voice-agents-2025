'use client';

import React, { useEffect, useRef, useState } from 'react';
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

interface Day4SplitViewProps {
  messages: ReceivedChatMessage[];
  className?: string;
}

export const Day4SplitView: React.FC<Day4SplitViewProps> = ({
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

  return (
    <section className={cn('h-full w-full bg-background overflow-hidden', className)}>
      {/* Main split-screen layout */}
      <div className="flex h-full flex-col justify-between px-4 py-8">
        {/* Top Section - Three Columns Layout */}
        <div className="flex flex-1 items-stretch justify-between gap-6">
          {/* Left Side - Agent Photo + Box */}
          <div className="flex items-center gap-3">
            {/* Agent Photo */}
            <motion.div
              initial={{ opacity: 0, x: -40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              whileHover={{ scale: 1.05 }}
              className="relative h-32 w-32 flex-shrink-0 overflow-hidden rounded-full border-2 border-blue-500/50 shadow-lg"
            >
              <Image
                src="/ai_agent_photo.png"
                alt="AI Agent"
                fill
                className="object-cover"
                priority
                unoptimized
              />
            </motion.div>

            {/* Left Panel - Agent Messages */}
            <MotionDiv
              initial={{ opacity: 0, x: -40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              className="flex w-full max-w-3xl flex-col gap-3 rounded-2xl border border-blue-500/30 bg-gradient-to-br from-blue-500/5 to-transparent p-5 backdrop-blur-sm"
            >
              {/* Header */}
              <div className="flex items-center gap-2">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                  className="h-3 w-3 rounded-full bg-blue-500"
                />
                <h3 className="text-sm font-semibold text-foreground">Agent Says</h3>
              </div>
              
              {/* Messages Scroll Area */}
              <ScrollArea
                ref={leftScrollRef}
                className="h-72 pr-3"
              >
                <div className="flex flex-col gap-2">
                  {agentMessages.length === 0 ? (
                    <div className="flex h-full items-center justify-center">
                      <p className="text-center text-xs text-muted-foreground">
                        👂 Listening for agent...
                      </p>
                    </div>
                  ) : (
                    agentMessages.map((msg, idx) => (
                      <AnimatePresence key={msg.id} mode="popLayout">
                        <MotionDiv
                          initial={{ opacity: 0, y: 10, x: -10 }}
                          animate={{ opacity: 1, y: 0, x: 0 }}
                          exit={{ opacity: 0, y: -10, x: -10 }}
                          transition={{ duration: 0.3, delay: idx * 0.05 }}
                          className="rounded-lg border border-blue-500/20 bg-blue-500/10 p-3 text-xs text-foreground leading-relaxed"
                        >
                          {msg.message}
                        </MotionDiv>
                      </AnimatePresence>
                    ))
                  )}
                </div>
              </ScrollArea>
            </MotionDiv>
          </div>

          {/* Center - Voice Visualizer */}
          <MotionDiv
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.7, delay: 0.2, ease: 'easeOut' }}
            className="flex flex-col items-center justify-center gap-6"
          >
            {/* Animated Outer Ring */}
            <div className="relative h-48 w-48 rounded-full">
              {/* Pulsing background rings */}
              <motion.div
                animate={{ scale: [1, 1.1, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="absolute inset-0 rounded-full border border-primary/30"
              />
              <motion.div
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2.5, repeat: Infinity }}
                className="absolute inset-0 rounded-full border border-primary/20"
              />

              {/* Center Visualizer */}
              <div className="absolute inset-0 flex items-center justify-center rounded-full border-2 border-primary/50 bg-gradient-to-br from-primary/15 to-transparent">
                <BarVisualizer
                  barCount={8}
                  state={agentState}
                  options={{ minHeight: 12 }}
                  trackRef={agentAudioTrack}
                  className="flex h-full w-full items-center justify-center gap-2.5"
                >
                  <span
                    className={cn([
                      'rounded-full transition-all duration-200 ease-linear',
                      'data-[lk-highlighted=true]:bg-primary data-[lk-muted=true]:bg-primary/40',
                      'w-2 min-h-4',
                    ])}
                    style={{
                      background:
                        'linear-gradient(180deg, rgba(59, 130, 246, 0.8) 0%, rgba(59, 130, 246, 0.3) 100%)',
                    }}
                  />
                </BarVisualizer>
              </div>
            </div>

            {/* Status Text */}
            <div className="text-center">
              <motion.p
                className="text-sm font-medium text-foreground capitalize"
                animate={{ opacity: [1, 0.7, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                {agentState === 'speaking' && '🎤 Speaking'}
                {agentState === 'listening' && '👂 Listening'}
                {agentState === 'idle' && '✨ Ready'}
                {!agentState && '⏳ Connecting'}
              </motion.p>
              <p className="text-xs text-muted-foreground">Active Recall Coach</p>
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
              className="relative h-32 w-32 flex-shrink-0 overflow-hidden rounded-full border-2 border-green-500/50 shadow-lg"
            >
              <Image
                src="/boy_hoto.png"
                alt="User"
                fill
                className="object-cover"
                priority
                unoptimized
              />
            </motion.div>

            {/* Right Panel - User Messages */}
            <MotionDiv
              initial={{ opacity: 0, x: 40 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, ease: 'easeOut' }}
              className="flex w-full max-w-3xl flex-col gap-3 rounded-2xl border border-green-500/30 bg-gradient-to-br from-green-500/5 to-transparent p-5 backdrop-blur-sm"
            >
              {/* Header */}
              <div className="flex items-center gap-2">
                <motion.div
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity, delay: 0.2 }}
                  className="h-3 w-3 rounded-full bg-green-500"
                />
                <h3 className="text-sm font-semibold text-foreground">You Say</h3>
              </div>
              
              {/* Messages Scroll Area */}
              <ScrollArea
                ref={rightScrollRef}
                className="h-72 pr-3"
              >
                <div className="flex flex-col gap-2">
                  {userMessages.length === 0 ? (
                    <div className="flex h-full items-center justify-center">
                      <p className="text-center text-xs text-muted-foreground">
                        🎙️ Your responses here...
                      </p>
                    </div>
                  ) : (
                    userMessages.map((msg, idx) => (
                      <AnimatePresence key={msg.id} mode="popLayout">
                        <MotionDiv
                          initial={{ opacity: 0, y: 10, x: 10 }}
                          animate={{ opacity: 1, y: 0, x: 0 }}
                          exit={{ opacity: 0, y: -10, x: 10 }}
                          transition={{ duration: 0.3, delay: idx * 0.05 }}
                          className="ml-auto max-w-xs rounded-lg border border-green-500/20 bg-green-500/10 p-3 text-xs text-foreground leading-relaxed"
                        >
                          {msg.message}
                        </MotionDiv>
                      </AnimatePresence>
                    ))
                  )}
                </div>
              </ScrollArea>
            </MotionDiv>
          </div>
        </div>
      </div>
    </section>
  );
};
