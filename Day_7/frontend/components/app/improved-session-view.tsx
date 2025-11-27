'use client';

import React, { useEffect, useRef, useState } from 'react';
import { motion } from 'motion/react';
import Image from 'next/image';
import type { AppConfig } from '@/app-config';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { useChatMessages } from '@/hooks/useChatMessages';
import { useConnectionTimeout } from '@/hooks/useConnectionTimout';
import { useDebugMode } from '@/hooks/useDebug';

const MotionBottom = motion.create('div');

const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    delay: 0.5,
  },
};

interface ImprovedSessionViewProps {
  appConfig: AppConfig;
}

export const ImprovedSessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & ImprovedSessionViewProps) => {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: process.env.NODE_ENV !== 'production' });

  const messages = useChatMessages();
  const [chatOpen, setChatOpen] = useState(false);
  const agentScrollRef = useRef<HTMLDivElement>(null);
  const userScrollRef = useRef<HTMLDivElement>(null);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsVideoInput,
  };

  // Separate messages by sender
  const agentMessages = messages.filter((m) => !m.from?.isLocal);
  const userMessages = messages.filter((m) => m.from?.isLocal);

  // Auto-scroll to latest messages
  useEffect(() => {
    if (agentScrollRef.current) {
      agentScrollRef.current.scrollTop = agentScrollRef.current.scrollHeight;
    }
  }, [agentMessages]);

  useEffect(() => {
    if (userScrollRef.current) {
      userScrollRef.current.scrollTop = userScrollRef.current.scrollHeight;
    }
  }, [userMessages]);

  return (
    <section className="relative z-10 flex h-full w-full flex-col overflow-hidden bg-background" {...props}>
      {/* Centered Header with Logo */}
      <div className="border-b bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-green-500/10 py-6 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl flex-col items-center justify-center text-center">
          {/* Logo */}
          <motion.div
            animate={{
              scale: [1, 1.05, 1],
            }}
            transition={{
              duration: 3,
              repeat: Infinity,
              ease: 'easeInOut',
            }}
            className="mb-3"
          >
            <div className="relative h-20 w-20 overflow-hidden rounded-full bg-white p-3 shadow-lg ring-4 ring-purple-500/20">
              <Image
                src="/dailymartlogowithname.png"
                alt="DailyMart"
                width={80}
                height={80}
                className="object-contain"
              />
            </div>
          </motion.div>
          
          {/* Title and Status */}
          <h1 className="mb-1 bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 bg-clip-text text-2xl font-bold text-transparent">
            DailyMart Voice Assistant
          </h1>
          <p className="mb-2 text-sm text-muted-foreground">
            Your friendly grocery ordering assistant
          </p>
          
          {/* Status Badge */}
          <div className="flex items-center gap-2 rounded-full bg-green-500/10 px-4 py-1.5">
            <div className="h-2 w-2 animate-pulse rounded-full bg-green-500" />
            <span className="text-xs font-medium text-green-600 dark:text-green-400">Active Call</span>
          </div>
        </div>
      </div>

      {/* Dual Message View */}
      <div className="flex-1 overflow-hidden p-4 md:p-6">
        <div className="grid h-full grid-cols-1 gap-4 md:grid-cols-[2fr_1fr_2fr] md:gap-6">
          {/* Agent Messages Column */}
          <div className="flex flex-col overflow-hidden rounded-2xl border bg-gradient-to-br from-blue-500/5 to-blue-600/5 shadow-lg backdrop-blur-sm">
            <div className="flex items-center gap-3 border-b bg-blue-500/10 p-4">
              <div className="relative h-10 w-10 overflow-hidden rounded-full bg-white p-2 shadow-md">
                <Image
                  src="/dailymartjustlogo.png"
                  alt="Agent"
                  width={40}
                  height={40}
                  className="object-contain"
                />
              </div>
              <div>
                <h3 className="font-semibold text-blue-600 dark:text-blue-400">
                  DailyMart Assistant
                </h3>
                <p className="text-xs text-muted-foreground">
                  {agentMessages.length > 0 ? '🎤 Speaking' : '💤 Waiting'}
                </p>
              </div>
            </div>

            <div ref={agentScrollRef} className="flex-1 space-y-3 overflow-y-auto p-4">
              {agentMessages.length === 0 ? (
                <div className="flex h-full items-center justify-center">
                  <p className="text-center text-sm text-muted-foreground">
                    Agent messages will appear here
                  </p>
                </div>
              ) : (
                agentMessages.map((message, index) => (
                  <motion.div
                    key={`agent-${message.timestamp}-${index}`}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    className="rounded-xl bg-blue-500/10 p-3 shadow-sm"
                  >
                    <p className="text-sm leading-relaxed">{message.message}</p>
                    <span className="mt-1 block text-xs text-muted-foreground">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </motion.div>
                ))
              )}
            </div>
          </div>

          {/* Center Divider */}
          <div className="hidden flex-col items-center justify-center md:flex">
            <div className="relative flex h-full w-full flex-col items-center justify-center">
              {/* Vertical line */}
              <div className="absolute inset-y-0 left-1/2 w-px -translate-x-1/2 bg-gradient-to-b from-transparent via-border to-transparent" />
              
              {/* Voice Activity Indicator */}
              <motion.div
                className="relative z-10 flex flex-col items-center"
              >
                <div className="rounded-full bg-gradient-to-br from-blue-500/20 via-purple-500/20 to-green-500/20 p-6 shadow-lg backdrop-blur-sm">
                  <div className="flex flex-col items-center gap-3">
                    <p className="text-xs font-semibold text-muted-foreground">Voice Shopping</p>
                    <div className="flex items-center justify-center gap-1.5">
                      <motion.div
                        animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 1.5, repeat: Infinity }}
                        className="h-3 w-3 rounded-full bg-green-500"
                      />
                      <motion.div
                        animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0.3 }}
                        className="h-3 w-3 rounded-full bg-blue-500"
                      />
                      <motion.div
                        animate={{ scale: [1, 1.5, 1], opacity: [0.5, 1, 0.5] }}
                        transition={{ duration: 1.5, repeat: Infinity, delay: 0.6 }}
                        className="h-3 w-3 rounded-full bg-purple-500"
                      />
                    </div>
                    <p className="text-xs text-muted-foreground">Active</p>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>

          {/* User Messages Column */}
          <div className="flex flex-col overflow-hidden rounded-2xl border bg-gradient-to-br from-green-500/5 to-green-600/5 shadow-lg backdrop-blur-sm">
            <div className="flex items-center gap-3 border-b bg-green-500/10 p-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-green-500 to-green-600 text-xl font-bold text-white shadow-md">
                👤
              </div>
              <div>
                <h3 className="font-semibold text-green-600 dark:text-green-400">You</h3>
                <p className="text-xs text-muted-foreground">
                  {userMessages.length > 0 ? '🎙️ Speaking' : '⏸️ Listening'}
                </p>
              </div>
            </div>

            <div ref={userScrollRef} className="flex-1 space-y-3 overflow-y-auto p-4">
              {userMessages.length === 0 ? (
                <div className="flex h-full items-center justify-center">
                  <p className="text-center text-sm text-muted-foreground">
                    Your messages will appear here
                  </p>
                </div>
              ) : (
                userMessages.map((message, index) => (
                  <motion.div
                    key={`user-${message.timestamp}-${index}`}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    className="rounded-xl bg-green-500/10 p-3 shadow-sm"
                  >
                    <p className="text-sm leading-relaxed">{message.message}</p>
                    <span className="mt-1 block text-xs text-muted-foreground">
                      {new Date(message.timestamp).toLocaleTimeString()}
                    </span>
                  </motion.div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Control Bar */}
      <MotionBottom {...BOTTOM_VIEW_MOTION_PROPS} className="border-t bg-background/95 p-4 backdrop-blur-sm">
        <div className="mx-auto max-w-2xl">
          <AgentControlBar controls={controls} onChatOpenChange={setChatOpen} />
        </div>
      </MotionBottom>
    </section>
  );
};
