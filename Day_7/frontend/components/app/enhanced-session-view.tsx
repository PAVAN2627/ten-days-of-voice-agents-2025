'use client';

import React, { useEffect, useState } from 'react';
import { motion } from 'motion/react';
import type { AppConfig } from '@/app-config';
import { DualMessageView } from '@/components/app/dual-message-view';
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

interface EnhancedSessionViewProps {
  appConfig: AppConfig;
}

export const EnhancedSessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & EnhancedSessionViewProps) => {
  useConnectionTimeout(200_000);
  useDebugMode({ enabled: process.env.NODE_ENV !== 'production' });

  const messages = useChatMessages();
  const [chatOpen, setChatOpen] = useState(false);
  const [isActive, setIsActive] = useState(true);

  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsVideoInput,
  };

  return (
    <section
      className="relative z-10 flex h-full w-full flex-col overflow-hidden bg-background"
      {...props}
    >
      {/* Header */}
      <div className="border-b bg-gradient-to-r from-blue-500/10 via-purple-500/10 to-green-500/10 p-4 backdrop-blur-sm">
        <div className="mx-auto flex max-w-7xl items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-foreground">DailyMart Voice Assistant</h1>
            <p className="text-sm text-muted-foreground">
              Your friendly grocery ordering assistant
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div
              className={`h-3 w-3 rounded-full ${isActive ? 'animate-pulse bg-green-500' : 'bg-gray-400'}`}
            />
            <span className="text-sm font-medium text-muted-foreground">
              {isActive ? 'Active' : 'Inactive'}
            </span>
          </div>
        </div>
      </div>

      {/* Dual Message View */}
      <div className="flex-1 overflow-hidden">
        <DualMessageView messages={messages} isActive={isActive} />
      </div>

      {/* Control Bar */}
      <MotionBottom {...BOTTOM_VIEW_MOTION_PROPS} className="border-t bg-background/95 p-4 backdrop-blur-sm">
        <div className="mx-auto max-w-2xl">
          <AgentControlBar controls={controls} onChatOpenChange={setChatOpen} />
        </div>
      </MotionBottom>

      {/* Chat Overlay (if needed) */}
      {chatOpen && (
        <div className="fixed inset-0 z-50 bg-black/50 backdrop-blur-sm">
          <div className="flex h-full items-center justify-center p-4">
            <div className="w-full max-w-2xl rounded-2xl bg-background p-6 shadow-2xl">
              <div className="mb-4 flex items-center justify-between">
                <h2 className="text-xl font-bold">Chat Transcript</h2>
                <button
                  onClick={() => setChatOpen(false)}
                  className="rounded-full p-2 hover:bg-muted"
                >
                  ✕
                </button>
              </div>
              <div className="max-h-96 space-y-3 overflow-y-auto">
                {messages.map((msg, idx) => (
                  <div
                    key={`chat-${msg.timestamp}-${idx}`}
                    className={`rounded-lg p-3 ${
                      msg.from?.isLocal
                        ? 'bg-green-500/20 text-right'
                        : 'bg-blue-500/20 text-left'
                    }`}
                  >
                    <p className="text-sm">{msg.message}</p>
                    <span className="mt-1 block text-xs text-muted-foreground">
                      {new Date(msg.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </section>
  );
};
