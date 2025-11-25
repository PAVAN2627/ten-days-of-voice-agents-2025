import Image from 'next/image';
import { Button } from '@/components/livekit/button';
import { motion } from 'motion/react';

// Razorpay-themed animated payment icon
function RazorpayAnimatedIcon() {
  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.5 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.8, ease: "easeOut" }}
      className="mb-8 relative"
    >
      {/* Outer glow ring */}
      <motion.div
        animate={{
          scale: [1, 1.2, 1],
          opacity: [0.3, 0.6, 0.3],
        }}
        transition={{
          duration: 3,
          repeat: Infinity,
          ease: "easeInOut"
        }}
        className="absolute inset-0 rounded-full bg-gradient-to-r from-blue-500 to-indigo-600 blur-2xl"
      />
      
      {/* Main icon container */}
      <div className="relative bg-gradient-to-br from-blue-600 to-indigo-700 rounded-3xl p-6 shadow-2xl">
        {/* Payment card icon with animation */}
        <motion.svg
          width="100"
          height="100"
          viewBox="0 0 100 100"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          className="text-white"
        >
          {/* Credit card */}
          <motion.rect
            x="10"
            y="25"
            width="80"
            height="50"
            rx="6"
            fill="white"
            fillOpacity="0.2"
            initial={{ x: -100 }}
            animate={{ x: 10 }}
            transition={{ duration: 0.6, delay: 0.2 }}
          />
          <motion.rect
            x="10"
            y="35"
            width="80"
            height="8"
            fill="white"
            fillOpacity="0.4"
            initial={{ scaleX: 0 }}
            animate={{ scaleX: 1 }}
            transition={{ duration: 0.4, delay: 0.5 }}
          />
          
          {/* Chip */}
          <motion.rect
            x="20"
            y="50"
            width="15"
            height="12"
            rx="2"
            fill="white"
            fillOpacity="0.8"
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ duration: 0.3, delay: 0.7 }}
          />
          
          {/* Card numbers */}
          <motion.g
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.6 }}
            transition={{ duration: 0.4, delay: 0.9 }}
          >
            <rect x="45" y="52" width="8" height="3" rx="1" fill="white" />
            <rect x="55" y="52" width="8" height="3" rx="1" fill="white" />
            <rect x="65" y="52" width="8" height="3" rx="1" fill="white" />
            <rect x="75" y="52" width="8" height="3" rx="1" fill="white" />
          </motion.g>
          
          {/* Checkmark animation */}
          <motion.path
            d="M35 65 L42 72 L55 59"
            stroke="#10b981"
            strokeWidth="4"
            strokeLinecap="round"
            strokeLinejoin="round"
            fill="none"
            initial={{ pathLength: 0 }}
            animate={{ pathLength: 1 }}
            transition={{ duration: 0.5, delay: 1.2 }}
          />
        </motion.svg>
        
        {/* Floating particles */}
        {[...Array(3)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white rounded-full"
            style={{
              top: `${20 + i * 30}%`,
              left: `${10 + i * 20}%`,
            }}
            animate={{
              y: [-10, 10, -10],
              opacity: [0.3, 0.8, 0.3],
            }}
            transition={{
              duration: 2 + i * 0.5,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.3,
            }}
          />
        ))}
      </div>
    </motion.div>
  );
}

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
    <div ref={ref} className="w-full h-full relative overflow-hidden">
      {/* Animated background gradient */}
      <motion.div
        className="absolute inset-0 bg-gradient-to-br from-blue-50 via-indigo-50 to-purple-50 dark:from-gray-900 dark:via-blue-950 dark:to-indigo-950"
        animate={{
          backgroundPosition: ['0% 0%', '100% 100%', '0% 0%'],
        }}
        transition={{
          duration: 20,
          repeat: Infinity,
          ease: "linear"
        }}
        style={{
          backgroundSize: '200% 200%',
        }}
      />
      
      {/* Floating payment icons background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(6)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute text-blue-200 dark:text-blue-900 opacity-20"
            style={{
              left: `${10 + i * 15}%`,
              top: `${20 + (i % 3) * 25}%`,
            }}
            animate={{
              y: [-20, 20, -20],
              rotate: [0, 10, 0, -10, 0],
              scale: [1, 1.1, 1],
            }}
            transition={{
              duration: 5 + i,
              repeat: Infinity,
              ease: "easeInOut",
              delay: i * 0.5,
            }}
          >
            {i % 3 === 0 ? '💳' : i % 3 === 1 ? '💰' : '📱'}
            <span className="text-4xl">{i % 3 === 0 ? '💳' : i % 3 === 1 ? '💰' : '📱'}</span>
          </motion.div>
        ))}
      </div>

      <section className="relative flex flex-col items-center justify-center text-center h-full px-4 z-10">
        {/* Logo Section with animation */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.1 }}
          className="mb-4"
        >
          <motion.div
            className="relative w-24 h-24 mx-auto mb-3"
            whileHover={{ scale: 1.05 }}
            transition={{ type: "spring", stiffness: 300 }}
          >
            <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-xl blur-lg opacity-40" />
            <div className="relative bg-white dark:bg-gray-800 rounded-xl p-4 shadow-xl flex items-center justify-center">
              {/* Razorpay Logo SVG */}
              <svg viewBox="0 0 120 40" className="w-full h-auto" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 8h8l8 16-4 8H12l-4-8V8z" fill="#3B82F6" className="fill-blue-600 dark:fill-blue-400"/>
                <path d="M16 8h8v24h-8z" fill="#6366F1" className="fill-indigo-600 dark:fill-indigo-400"/>
                <text x="32" y="26" className="fill-blue-600 dark:fill-blue-400 font-bold text-[16px]" fontFamily="Arial, sans-serif">
                  Razorpay
                </text>
              </svg>
            </div>
          </motion.div>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.3 }}
            className="text-xs text-blue-600 dark:text-blue-400 font-bold tracking-wider"
          >
            AI SDR ASSISTANT
          </motion.p>
        </motion.div>

        {/* Animated Payment Icon */}
        <RazorpayAnimatedIcon />

        {/* Main Text with stagger animation */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="max-w-2xl"
        >
          <motion.h1
            className="text-5xl md:text-6xl font-extrabold bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 bg-clip-text text-transparent mb-4"
            animate={{
              backgroundPosition: ['0% 50%', '100% 50%', '0% 50%'],
            }}
            transition={{
              duration: 5,
              repeat: Infinity,
              ease: "linear"
            }}
            style={{
              backgroundSize: '200% auto',
            }}
          >
            Meet Priya
          </motion.h1>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.5 }}
            className="text-2xl text-gray-800 dark:text-gray-200 mb-3 font-semibold"
          >
            Your AI Sales Development Representative
          </motion.p>
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
            className="text-gray-600 dark:text-gray-400 mb-8 text-lg max-w-xl mx-auto"
          >
            Experience intelligent conversations powered by advanced AI. Get instant answers about Razorpay, schedule demos, and let Priya capture your requirements seamlessly.
          </motion.p>
        </motion.div>

        {/* Features with stagger */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.7 }}
          className="grid grid-cols-3 gap-6 mb-12 max-w-2xl"
        >
          {[
            { icon: '🎤', title: 'Voice AI', desc: 'Natural conversations' },
            { icon: '⚡', title: 'Real-time', desc: 'Instant responses' },
            { icon: '📊', title: 'Smart CRM', desc: 'Auto lead capture' },
          ].map((feature, i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.8 + i * 0.1 }}
              whileHover={{ scale: 1.05, y: -5 }}
              className="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-xl border border-blue-100 dark:border-blue-900"
            >
              <motion.p
                className="text-4xl mb-2"
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity, delay: i * 0.3 }}
              >
                {feature.icon}
              </motion.p>
              <p className="text-gray-900 dark:text-gray-100 font-bold text-sm mb-1">{feature.title}</p>
              <p className="text-gray-600 dark:text-gray-400 text-xs">{feature.desc}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* CTA Button with pulse effect */}
        <motion.div
          initial={{ opacity: 0, scale: 0.9 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.5, delay: 1 }}
          className="relative"
        >
          <motion.div
            className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full blur-2xl opacity-50"
            animate={{
              scale: [1, 1.2, 1],
              opacity: [0.5, 0.8, 0.5],
            }}
            transition={{
              duration: 2,
              repeat: Infinity,
              ease: "easeInOut"
            }}
          />
          <Button
            variant="primary"
            size="lg"
            onClick={onStartCall}
            className="relative w-72 font-bold text-base py-5 bg-gradient-to-r from-blue-600 via-indigo-600 to-purple-600 hover:from-blue-700 hover:via-indigo-700 hover:to-purple-700 shadow-2xl transform transition-all hover:scale-105"
          >
            <motion.span
              animate={{ scale: [1, 1.1, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              🎤
            </motion.span>
            {' '}{startButtonText}
          </Button>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 1.2 }}
            className="text-xs text-gray-500 dark:text-gray-500 mt-3"
          >
            Click to start your AI-powered conversation
          </motion.p>
        </motion.div>
      </section>

      {/* Footer - Smaller and more subtle */}
      <div className="absolute bottom-4 left-0 flex w-full items-center justify-center px-4 z-20">
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 1.3 }}
          className="text-center"
        >
          <p className="text-gray-500 dark:text-gray-500 text-xs">
            Powered by <span className="text-blue-600 dark:text-blue-400 font-semibold">Razorpay</span> • 
            <a
              target="_blank"
              rel="noopener noreferrer"
              href="https://razorpay.com"
              className="text-blue-600 dark:text-blue-400 hover:underline ml-1"
            >
              Learn more
            </a>
          </p>
        </motion.div>
      </div>
    </div>
  );
};
