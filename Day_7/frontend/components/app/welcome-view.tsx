import { Button } from '@/components/livekit/button';
import Image from 'next/image';
import { motion } from 'motion/react';

interface WelcomeViewProps {
  startButtonText: string;
  onStartCall: () => void;
}

export const WelcomeView = ({
  startButtonText,
  onStartCall,
  ref,
}: React.ComponentProps<'div'> & WelcomeViewProps) => {
  return (
    <div ref={ref} className="relative h-full w-full overflow-hidden bg-gradient-to-br from-blue-50 via-purple-50 to-green-50 dark:from-blue-950 dark:via-purple-950 dark:to-green-950">
      {/* Animated background circles */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
          className="absolute -left-20 -top-20 h-96 w-96 rounded-full bg-blue-400/20 blur-3xl"
        />
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            opacity: [0.3, 0.5, 0.3],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 1,
          }}
          className="absolute -right-20 -bottom-20 h-96 w-96 rounded-full bg-green-400/20 blur-3xl"
        />
      </div>

      <section className="relative z-10 flex h-full flex-col items-center justify-center px-6 text-center">
        {/* Logo */}
        <motion.div
          initial={{ scale: 0, rotate: -180 }}
          animate={{ scale: 1, rotate: 0 }}
          transition={{ duration: 0.8, type: 'spring', bounce: 0.5 }}
          className="mb-8"
        >
          <div className="relative h-40 w-40 overflow-hidden rounded-full bg-white p-6 shadow-2xl ring-4 ring-blue-500/20">
            <Image
              src="/dailymartlogowithname.png"
              alt="DailyMart"
              width={160}
              height={160}
              className="object-contain"
              priority
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
          Order groceries with your voice. Browse products, manage your cart, and complete purchases
          - all hands-free!
        </motion.p>

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="mb-10 grid grid-cols-1 gap-4 md:grid-cols-3"
        >
          <div className="rounded-2xl bg-white/50 p-6 backdrop-blur-sm dark:bg-gray-800/50">
            <div className="mb-3 text-4xl">🎤</div>
            <h3 className="mb-2 font-semibold">Voice Ordering</h3>
            <p className="text-sm text-muted-foreground">Natural voice commands</p>
          </div>
          <div className="rounded-2xl bg-white/50 p-6 backdrop-blur-sm dark:bg-gray-800/50">
            <div className="mb-3 text-4xl">🛒</div>
            <h3 className="mb-2 font-semibold">Smart Cart</h3>
            <p className="text-sm text-muted-foreground">Budget & dietary filters</p>
          </div>
          <div className="rounded-2xl bg-white/50 p-6 backdrop-blur-sm dark:bg-gray-800/50">
            <div className="mb-3 text-4xl">🚚</div>
            <h3 className="mb-2 font-semibold">Fast Delivery</h3>
            <p className="text-sm text-muted-foreground">FREE above ₹1000</p>
          </div>
        </motion.div>

        {/* Start Button */}
        <motion.div
          initial={{ opacity: 0, scale: 0.8 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.9, type: 'spring' }}
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

        {/* Info Text */}
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1.1 }}
          className="mt-8 max-w-md text-sm text-muted-foreground"
        >
          Click the button above to start your voice shopping experience. Register or login to begin
          ordering!
        </motion.p>

        {/* Popular Items Badge */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.3 }}
          className="mt-6 flex flex-wrap justify-center gap-2"
        >
          {['🍚 Rice', '🥛 Milk', '🌶️ Spices', '🍪 Snacks', '🥤 Drinks', '🍰 Sweets'].map(
            (item, i) => (
              <span
                key={i}
                className="rounded-full bg-white/70 px-4 py-2 text-sm font-medium shadow-sm backdrop-blur-sm dark:bg-gray-800/70"
              >
                {item}
              </span>
            )
          )}
        </motion.div>
      </section>
    </div>
  );
};
