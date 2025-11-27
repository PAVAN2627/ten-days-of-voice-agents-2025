'use client';

import React from 'react';
import { motion } from 'motion/react';
import Image from 'next/image';

interface DualMessageViewProps {
  messages: any[];
  isActive: boolean;
}

export function DualMessageView({ messages, isActive }: DualMessageViewProps) {
  const agentMessages = messages.filter((m) => !m.from?.isLocal);
  const userMessages = messages.filter((m) => m.from?.isLocal);

  return (
    <div className="grid h-full w-full grid-cols-1 gap-4 p-4 md:grid-cols-[1fr_auto_1fr] md:gap-6 md:p-6">
      {/* Agent Messages Column */}
      <div className="flex flex-col space-y-4 overflow-hidden rounded-2xl bg-gradient-to-br from-blue-500/10 to-blue-600/10 p-6 backdrop-blur-sm">
        <div className="flex items-center gap-3 border-b border-blue-500/20 pb-4">
          <div className="relative h-12 w-12 overflow-hidden rounded-full bg-white p-2 shadow-lg">
            <Image
              src="/dailymartjustlogo.png"
              alt="DailyMart Agent"
              width={48}
              height={48}
              className="object-contain"
            />
          </div>
          <div>
            <h3 className="text-lg font-semibold text-blue-600 dark:text-blue-400">
              DailyMart Assistant
            </h3>
            <p className="text-sm text-muted-foreground">
              {isActive ? '🎤 Speaking...' : '💤 Waiting'}
            </p>
          </div>
        </div>

        <div className="flex-1 space-y-3 overflow-y-auto">
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
                transition={{ delay: index * 0.1 }}
                className="rounded-xl bg-blue-500/20 p-4 shadow-sm backdrop-blur-sm"
              >
                <p className="text-sm leading-relaxed text-foreground">{message.message}</p>
                <span className="mt-2 block text-xs text-muted-foreground">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </motion.div>
            ))
          )}
        </div>
      </div>

      {/* Center Divider with Logo */}
      <div className="hidden items-center justify-center md:flex">
        <div className="relative flex h-full flex-col items-center justify-center">
          <div className="absolute inset-y-0 w-px bg-gradient-to-b from-transparent via-border to-transparent" />
          <motion.div
            animate={{
              scale: isActive ? [1, 1.1, 1] : 1,
            }}
            transition={{
              duration: 2,
              repeat: isActive ? Infinity : 0,
              ease: 'easeInOut',
            }}
            className="relative z-10 rounded-full bg-background p-4 shadow-xl"
          >
            <Image
              src="/dailymartlogowithname.png"
              alt="DailyMart"
              width={80}
              height={80}
              className="object-contain"
            />
          </motion.div>
        </div>
      </div>

      {/* User Messages Column */}
      <div className="flex flex-col space-y-4 overflow-hidden rounded-2xl bg-gradient-to-br from-green-500/10 to-green-600/10 p-6 backdrop-blur-sm">
        <div className="flex items-center gap-3 border-b border-green-500/20 pb-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-full bg-gradient-to-br from-green-500 to-green-600 text-2xl font-bold text-white shadow-lg">
            👤
          </div>
          <div>
            <h3 className="text-lg font-semibold text-green-600 dark:text-green-400">You</h3>
            <p className="text-sm text-muted-foreground">
              {isActive ? '🎙️ Listening...' : '⏸️ Paused'}
            </p>
          </div>
        </div>

        <div className="flex-1 space-y-3 overflow-y-auto">
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
                transition={{ delay: index * 0.1 }}
                className="rounded-xl bg-green-500/20 p-4 shadow-sm backdrop-blur-sm"
              >
                <p className="text-sm leading-relaxed text-foreground">{message.message}</p>
                <span className="mt-2 block text-xs text-muted-foreground">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
