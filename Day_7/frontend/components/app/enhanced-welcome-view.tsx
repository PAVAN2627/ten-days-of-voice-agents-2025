'use client';

import React from 'react';
import { motion } from 'motion/react';
import Image from 'next/image';
import { Button } from '@/components/livekit/button';

interface EnhancedWelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

const popularItems = [
  { name: '🍚 Basmati Rice', price: '₹150' },
  { name: '🥛 Fresh Milk', price: '₹60' },
  { name: '🌶️ Spices', price: '₹80' },
  { name: '🍪 Snacks', price: '₹45' },
  { name: '🥤 Beverages', price: '₹50' },
  { name: '🍰 Sweets', price: '₹120' },
];

export const EnhancedWelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & EnhancedWelcomeViewProps) => {
  return (
    <div ref={ref} className="flex h-full w-full items-center justify-center bg-gradient-to-br from-blue-50 via-purple-50 to-green-50 dark:from-blue-950 dark:via-purple-950 dark:to-green-950">
      <section className="flex max-w-4xl flex-col items-center justify-center px-6 text-center">
        {/* Logo */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ duration: 0.8, type: 'spring' }}
          className="mb-8"
        >
          <div className="relative h-32 w-32 overflow-hidden rounded-full bg-white p-4 shadow-2xl">
            <Image
              src="/dailymartlogowithname.png"
              alt="DailyMart"
              width={128}
              height={128}
              className="object-contain"
            />
          </div>
        </motion.div>

        {/* Title */}
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="mb-4 bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 bg-clip-text text-5xl font-bold text-transparent md:text-6xl"
        >
          DailyMart Voice Assistant
        </motion.h1>

        {/* Subtitle */}
        <motion.p
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="mb-8 max-w-2xl text-lg text-muted-foreground md:text-xl"
        >
          Your friendly grocery ordering assistant. Order groceries, manage your cart, and complete
          purchases entirely through voice commands.
        </motion.p>

        {/* Popular Items */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mb-8 w-full max-w-2xl"
        >
          <h3 className="mb-4 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
            Popular Items
          </h3>
          <div className="grid grid-cols-2 gap-3 md:grid-cols-3">
            {popularItems.map((item, index) => (
              <motion.div
                key={item.name}
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.8 + index * 0.1 }}
                className="rounded-xl bg-white/50 p-4 shadow-sm backdrop-blur-sm dark:bg-gray-800/50"
              >
                <p className="text-sm font-medium">{item.name}</p>
                <p className="text-xs text-muted-foreground">{item.price}</p>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Features */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.2 }}
          className="mb-8 grid grid-cols-1 gap-4 md:grid-cols-3"
        >
          <div className="rounded-xl bg-blue-500/10 p-4 backdrop-blur-sm">
            <div className="mb-2 text-3xl">🎤</div>
            <h4 className="mb-1 font-semibold">Voice Ordering</h4>
            <p className="text-xs text-muted-foreground">
              Order groceries naturally with your voice
            </p>
          </div>
          <div className="rounded-xl bg-purple-500/10 p-4 backdrop-blur-sm">
            <div className="mb-2 text-3xl">🛒</div>
            <h4 className="mb-1 font-semibold">Smart Cart</h4>
            <p className="text-xs text-muted-foreground">
              Manage items, quantities, and budget
            </p>
          </div>
          <div className="rounded-xl bg-green-500/10 p-4 backdrop-blur-sm">
            <div className="mb-2 text-3xl">📧</div>
            <h4 className="mb-1 font-semibold">Email Confirmation</h4>
            <p className="text-xs text-muted-foreground">
              Get instant order confirmations
            </p>
          </div>
        </motion.div>

        {/* Start Button */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 1.5, type: 'spring' }}
        >
          <Button
            variant="primary"
            size="lg"
            onClick={onStartCall}
            className="group relative overflow-hidden bg-gradient-to-r from-blue-600 via-purple-600 to-green-600 px-12 py-6 text-lg font-bold text-white shadow-2xl transition-all hover:scale-105 hover:shadow-3xl"
          >
            <span className="relative z-10 flex items-center gap-3">
              🎙️ {startButtonText}
            </span>
            <div className="absolute inset-0 bg-gradient-to-r from-green-600 via-purple-600 to-blue-600 opacity-0 transition-opacity group-hover:opacity-100" />
          </Button>
        </motion.div>

        {/* Instructions */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.8 }}
          className="mt-8 max-w-md text-xs text-muted-foreground"
        >
          Click the button above to start your voice shopping experience. You can register, browse
          products, add items to cart, and place orders using just your voice!
        </motion.p>
      </section>
    </div>
  );
};
